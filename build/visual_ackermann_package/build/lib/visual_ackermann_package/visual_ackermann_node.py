#!/usr/bin/env python3

'''
Visual Servo demonstration code 
Junaed Sattar (junaed@umn.edu)

11/18/2025
'''

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from ackermann_msgs.msg import AckermannDriveStamped
import cv2
from cv_bridge import CvBridge
import numpy as np

'''
Class to demonstrate visuall-guided control of an Ackermann-steered vehicle
'''

class VisionAckermannController(Node):
    '''
    Class constructor that initializes all necessary variables, parameters and sub/pubs
    '''
    def __init__(self):
        # initialize the node with the name
        super().__init__('visual_ackermann_package')
        # declate these four as command line parameters, but also with default values if none are given
        self.declare_parameter("image_topic", "/image_raw")
        self.declare_parameter("cmd_topic", "/cmd_ackermann")
        self.declare_parameter("max_speed", 1.0)
        self.declare_parameter("steer_gain", 0.0025)

        # assign the necessary parameter values to internal variables
        img_topic = self.get_parameter("image_topic").get_parameter_value().string_value
        cmd_topic = self.get_parameter("cmd_topic").get_parameter_value().string_value

        # create the CV to ROS bidirectional bridge, to convert CV image types to ROS Image messages, and
        # vice versa
        self.bridge = CvBridge()
        # publish commands to an Ackermann drive robot (e.g., a car-like steering wheel)
        self.cmd_pub = self.create_publisher(AckermannDriveStamped, cmd_topic, 10)
        # subscribe to an image topic that publishes Image type messages 
        self.create_subscription(Image, img_topic, self.image_callback, 10)
        # create a publisher to publish CV images to a ROS Image message topic
        self.grayimage_pub = self.create_publisher(Image, 'gray_image_raw', 1)
        # Loggers are used to print and save status messages
        self.get_logger().info(f"Vision controller started. Subscribing to {img_topic}")

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
        
        # Convert the thresholded CV image to a ROS Image format
        thresh_msg = self.bridge.cv2_to_imgmsg(thresh)
        # Publish the thresholded image 
        self.grayimage_pub.publish(thresh_msg)

        # If not enough bright pixels are detected, then there are no targets to threshold.
        if len(xs) == 0:
            self.get_logger().warn("No bright target detected")
            self.publish_drive(0.0, 0.0)
            return

        # Get the mean x axis value for the thresholded values, aka the x value of the thresholded centroid
        cx = np.mean(xs)
        # Find the image width
        img_w = frame.shape[1]
        # the error is measured in terms of how many pixels the centroid is displaced from the center
        error_x = cx - img_w / 2.0
        # Read the default streering gain for the Proportional controller
        steer_gain = self.get_parameter("steer_gain").value
        # Steering angle depends on the error and the steering gain
        steering_angle = -error_x * steer_gain
        # Speed is what we set it to be, as detault or as a parameter
        speed = self.get_parameter("max_speed").value
        # Publish the command to the Ackerann message 
        self.publish_drive(speed, steering_angle)
        # Log what we published for the record
        self.get_logger().info(f"Steering angle at {steering_angle} and speed at {speed}")

    '''
    Method that publishes an AckermannDriveStampoed message
    '''
    def publish_drive(self, speed, steering_angle):
        msg = AckermannDriveStamped()
        msg.drive.speed = float(speed)
        msg.drive.steering_angle = float(steering_angle)
        self.cmd_pub.publish(msg)
        

'''
main method that sets up ROS
'''
def main(args=None):
    # Initialize the ROS Python Client Library
    rclpy.init(args=args)
    # Create a node of the VisualAckermannController
    node = VisionAckermannController()
    # Start the ROS spinner, that runs until it receives a shutdown signal (Ctrl+C will do it too)
    rclpy.spin(node)
    # Clean up the node when we are done
    node.destroy_node()
    # Shut down the RCLPy system
    rclpy.shutdown()

if __name__ == "__main__":
    main()

