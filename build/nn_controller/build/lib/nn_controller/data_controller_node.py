import rclpy                                                                  
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import message_filters                                                        
import cv2
import csv                                                                    
import os       
import time


class DataCollectorNode(Node):
    def __init__(self):
        super().__init__('data_collector')
                                                                            
        self.declare_parameter('output_dir', os.path.expanduser('~/nn_data'))
        self.output_dir = self.get_parameter('output_dir').get_parameter_value().string_valueos.makedirs(self.output_dir, exist_ok=True)
                                                                            
        self.bridge = CvBridge()
        self.frame_count = 0
                                                                            
        # Open CSV for labels
        csv_path = os.path.join(self.output_dir, 'labels.csv')                
        self.csv_file = open(csv_path, 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)                           
        # Write header only if file is new/empty
        if os.path.getsize(csv_path) == 0:                                    
            self.csv_writer.writerow(['filename', 'linear_x', 'angular_z'])
                                                                            
        # Synchronized subscribers
        image_sub = message_filters.Subscriber(self, Image, '/camera/image_raw')                                                          
        cmd_sub   = message_filters.Subscriber(self, Twist, '/cmd_vel')
        self.sync = message_filters.ApproximateTimeSynchronizer(              
            [image_sub, cmd_sub], queue_size=10, slop=0.1)
        self.sync.registerCallback(self.synchronized_callback)                
                
        self.get_logger().info(f'Data collector started. Saving to: {self.output_dir}')

    def synchronized_callback(self, img_msg, twist_msg):                      
        linear_x  = twist_msg.linear.x
        angular_z = twist_msg.angular.z                                       
                                                                            
        # Skip frames where the robot is stationary — they add noise          
        if abs(linear_x) < 0.01 and abs(angular_z) < 0.01:                    
            return                                                            
                
        cv_image = self.bridge.imgmsg_to_cv2(img_msg, desired_encoding='bgr8')
        filename = f'{self.frame_count:06d}.png'
        cv2.imwrite(os.path.join(self.output_dir, filename), cv_image)        
        self.csv_writer.writerow([filename, linear_x, angular_z])             
        self.csv_file.flush()  # don't lose data if killed mid-session
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