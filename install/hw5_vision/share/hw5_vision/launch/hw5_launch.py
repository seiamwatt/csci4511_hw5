#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # Video publisher node
        Node(
            package='hw5_vision',
            executable='video_publisher',
            name='video_publisher',
            output='screen',
            parameters=[{
                'video_path': '/home/eiamw001/ros_hw5/hw5_vision/video.mp4',
                'fps': 30.0,
                'loop': True,
            }],
        ),

        # Perception node
        Node(
            package='hw5_vision',
            executable='perception_node',
            name='perception_node',
            output='screen',
        ),

        # Control node
        Node(
            package='hw5_vision',
            executable='control_node',
            name='control_node',
            output='screen',
        ),

        # Turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim_node',
            output='screen',
        ),
    ])