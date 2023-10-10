import rclpy
from math import *
from std_msgs.msg import *
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from numpy import*
from rclpy.node import Node
import numpy as np

class Simple_Drive(Node):
    def __init__(self):
        super().__init__('simple_drive_teleop')
        
        self.publisher_vel = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer=self.create_timer(0.05,self.control)
        self.subscriber_joy = self.create_subscription(Joy,"joy", self.callbackjoy,10)


        self.buttons, self.axes = [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0]
        self.velocity=0.33
        self.twist=Twist()
        self.deathZone = 0.3


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

    def control(self):
        def calcVel(joyIn):
            return (1.29*joyIn)-0.29
        
        if self.buttons[3]:
            self.velocity=1
        elif self.buttons[2] or self.buttons[1]:
            self.velocity=0.5
        elif self.buttons[0]:
            self.velocity=0.33
        
        elif self.axes[1]>=self.deathZone or self.axes[1]<=-self.deathZone:
            self.twist.linear.x=calcVel(self.axes[1])*self.velocity
            #print(self.twist)
        
        elif self.axes[0]>=self.deathZone or self.axes[0]<=-self.deathZone:
            self.twist.angular.z=calcVel(self.axes[0])*self.velocity
        
        else:
            self.twist.linear.x=0.0
            self.twist.angular.z=0.0
        
        self.publisher_vel.publish(self.twist)
        print("Twist publicado")
            

def main(args=None):
    rclpy.init(args=args)
    listener=Simple_Drive()
    rclpy.spin(listener)
    listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()