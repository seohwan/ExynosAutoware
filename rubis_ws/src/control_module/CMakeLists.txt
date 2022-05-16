cmake_minimum_required(VERSION 2.8.3)
project(control_module)

## Compile as C++11, supported in ROS Kinetic and newer
add_compile_options(-std=c++11)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  tf
  std_msgs
  geometry_msgs
  visualization_msgs  
)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES contorl_module
  CATKIN_DEPENDS roscpp tf geometry_msgs std_msgs visualization_msgs
#  DEPENDS system_lib
)

include_directories(
# include
  ${PROJECT_SOURCE_DIR}/include/control_module
  ${catkin_INCLUDE_DIRS}
)

add_executable(twist_converter src/twist_converter.cpp)
target_link_libraries(twist_converter
   ${catkin_LIBRARIES}
)


add_executable(control_module
	include/control_module/control_module.h
        src/control_module/control_module_node.cpp
	src/control_module/control_module.cpp)
target_link_libraries(control_module
   ${catkin_LIBRARIES}
)
# add_dependencies(control_module ${catkin_EXPORTED_TARGETS} ${${my_package}_EXPORTED_TARGETS})
add_dependencies(control_module ${${my_package}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS} ${PROJECT_NAME}_gencfg)
