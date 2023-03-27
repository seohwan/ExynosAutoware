#include "carla_autorunner/carla_autorunner.h"

void CarlaAutorunner::Run(){
    register_subscribers();             // Register subscribers that shoud check can go next or not
    ros_autorunner_.init(nh_, sub_v_);   // Initialize the ROS-Autorunner
    ros::Rate rate(1);                  // Rate can be changed
    while(ros::ok()){               
        if(!ros_autorunner_.Run()) break;           // Run Autorunner
        ros::spinOnce();
        geometry_msgs::PoseStamped goal_msg;
        goal_msg.header.stamp = ros::Time::now();
        goal_msg.header.frame_id = "world";
        goal_msg.pose.position.x = 302.250;
        goal_msg.pose.position.y = 118.089;
        goal_msg.pose.position.z = 0.0;
        goal_msg.pose.orientation.x = 0.0;
        goal_msg.pose.orientation.y = 0.0;
        goal_msg.pose.orientation.z = -0.015;
        goal_msg.pose.orientation.w = 1.000;

        rate.sleep();
    }    
}

void CarlaAutorunner::register_subscribers(){
    int total_step_num = nh_.param("/total_step_num", -1);
    if(total_step_num < 0){
        std::cout<<"Parameter total_step_num is invalid"<<std::endl;
        exit(1);
    }    
    sub_v_.resize(total_step_num);          // Resizing the subscriber vectors. Its size must be same with number of steps

    // Set the check function(subscriber)
    sub_v_[STEP(1)] = nh_.subscribe("/points_raw", 1, &CarlaAutorunner::points_raw_cb, this);   
    sub_v_[STEP(2)] = nh_.subscribe("/ndt_pose", 1, &CarlaAutorunner::ndt_pose_cb, this);   
    sub_v_[STEP(3)] = nh_.subscribe("/behavior_state", 1, &CarlaAutorunner::behavior_state_cb, this); 

    initial_pose_pub_ = nh_.advertise< geometry_msgs::PoseWithCovarianceStamped>("initialpose", 1);
    goal_pub_ = nh_.advertise<geometry_msgs::PoseStamped>("/move_base_simple/goal", 1);
}

 void CarlaAutorunner::points_raw_cb(const sensor_msgs::PointCloud2& msg){
    if(!msg.fields.empty() && !ros_autorunner_.step_info_list_[STEP(2)].is_prepared){
        ROS_WARN("[STEP 1] Map and Sensors are prepared");
    	sleep(SLEEP_PERIOD);
        ros_autorunner_.step_info_list_[STEP(2)].is_prepared = true;
    }
 }

 void CarlaAutorunner::ndt_pose_cb(const geometry_msgs::PoseStamped& msg){
    static int failure_cnt = 0, success_cnt = 0;
    failure_cnt++;
    
    static const double pos_x = 314.072479248;
    static const double pos_y = 129.654495239;
    static const double pos_z = 0.044597864151;

    static const double ori_x = 0.0;
    static const double ori_y = 0.0;
    static const double ori_z = 0.70715665039;
    static const double ori_w = 0.70705690407;


    if(failure_cnt > 10){        
        std::cout<<"# Refresh inital pose"<<std::endl;
        std::cout<<msg.pose.position.x - pos_x <<" "<<msg.pose.position.y - pos_y <<" "
                 <<msg.pose.orientation.x - ori_x<<" "<<msg.pose.orientation.y - ori_y<<" "
                 <<msg.pose.orientation.z - ori_z<<" "<<msg.pose.orientation.w - ori_w<<" "<<std::endl;
        
        geometry_msgs::PoseWithCovarianceStamped initial_pose_msg;
        initial_pose_msg.header = msg.header;
        initial_pose_msg.pose.pose.position.x = pos_x;
        initial_pose_msg.pose.pose.position.y = pos_y;
        initial_pose_msg.pose.pose.position.z = pos_z;
        initial_pose_msg.pose.pose.orientation.x = ori_x;
        initial_pose_msg.pose.pose.orientation.y = ori_y;
        initial_pose_msg.pose.pose.orientation.z = ori_z;
        initial_pose_msg.pose.pose.orientation.w = ori_w;
        initial_pose_pub_.publish(initial_pose_msg);
        failure_cnt = 0;          
    }

    if( msg.pose.position.x <= pos_x + 1.5 && msg.pose.position.x >= pos_x - 1.5 &&        
        msg.pose.position.y <= pos_y + 1.5 && msg.pose.position.y >= pos_y - 1.5 &&
        msg.pose.orientation.x <= ori_x + 0.01 && msg.pose.orientation.x >= ori_x - 0.01 &&
        msg.pose.orientation.y <= ori_y + 0.01 && msg.pose.orientation.y >= ori_y - 0.01 &&
        msg.pose.orientation.z <= ori_z + 0.01 && msg.pose.orientation.z >= ori_z - 0.01 &&
        msg.pose.orientation.w <= ori_w + 0.01 && msg.pose.orientation.w >= ori_w - 0.01 &&
        !ros_autorunner_.step_info_list_[STEP(3)].is_prepared){
        success_cnt++;
        if(success_cnt < 3) return;
        ROS_WARN("[STEP 2] Localization is success");
    	sleep(SLEEP_PERIOD);
        ros_autorunner_.step_info_list_[STEP(3)].is_prepared = true;
    }
    else{
        success_cnt = 0;
    }
 }


 void CarlaAutorunner::behavior_state_cb(const visualization_msgs::MarkerArray& msg){
    std::string state = msg.markers.front().text;    
    if(!msg.markers.empty() && state.find(std::string("Forward"))!=std::string::npos){
        ROS_WARN("[STEP 3] Global & local planning success");
        ros_autorunner_.step_info_list_[STEP(4)].is_prepared = true;
    }
}



