#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.bridge = CvBridge()

        # Subscribe to camera images
        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        # Publish target centroid
        self.pub = self.create_publisher(Point, '/target/center', 10)

        # HSV range for your chosen color (example: blue)
        self.lower_hsv = np.array([100, 150, 50])
        self.upper_hsv = np.array([130, 255, 255])

    def image_callback(self, msg):
        # Convert ROS Image -> OpenCV
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Convert BGR -> HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create binary mask for target color
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)

        # Find contours and compute centroid
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        point = Point()
        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M['m00'] > 0:
                point.x = float(M['m10'] / M['m00'])  # centroid x
                point.y = float(M['m01'] / M['m00'])  # centroid y
                point.z = 1.0  # flag: target found
            else:
                point.z = 0.0  # no target
        else:
            point.z = 0.0  # no target

        self.pub.publish(point)


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()