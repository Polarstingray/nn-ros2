from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # TURTLEBOT3_MODEL must be set in the shell before launching because
    # spawn_turtlebot3.launch.py reads os.environ at parse time, before
    # SetEnvironmentVariable actions execute.
    import os as _os
    _os.environ.setdefault('TURTLEBOT3_MODEL', 'waffle_pi')

    gz_ip = SetEnvironmentVariable(name='GZ_IP', value='127.0.0.1')
    bot = SetEnvironmentVariable(name='TURTLEBOT3_MODEL', value='waffle_pi')

    # Derive workspace root from the installed package share directory
    ws_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        get_package_share_directory('nn_controller')
    ))))
    # ws_root is the colcon workspace root; sources and venv live inside NN-ROS2/
    repo_root = os.path.join(ws_root, 'NN-ROS2')

    model_path_arg = DeclareLaunchArgument(
        'model_path',
        default_value=os.path.join(
            repo_root, 'src', 'nn_controller', 'resource', 'resnet50_model.pth'),
        description='Absolute path to the trained resnet50_model.pth weights file'
    )

    # prepend venv instead of replacing with PYTHONPATH
    venv_site = os.path.join(repo_root, 'torch_venv', 'lib', 'python3.12', 'site-packages')
    pythonpath = SetEnvironmentVariable(
        name='PYTHONPATH',
        value=[venv_site, ':', EnvironmentVariable('PYTHONPATH', default_value='')]
    )

    # Launch Gazebo + TurtleBot3 Waffle Pi
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('turtlebot3_gazebo'),
            '/launch/turtlebot3_world.launch.py'
        ])
    )

    # delay starting the NN control to give gz time to load and publish camera topics
    nn_node = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='nn_controller',
                executable='nn_controller_node',
                name='nn_controller_node',
                output='screen',
                parameters=[{'model_path': LaunchConfiguration('model_path')}],
            )
        ]
    )

    return LaunchDescription([model_path_arg, gz_ip, bot, pythonpath, gazebo_launch, nn_node])
