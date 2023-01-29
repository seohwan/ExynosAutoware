/*
 * Copyright 2015-2019 Autoware Foundation. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "twist_filter/twist_filter_node.h"

namespace twist_filter_node
{
TwistFilterNode::TwistFilterNode() : nh_(), private_nh_("~")
{
  // Parameters
  twist_filter::Configuration twist_filter_config;
  nh_.param("vehicle_info/wheel_base", twist_filter_config.wheel_base, 2.7);
  nh_.param("twist_filter/lateral_accel_limit", twist_filter_config.lateral_accel_limit, 5.0);
  nh_.param("twist_filter/lateral_jerk_limit", twist_filter_config.lateral_jerk_limit, 5.0);
  nh_.param("twist_filter/lowpass_gain_linear_x", twist_filter_config.lowpass_gain_linear_x, 0.0);
  nh_.param("twist_filter/lowpass_gain_angular_z", twist_filter_config.lowpass_gain_angular_z, 0.0);
  nh_.param("twist_filter/lowpass_gain_steering_angle", twist_filter_config.lowpass_gain_steering_angle, 0.0);
  nh_.param("twist_filter/max_stop_count", max_stop_count_, 30);
  nh_.param("twist_filter/instance_mode", rubis::instance_mode_, 0);
  twist_filter_ptr_ = std::make_shared<twist_filter::TwistFilter>(twist_filter_config);
  emergency_stop_ = false;
  current_stop_count_ = 0;

  // Subscribe
  if(rubis::instance_mode_) rubis_twist_sub_ = nh_.subscribe("rubis_twist_raw", 1, &TwistFilterNode::rubisTwistCmdCallback, this);
  else twist_sub_ = nh_.subscribe("twist_raw", 1, &TwistFilterNode::twistCmdCallback, this);
  ctrl_sub_ = nh_.subscribe("ctrl_raw", 1, &TwistFilterNode::ctrlCmdCallback, this);
  config_sub_ = nh_.subscribe("config/twist_filter", 10, &TwistFilterNode::configCallback, this);
  emergency_stop_sub_ = nh_.subscribe("emergency_stop", 1 ,&TwistFilterNode::emergencyStopCallback, this);

  // Publish
  twist_pub_ = nh_.advertise<geometry_msgs::TwistStamped>("twist_cmd", 5);
  if(rubis::instance_mode_) rubis_twist_pub_ = nh_.advertise<rubis_msgs::TwistStamped>("rubis_twist_cmd", 5);
  ctrl_pub_ = nh_.advertise<autoware_msgs::ControlCommandStamped>("ctrl_cmd", 5);
  twist_lacc_limit_debug_pub_ = private_nh_.advertise<std_msgs::Float32>("limitation_debug/twist/lateral_accel", 5);
  twist_ljerk_limit_debug_pub_ = private_nh_.advertise<std_msgs::Float32>("limitation_debug/twist/lateral_jerk", 5);
  ctrl_lacc_limit_debug_pub_ = private_nh_.advertise<std_msgs::Float32>("limitation_debug/ctrl/lateral_accel", 5);
  ctrl_ljerk_limit_debug_pub_ = private_nh_.advertise<std_msgs::Float32>("limitation_debug/ctrl/lateral_jerk", 5);
  twist_lacc_result_pub_ = private_nh_.advertise<std_msgs::Float32>("result/twist/lateral_accel", 5);
  twist_ljerk_result_pub_ = private_nh_.advertise<std_msgs::Float32>("result/twist/lateral_jerk", 5);
  ctrl_lacc_result_pub_ = private_nh_.advertise<std_msgs::Float32>("result/ctrl/lateral_accel", 5);
  ctrl_ljerk_result_pub_ = private_nh_.advertise<std_msgs::Float32>("result/ctrl/lateral_jerk", 5);

}

void TwistFilterNode::configCallback(const autoware_config_msgs::ConfigTwistFilterConstPtr& config_msg)
{
  twist_filter::Configuration twist_filter_config;
  twist_filter_config.lateral_accel_limit = config_msg->lateral_accel_limit;
  twist_filter_config.lateral_jerk_limit = config_msg->lateral_jerk_limit;
  twist_filter_config.lowpass_gain_linear_x = config_msg->lowpass_gain_linear_x;
  twist_filter_config.lowpass_gain_angular_z = config_msg->lowpass_gain_angular_z;
  twist_filter_config.lowpass_gain_steering_angle = config_msg->lowpass_gain_steering_angle;
  twist_filter_ptr_->setConfiguration(twist_filter_config);
}

inline void TwistFilterNode::publishTwist(const geometry_msgs::TwistStampedConstPtr& msg){
  const twist_filter::Twist twist = { msg->twist.linear.x, msg->twist.angular.z };
  ros::Time current_time = ros::Time::now();

  static ros::Time last_callback_time = current_time;
  static twist_filter::Twist twist_prev = twist;

  double time_elapsed = (current_time - last_callback_time).toSec();

  twist_filter::Twist twist_out = twist;

  // Apply lateral limit
  auto twist_limit_result = twist_filter_ptr_->lateralLimitTwist(twist, twist_prev, time_elapsed);
  if (twist_limit_result)
  {
    twist_out = twist_limit_result.get();
  }

  // Publish lateral accel and jerk before smoothing
  auto lacc_no_smoothed_result = twist_filter_ptr_->calcLaccWithAngularZ(twist);
  if (lacc_no_smoothed_result)
  {
    std_msgs::Float32 lacc_msg_debug;
    lacc_msg_debug.data = lacc_no_smoothed_result.get();
    twist_lacc_limit_debug_pub_.publish(lacc_msg_debug);
  }
  auto ljerk_no_smoothed_result = twist_filter_ptr_->calcLjerkWithAngularZ(twist, twist_prev, time_elapsed);
  if (ljerk_no_smoothed_result)
  {
    std_msgs::Float32 ljerk_msg_debug;
    ljerk_msg_debug.data = ljerk_no_smoothed_result.get();
    twist_ljerk_limit_debug_pub_.publish(ljerk_msg_debug);
  }

  // Smoothing
  twist_out = twist_filter_ptr_->smoothTwist(twist_out);

  // Smoothed value publish
  geometry_msgs::TwistStamped out_msg = *msg;
  if(emergency_stop_ == false){
    out_msg.twist.linear.x = twist_out.lx;
    out_msg.twist.angular.z = twist_out.az;
  }
  else{
    out_msg.twist.linear.x = -1000;
    out_msg.twist.angular.z = 0;
  }
  twist_pub_.publish(out_msg);
  if(rubis::instance_mode_ && rubis::instance_ != RUBIS_NO_INSTANCE){
    rubis_msgs::TwistStamped rubis_out_msg;
    rubis_out_msg.instance = rubis::instance_;
    rubis_out_msg.obj_instance = rubis::obj_instance_;
    rubis_out_msg.msg = out_msg;
    rubis_twist_pub_.publish(rubis_out_msg);
  }

  if(rubis::sched::is_task_ready_ == TASK_NOT_READY) rubis::sched::init_task();
  rubis::sched::task_state_ = TASK_STATE_DONE;

  // Publish lateral accel and jerk after smoothing
  auto lacc_smoothed_result = twist_filter_ptr_->calcLaccWithAngularZ(twist_out);
  if (lacc_smoothed_result)
  {
    std_msgs::Float32 lacc_msg;
    lacc_msg.data = lacc_smoothed_result.get();
    twist_lacc_result_pub_.publish(lacc_msg);
  }
  auto ljerk_smoothed_result = twist_filter_ptr_->calcLjerkWithAngularZ(twist_out, twist_prev, time_elapsed);
  if (ljerk_smoothed_result)
  {
    std_msgs::Float32 ljerk_msg;
    ljerk_msg.data = ljerk_smoothed_result.get();
    twist_ljerk_result_pub_.publish(ljerk_msg);
  }

  // Preserve value and time
  twist_prev = twist_out;
  last_callback_time = current_time;
}

void TwistFilterNode::rubisTwistCmdCallback(const rubis_msgs::TwistStampedConstPtr& _msg){
  // Before spin
  if(task_profiling_flag) rubis::sched::start_task_profiling();

  // Callback
  _emergencyStopCallback();
  _ctrlCmdCallback(ctrl_cmd_ptr_);

  geometry_msgs::TwistStampedConstPtr msg = boost::make_shared<const geometry_msgs::TwistStamped>(_msg-> msg);
  rubis::instance_ = _msg->instance;
  rubis::obj_instance_ = _msg->obj_instance;
  publishTwist(msg);

  // After spin
  if(task_profiling_flag) rubis::sched::stop_task_profiling(rubis::instance_, rubis::sched::task_state_);
}


void TwistFilterNode::twistCmdCallback(const geometry_msgs::TwistStampedConstPtr& msg)
{
  rubis::instance_ = RUBIS_NO_INSTANCE;
  publishTwist(msg);
}

void TwistFilterNode::ctrlCmdCallback(const autoware_msgs::ControlCommandStampedConstPtr& msg)
{
  ctrl_cmd_ptr_ = boost::make_shared<autoware_msgs::ControlCommandStamped const>(*msg);
}

void TwistFilterNode::_ctrlCmdCallback(const autoware_msgs::ControlCommandStampedConstPtr& msg)
{
  if(ctrl_cmd_ptr_ == NULL) return;
  const twist_filter::Ctrl ctrl = { msg->cmd.linear_velocity, msg->cmd.steering_angle };
  ros::Time current_time = ros::Time::now();

  static ros::Time last_callback_time = current_time;
  static twist_filter::Ctrl ctrl_prev = ctrl;

  double time_elapsed = (current_time - last_callback_time).toSec();

  checkCtrl(ctrl, ctrl_prev, time_elapsed);

  twist_filter::Ctrl ctrl_out = ctrl;

  // Apply lateral limit
  auto ctrl_limit_result = twist_filter_ptr_->lateralLimitCtrl(ctrl, ctrl_prev, time_elapsed);
  if (ctrl_limit_result)
  {
    ctrl_out = ctrl_limit_result.get();
  }

  // Publish lateral accel and jerk before smoothing
  auto lacc_no_smoothed_result = twist_filter_ptr_->calcLaccWithSteeringAngle(ctrl);
  if (lacc_no_smoothed_result)
  {
    std_msgs::Float32 lacc_msg_debug;
    lacc_msg_debug.data = lacc_no_smoothed_result.get();
    ctrl_lacc_limit_debug_pub_.publish(lacc_msg_debug);
  }
  auto ljerk_no_smoothed_result = twist_filter_ptr_->calcLjerkWithSteeringAngle(ctrl, ctrl_prev, time_elapsed);
  if (ljerk_no_smoothed_result)
  {
    std_msgs::Float32 ljerk_msg_debug;
    ljerk_msg_debug.data = ljerk_no_smoothed_result.get();
    ctrl_ljerk_limit_debug_pub_.publish(ljerk_msg_debug);
  }

  // Smoothing
  ctrl_out = twist_filter_ptr_->smoothCtrl(ctrl_out);

  // Smoothed value publish
  autoware_msgs::ControlCommandStamped out_msg = *msg;
  out_msg.cmd.linear_velocity = ctrl_out.lv;
  out_msg.cmd.steering_angle = ctrl_out.sa;

  if(emergency_stop_) out_msg.cmd.linear_velocity = -1000;

  ctrl_pub_.publish(out_msg);

  // Publish lateral accel and jerk after smoothing
  auto lacc_smoothed_result = twist_filter_ptr_->calcLaccWithSteeringAngle(ctrl_out);
  if (lacc_smoothed_result)
  {
    std_msgs::Float32 lacc_msg;
    lacc_msg.data = lacc_smoothed_result.get();
    ctrl_lacc_result_pub_.publish(lacc_msg);
  }
  auto ljerk_smoothed_result = twist_filter_ptr_->calcLjerkWithSteeringAngle(ctrl_out, ctrl_prev, time_elapsed);
  if (ljerk_smoothed_result)
  {
    std_msgs::Float32 ljerk_msg;
    ljerk_msg.data = ljerk_smoothed_result.get();
    ctrl_ljerk_result_pub_.publish(ljerk_msg);
  }

  // Preserve value and time
  ctrl_prev = ctrl_out;
  last_callback_time = current_time;
}

void TwistFilterNode::emergencyStopCallback(const std_msgs::Bool& msg){
  current_emergency_stop_ = msg.data;
  return;
}

void TwistFilterNode::_emergencyStopCallback(){
  static std::string state("none");
  
  if(current_emergency_stop_ == true){
    state = std::string("object is detected");
    emergency_stop_ = true;
    current_stop_count_ = max_stop_count_;
  }
  else if(current_emergency_stop_ == false && emergency_stop_ == true){ // Emergency Stop event is finished or wait
    current_stop_count_--;
    if(current_stop_count_ > 0){
      state = std::string("Wait for go");
      emergency_stop_ = true;
    }
    else
      emergency_stop_ = false;
  }
  else if(current_emergency_stop_ == false && emergency_stop_ == false){ // No event
    state = std::string("No object");
    emergency_stop_ = false;
    current_stop_count_ = 0;
  }
}

void TwistFilterNode::checkTwist(const twist_filter::Twist twist, const twist_filter::Twist twist_prev,
                                 const double& dt)
{
  const auto lacc = twist_filter_ptr_->calcLaccWithAngularZ(twist);
  const auto ljerk = twist_filter_ptr_->calcLjerkWithAngularZ(twist, twist_prev, dt);

  const twist_filter::Configuration& config = twist_filter_ptr_->getConfiguration();

}

void TwistFilterNode::checkCtrl(const twist_filter::Ctrl ctrl, const twist_filter::Ctrl ctrl_prev, const double& dt)
{
  const auto lacc = twist_filter_ptr_->calcLaccWithSteeringAngle(ctrl);
  const auto ljerk = twist_filter_ptr_->calcLjerkWithSteeringAngle(ctrl, ctrl_prev, dt);

  const twist_filter::Configuration& config = twist_filter_ptr_->getConfiguration();

}

}  // namespace twist_filter_node
