import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/penguin/school/robot/NN-ROS2/install/nn_controller'
