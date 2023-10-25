# Code design by Quantum Robotics, author <quantumrobotics.itesm@gmail.com
#
# Mainteiners: Eduardo Chavez <eduardochavezmartin10@gmail.com>
#              Cesar FLores <A01751101@tec.mx>

import rclpy
import math
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
        self.publisher_angl = self.create_publisher(Float64, 'angle_swr', 10)
        self.subscriber_joy = self.create_subscription(Joy,"joy", self.callbackjoy,10)
        self.subscriber_joy
        self.angle_srw = Float64()
        self.buttons, self.axes = [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0]
        self.velocity=0.33  
        self.twist=Twist()
        self.timer = self.create_timer(0.05, self.control)
        self.anglesRad = 0.0
        self.flag=0

    def callbackjoy(self,data):
        self.buttons = list(data.buttons [:])
        self.axes = list(data.axes [:])

    def control(self):
    
        #Velocity selector
        if self.buttons[3]:
            self.velocity=1
        elif self.buttons[2] or self.buttons[1]:
            self.velocity=0.5
        elif self.buttons[0]:
            self.velocity=0.33
        
        if self.axes[1]!= 0 and abs(self.axes[0]) <=0.2 and self.axes[3] == 0 and self.axes[4] == 0:
            self.twist.linear.x=self.axes[1]*self.velocity
            self.twist.linear.y= 0.0  
            self.twist.angular.z= 0.0
            self.angle_srw.data = 0.0
            self.publisher_vel.publish(self.twist)
            self.publisher_angl.publish(self.angle_srw)
            self.flag=0


        elif self.axes[0] !=0 and abs(self.axes[1]) <=0.2:
            self.twist.angular.z=self.axes[0]*self.velocity
            self.twist.linear.y= 0.0 
            self.twist.linear.x= 0.0  
            self.angle_srw.data = 0.0
            self.publisher_vel.publish(self.twist)
            self.publisher_angl.publish(self.angle_srw)
            self.flag=0

        #elif 1 Xime
        elif self.axes[6] !=0 and self.axes[0] ==0 and self.axes[1] == 0:

            self.twist.linear.y=self.axes[6]*self.velocity
            self.twist.linear.x= 0.0
            self.twist.angular.z= 0.0 
            self.angle_srw.data = 0.0
            self.publisher_vel.publish(self.twist)
            self.publisher_angl.publish(self.angle_srw)
            self.flag=0

        elif (self.axes[3] !=0 or self.axes[4] != 0) and self.axes[0] == 0 and self.axes[6] == 0 and self.axes[7] == 0:
            self.twist.linear.x=self.axes[1]*self.velocity
            self.anglesRad = math.degrees(np.arctan2(self.axes[3],self.axes[4]))# +2*math.pi)%2*math.pi
            if(self.anglesRad>= -90 and self.anglesRad<= 90):
                self.angle_srw.data = self.anglesRad
            elif(self.anglesRad >90):
                self.angle_srw.data = 90.0
            else: #elif(self.anglesRad < 90):
                self.angle_srw.data = -90.0
            self.publisher_vel.publish(self.twist)
            self.publisher_angl.publish(self.angle_srw)
            self.flag=0

        
        else:
            self.twist.linear.x=0.0
            self.twist.linear.y=0.0
            self.twist.angular.z=0.0
            self.angle_srw.data = 0.0
            self.flag+=1
            if self.flag==1:
                self.publisher_vel.publish(self.twist)
                self.publisher_angl.publish(self.angle_srw)
            

def main(args=None):
    rclpy.init(args=args)
    listener=Simple_Drive()
    rclpy.spin(listener)
    listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()