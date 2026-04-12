import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
from ament_index_python.packages import get_package_share_directory
import os

class NNController(Node):
    def __init__(self):
        super().__init__('nn_controller')

        # Load the custom ResNet model
        pkg_share = get_package_share_directory('nn_controller')
        model_path = os.path.join(pkg_share, 'resource', 'resnet50_model.pth')
        
        self.resnet50 = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
        self.model = self.resnet50
        self.num_features = self.resnet50.fc.in_features # 2048
        self.resnet50.fc = nn.Linear(self.num_features, 2) # 2
        
        self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
        self.model.eval()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        # Preprocessing (should match our training pipeline)
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                 std=[0.25, 0.25, 0.25]),
        ])

        self.bridge = CvBridge()

        # Subscriptions & Publishers
        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info('NN Controller node started - waiting for camera images')

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

            # Preprocess
            input_tensor = self.transform(rgb_image).unsqueeze(0).to(self.device)

            # Inference
            with torch.no_grad():
                output = self.model(input_tensor)          # shape: [vel, ang] expected

            # Extract velocities (adapt indexing as model probably outputs differently)
            linear_x = float(output[0][0].item())
            angular_z = float(output[0][1].item())

            # Publish command
            twist = Twist()
            twist.linear.x = linear_x
            twist.angular.z = angular_z
            self.pub.publish(twist)

            self.get_logger().debug(f'Published vel: linear={linear_x:.2f}, angular={angular_z:.2f}')

        except Exception as e:
            self.get_logger().error(f'Error in callback: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = NNController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
