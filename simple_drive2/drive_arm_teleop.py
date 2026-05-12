import rclpy
import math
from std_msgs.msg import Float64, String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from rclpy.node import Node


def my_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class ArmTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop_joy')

        # Parameters
        self.declare_parameter('linear_velocity', 0.08)
        self.declare_parameter('angular_velocity', 0.5)
        self.declare_parameter('deadzone', 0.05)
        self.declare_parameter('rate', 10.0)

        self.linear_vel = self.get_parameter('linear_velocity').get_parameter_value().double_value
        self.angular_vel = self.get_parameter('angular_velocity').get_parameter_value().double_value
        self.deadzone = self.get_parameter('deadzone').get_parameter_value().double_value
        rate = self.get_parameter('rate').get_parameter_value().double_value

        # Publishers — aligned with arm_mode_manager topics
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel/arm', 10)
        self.pub_jog_mode = self.create_publisher(String, '/arm_jog/mode', 10)
        self.pub_camera_servo = self.create_publisher(Float64, '/arm_teleop/camera_servo', 10)
        self.pub_gripper = self.create_publisher(Float64, '/arm_teleop/gripper', 10)
        self.pub_linear_actuator = self.create_publisher(Float64, '/arm_teleop/linear_actuator', 10)

        # Subscribers
        self.create_subscription(Joy, 'joy', self.cb_joy, 10)
        self.create_subscription(String, '/arm_mode/current', self.cb_mode, 10)
        self.create_subscription(String, '/arm_jog/mode/current', self.cb_jog_mode, 10)

        # State
        self.buttons = [0] * 16
        self.axes = [0.0] * 8
        self.current_mode = 'idle'
        self.current_jog_mode = 'cartesian'

        # Control loop
        self.create_timer(1.0 / rate, self.control_loop)

        self.get_logger().info('Arm teleop ready')

    def cb_joy(self, msg: Joy):
        self.buttons = list(msg.buttons)
        self.axes = list(msg.axes)

    def cb_mode(self, msg: String):
        self.current_mode = msg.data

    def cb_jog_mode(self, msg: String):
        self.current_jog_mode = msg.data

    def _apply_deadzone(self, value: float) -> float:
        return value if abs(value) > self.deadzone else 0.0

    def control_loop(self):
        twist = Twist()

        # ---------------------------------------------------------------
        # Joystick axes → arm velocity
        # axes[1] = left stick Y (forward/back)
        # axes[0] = left stick X (left/right)
        # buttons[0] = A → enable Z mode (stick Y controls Z instead of X)
        # ---------------------------------------------------------------
        stick_x = self._apply_deadzone(self.axes[1]) if len(self.axes) > 1 else 0.0
        stick_y = self._apply_deadzone(self.axes[0]) if len(self.axes) > 0 else 0.0
        enable_z = self.buttons[0] if len(self.buttons) > 0 else 0

        if enable_z:
            twist.linear.z = stick_x * self.linear_vel
            twist.linear.x = 0.0
        else:
            twist.linear.x = stick_x * self.linear_vel
            twist.linear.z = 0.0
        twist.linear.y = stick_y * self.linear_vel

        # ---------------------------------------------------------------
        # Roll / Pitch — buttons 7-10
        # buttons[7]  → roll +
        # buttons[8]  → roll -
        # buttons[9]  → pitch +
        # buttons[10] → pitch -
        # ---------------------------------------------------------------
        if len(self.buttons) > 10:
            if self.buttons[5]:
                twist.angular.x = self.angular_vel
            elif self.buttons[6]:
                twist.angular.x = -self.angular_vel
            else:
                twist.angular.x = 0.0

            if self.buttons[10]:
                twist.angular.y = self.angular_vel
            elif self.buttons[9]:
                twist.angular.y = -self.angular_vel
            else:
                twist.angular.y = 0.0

        self.pub_vel.publish(twist)

        # ---------------------------------------------------------------
        # Camera servo — right stick Y (axes[3])
        # ---------------------------------------------------------------
        if len(self.axes) > 2:
            cam_msg = Float64()
            cam_msg.data = my_map(self.axes[2], -1.0, 1.0, -90.0, 90.0)
            self.pub_camera_servo.publish(cam_msg)

        # ---------------------------------------------------------------
        # Jog mode switch
        # buttons[1] (B) → cartesian
        # buttons[2] (X) → relative
        # ---------------------------------------------------------------
        if len(self.buttons) > 2:
            if self.buttons[1]:
                mode_msg = String()
                mode_msg.data = 'cartesian'
                self.pub_jog_mode.publish(mode_msg)
            elif self.buttons[2]:
                mode_msg = String()
                mode_msg.data = 'relative'
                self.pub_jog_mode.publish(mode_msg)

        # ---------------------------------------------------------------
        # Gripper — buttons[3] open, buttons[4] close
        # ---------------------------------------------------------------
        grip_msg = Float64()
        if len(self.buttons) > 4:
            if self.buttons[3]:
                grip_msg.data = 1.0
            elif self.buttons[4]:
                grip_msg.data = -1.0
            else:
                grip_msg.data = 0.0
        self.pub_gripper.publish(grip_msg)

        # ---------------------------------------------------------------
        # Linear actuator — buttons[5] extend, buttons[6] retract
        # ---------------------------------------------------------------
        la_msg = Float64()
        if len(self.buttons) > 6:
            if self.buttons[7]:
                la_msg.data = 1.0
            elif self.buttons[8]:
                la_msg.data = -1.0
            else:
                la_msg.data = 0.0
        self.pub_linear_actuator.publish(la_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ArmTeleop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()