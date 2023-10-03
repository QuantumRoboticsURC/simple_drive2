import rclpy
from math import *
from std_msgs.msg import *
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from numpy import*
from rclpy.node import Node

class Simple_Drive(Node):
    def __init__(self):
        super().__init__('simple_drive_teleop')

        self.publisher_vel = self.create_publisher(String, 'cmd_vel', 10)

        self.subscriber_joy = self.create_subscription(Joy,"joy", self.callbackjoy,10)
        self.subscriber_joy


        self.buttons, self.axes = [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0]



    def callbackjoy(self,data):
        self.buttons = list(data.buttons [:])
        self.axes = list(data.axes [:])

    def my_map(self,x,in_min,in_max,out_min,out_max):
        x = int(x)
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def angulos(self,servo,data,min,max):
        grados=degrees(data)
        angulo=int(self.my_map(grados,-90,90,min,max))
        if angulo>240:
            angulo=240
        elif angulo<0:
            angulo=0
        servo.moveTimeWrite(angulo)

    

def main(args=None):
    rclpy.init(args=args)
    listener=Simple_Drive()
    rclpy.spin(listener)
    listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

