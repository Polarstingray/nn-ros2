import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import TwistStamped
from cv_bridge import CvBridge
import cv2
import csv
import os


class DataCollectorNode(Node):
    def __init__(self):
        super().__init__('data_collector')

        self.declare_parameter('output_dir', os.path.expanduser('~/nn_data'))
        self.output_dir = self.get_parameter('output_dir').get_parameter_value().string_value
        os.makedirs(self.output_dir, exist_ok=True)

        self.bridge = CvBridge()
        # Resume count from existing images so filenames never collide across sessions
        self.frame_count = len([f for f in os.listdir(self.output_dir) if f.endswith('.png')])
        self.latest_cmd_vel = None

        # open CSV for labels
        csv_path = os.path.join(self.output_dir, 'labels.csv')
        self.csv_file = open(csv_path, 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        if os.path.getsize(csv_path) == 0:
            self.csv_writer.writerow(['filename', 'linear_x', 'angular_z'])

        # subscribe to cmd_vel to get the latest velocity command for labeling
        self.create_subscription(TwistStamped, '/cmd_vel', self.cmd_vel_callback, 10)

        # camera: save a frame on every image, paired with the cached cmd_vel
        self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.get_logger().info(f'Data collector started. Saving to: {self.output_dir}')


    def cmd_vel_callback(self, msg):
        self.latest_cmd_vel = msg

    def image_callback(self, msg):
        if self.latest_cmd_vel is None:
            return # skip until initial movement

        linear_x  = self.latest_cmd_vel.twist.linear.x
        angular_z = self.latest_cmd_vel.twist.angular.z

        # skip stationary frames
        if abs(linear_x) < 0.01 and abs(angular_z) < 0.01:
            return

        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        filename = f'{self.frame_count:06d}.png'
        cv2.imwrite(os.path.join(self.output_dir, filename), cv_image)
        self.csv_writer.writerow([filename, linear_x, angular_z])
        self.csv_file.flush()
        self.frame_count += 1

        if self.frame_count % 100 == 0:
            self.get_logger().info(f'Collected {self.frame_count} frames')

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DataCollectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
