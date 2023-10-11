from launch import LaunchDescription
from launch_ros.actions import Node
import launch_ros.actions

def generate_launch_description():
    return LaunchDescription([
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
                'deadzone': 0.3,
                'autorepeat_rate': 20.0,
            }])
    ])