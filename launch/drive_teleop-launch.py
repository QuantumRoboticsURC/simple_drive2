from launch import LaunchDescription
from launch_ros.actions import Node
import launch_ros.actions
import launch


def generate_launch_description():
    joy_dev = launch.substitutions.LaunchConfiguration('joy_dev')

    return LaunchDescription([
        launch.actions.DeclareLaunchArgument('joy_dev', default_value='/dev/input/js0'),
        Node(
            package='simple_drive2',
            executable='simple_drive_teleop',
            name='simple_drive_teleop'
        ),

        launch_ros.actions.Node(
            package='joy', 
            executable='joy_node',
            name='joy_node',
            parameters=[{
                'dev': joy_dev,
                'deadzone': 0.3,
                'autorepeat_rate': 20.0,
            }])
    ])