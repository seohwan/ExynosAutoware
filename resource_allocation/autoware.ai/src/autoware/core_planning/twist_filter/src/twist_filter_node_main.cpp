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

extern unsigned long rubis::instance_;
extern 

int main(int argc, char** argv)
{
  ros::init(argc, argv, "twist_filter");
  twist_filter_node::TwistFilterNode node;

  ros::NodeHandle private_nh("~");

  // Scheduling & Profiling Setup
  std::string node_name = ros::this_node::getName();
  std::string task_response_time_filename;
  private_nh.param<std::string>(node_name+"/task_response_time_filename", task_response_time_filename, "~/Documents/profiling/response_time/twist_filter.csv");

  int rate;
  private_nh.param<int>(node_name+"/rate", rate, 10);

  struct rubis::sched_attr attr;
  std::string policy;
  int priority, exec_time ,deadline, period;
    
  private_nh.param(node_name+"/task_scheduling_configs/policy", policy, std::string("NONE"));    
  private_nh.param(node_name+"/task_scheduling_configs/priority", priority, 99);
  private_nh.param(node_name+"/task_scheduling_configs/exec_time", exec_time, 0);
  private_nh.param(node_name+"/task_scheduling_configs/deadline", deadline, 0);
  private_nh.param(node_name+"/task_scheduling_configs/period", period, 0);
  attr = rubis::create_sched_attr(priority, exec_time, deadline, period);    
  rubis::init_task_scheduling(policy, attr);

  std::string cpuset, cache_allocation;

  private_nh.param(node_name+"/task_resource_configs/cpuset", cpuset, std::string("-1"));
  private_nh.param(node_name+"/task_resource_configs/cache_allocation", cache_allocation, std::string("-1"));
  rubis::init_resource_cpu_allocation(cpuset);
  rubis::init_resource_cache_allocation(cache_allocation);

  rubis::init_task_profiling(task_response_time_filename);
  
  ros::spin();
  
  return 0;
}
