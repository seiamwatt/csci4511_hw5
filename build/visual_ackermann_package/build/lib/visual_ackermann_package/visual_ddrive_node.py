#!/usr/bin/env python3

'''
Visual Servo demonstration code for a differential drive robot
Junaed Sattar (junaed@umn.edu)

11/18/2025
'''

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import cv2
from cv_bridge import CvBridge
import numpy as np

'''
Class to demonstrate visuall-guided control of an Ackermann-steered vehicle
'''

class VisionDiffDriveController(Node):
    '''
    Class constructor that initializes all necessary variables, parameters and sub/pubs
    '''
    def __init__(self):
        # initialize the node with the name
        super().__init__('visual_ddrive_node')
        # declate these four as command line parameters, but also with default values if none are given
        self.declare_parameter("image_topic", "/image_raw")
        self.declare_parameter("cmd_topic", "/cmd_vel")
        self.declare_parameter("max_linear_speed", 0.5)   # m/s
        self.declare_parameter("angular_gain", 0.0025)    # rad/pixel
        self.declare_parameter("stop_if_no_target", True)

        # assign the necessary parameter values to internal variables
        img_topic = self.get_parameter("image_topic").get_parameter_value().string_value
        cmd_topic = self.get_parameter("cmd_topic").get_parameter_value().string_value

        # create the CV to ROS bidirectional bridge, to convert CV image types to ROS Image messages, and
        # vice versa
        self.bridge = CvBridge()
        # publish commands to a differential drive robot (e.g., a turtlebot)
        self.cmd_pub = self.create_publisher(Twist, cmd_topic, 10)
        # subscribe to an image topic that publishes Image type messages 
        self.create_subscription(Image, img_topic, self.image_callback, 10)
        # create a publisher to publish CV images to a ROS Image message topic
        self.grayimage_pub = self.create_publisher(Image, 'gray_image_raw', 1)
        # Loggers are used to print and save status messages
        self.get_logger().info(
            f"Vision diff-drive controller started. "
            f"Subscribing to {img_topic}, publishing Twist on {cmd_topic}"
        )

    '''
    The image message subscriber callback method
    '''
    def image_callback(self, msg):
        # Convert the ROS Image message to a CV image in bgr9 format
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        # convert this image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Commented out, for now, to stop publishing the grayscale version
#        gray_msg = self.bridge.cv2_to_imgmsg(gray)
#       self.grayimage_pub.publish(gray_msg)
        # threshold the image by suppressing any pixel with grayscale intensity less than 150
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        # get all the (y,x) coordinates of the non-suppressed pixels (that is, the white ones)
        ys, xs = np.where(thresh == 255)
        # Twist message type object to publish commands to the robot
        twist = Twist()
        # Convert the thresholded CV image to a ROS Image format
        thresh_msg = self.bridge.cv2_to_imgmsg(thresh)
        # Publish the thresholded image 
        self.grayimage_pub.publish(thresh_msg)

        # If not enough bright pixels are detected, then there are no targets to threshold.
        if len(xs) == 0:
            self.get_logger().warn("No bright target detected")

            if self.get_parameter("stop_if_no_target").value:
                # publish zero cmd_vel
                self.cmd_pub.publish(twist)
            else:
                # e.g., rotate in place slowly to search
                twist.angular.z = 0.3
                self.cmd_pub.publish(twist)
            return

        # Get the mean x axis value for the thresholded values, aka the x value of the thresholded centroid
        cx = np.mean(xs)
        # Find the image width
        img_w = frame.shape[1]
        # the error is measured in terms of how many pixels the centroid is displaced from the center
        error_x = cx - img_w / 2.0
        # Read the default angular gain for the Proportional controller
        angular_gain = self.get_parameter("angular_gain").value
        # Read the max linear speed parameter
        max_linear_speed = self.get_parameter("max_linear_speed").value

        # Angular velocity: proportional to horizontal error
        twist.angular.z = -error_x * angular_gain  # sign so left error -> +z

        # Linear velocity: simple constant (you can make it depend on error)
        twist.linear.x = max_linear_speed

        # Publish the command to the Ackerann message 
        self.cmd_pub.publish(twist)

'''
main method that sets up ROS
'''
def main(args=None):
    # Initialize the ROS Python Client Library
    rclpy.init(args=args)
    # Create a node of the VisionDiffDriveController type
    node = VisionDiffDriveController()
    # Start the ROS spinner, that runs until it receives a shutdown signal (Ctrl+C will do it too)
    rclpy.spin(node)
    # Clean up the node when we are done
    node.destroy_node()
    # Shut down the RCLPy system
    rclpy.shutdown()

if __name__ == "__main__":
    main()

