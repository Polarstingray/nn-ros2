from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    render = SetEnvironmentVariable(name='LIBGL_ALWAYS_SOFTWARE', value='1') # Fixes my vm crashes, uses software rendering
    bot = SetEnvironmentVariable(name='TURTLEBOT3_MODEL', value='burger')

    # Launch Gazebo + TurtleBot3 Burger
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('turtlebot3_gazebo'),
            '/launch/empty_world.launch.py'   # or turtlebot3_world.launch.py
        ])
    )

    # Launch nn_controller
    nn_node = Node(
        package='nn_controller',
        executable='nn_controller_node',
        name='nn_controller_node',
        output='screen',
    )

    return LaunchDescription([render, bot, gazebo_launch, nn_node])
