#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist


class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        # Subscribe to target centroid from perception node
        self.sub = self.create_subscription(
            Point, '/target/center', self.target_callback, 10)

        # Publish velocity commands to turtlesim
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Image width (must match your video)
        self.image_width = 640

        # Proportional gain for steering
        self.kp = 0.005

        # Forward speed when target is found
        self.forward_speed = 1.0

        # Search rotation speed when no target
        self.search_speed = 0.5

    def target_callback(self, msg):
        twist = Twist()

        if msg.z == 1.0:
            # Target found — compute horizontal error
            image_center = self.image_width / 2.0
            error = image_center - msg.x

            # Proportional steering
            twist.angular.z = self.kp * error

            # Drive forward
            twist.linear.x = self.forward_speed
        else:
            # No target — search by rotating in place
            twist.linear.x = 0.0
            twist.angular.z = self.search_speed

        self.pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()