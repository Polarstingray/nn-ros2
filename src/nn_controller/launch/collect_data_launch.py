from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    gz_ip = SetEnvironmentVariable(name='GZ_IP', value='127.0.0.1')  # force gz-transport over loopback
    bot   = SetEnvironmentVariable(name='TURTLEBOT3_MODEL', value='waffle_pi')

    output_dir_arg = DeclareLaunchArgument(
        'output_dir',
        default_value=os.path.expanduser('~/nn_data'),
        description='Directory to save collected images and labels.csv'
    )
                                                                            
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([                                       
            get_package_share_directory('turtlebot3_gazebo'),
            '/launch/turtlebot3_world.launch.py'  # changed from empty_world
        ])                                                                    
    )
                                                                            
    teleop = Node(
        package='turtlebot3_teleop',
        executable='teleop_keyboard',
        name='teleop_keyboard',
        output='screen',
        prefix='xterm -e',
    )                                                                         

    collector = Node(
        package='nn_controller',
        executable='data_collector_node',
        name='data_collector',
        output='screen',
        parameters=[{'output_dir': LaunchConfiguration('output_dir')}],
    )

    return LaunchDescription([output_dir_arg, gz_ip, bot, gazebo, teleop, collector])