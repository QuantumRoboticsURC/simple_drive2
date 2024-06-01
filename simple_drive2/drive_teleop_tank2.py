# Code design by Quantum Robotics, author <quantumrobotics.itesm@gmail.com
#
# Mainteiners: Santiago Chevez  <A01749887@tec.mx>
#              Cesar FLores <A01751101@tec.mx>

# importando librerías
import rclpy #importa la librería de Ros2
import math #importa funciones para cálculos matemáticos
from std_msgs.msg import * # importa un paquete con definiciones básicas de mensajería de Ros, el * imports todo lo que hay
from geometry_msgs.msg import Twist # importa un paquete de dimensiones, ángulos. Twist es x y z
from sensor_msgs.msg import Joy # paquete que lee el control
from numpy import* # importa librería para computo numérico
from rclpy.node import Node # importa una entidad que procesa la info de Ros2
import numpy as np # numpy se puede escribir como np

# recibe el node 
class Simple_Drive(Node):
    def __init__(self):
        # super (función de herencia, necesita de _init_  y el simple_drive_teleop para funcionar)
        super().__init__('simple_drive_teleop2')
        # publican un mensaje y crean un publicador
        self.publisher_vel = self.create_publisher(Twist, 'cmd_vel', 10)
        # create_subscription manda un mensaje a otro lado 
        self.subscriber_joy = self.create_subscription(Joy,"joy", self.callbackjoy,10)
        self.subscriber_joy
        # crear suscripcion a un mensaje booleano de web interface
        self.subscriber_webInt = self.create_subscription(Bool,"SD_WI", self.callbackwi,10)
        self.subscriber_webInt
        self.angle_srw = Float64()
        self.active = False
        # el inicio de las posiciones de los botones
        self.buttons, self.axes = [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0]
        # velocidad mínima
        self.velocity=3 
        self.twist=Twist()
        # tiempo que necesita ṕara realizarse
        self.timer = self.create_timer(0.05, self.control)
        self.anglesRad = 0.0
        self.flag=0

    def callbackjoy(self,data):
        self.buttons = list(data.buttons [:])
        self.axes = list(data.axes [:])

    # funcion para obtener valor de web interface
    def callbackwi(self,data):
        self.active = bool(data.data)
        print(self.active)

    def control(self):

# botones asignados a la velicidad, baja, media y alta
    #Velocity selector
        if self.buttons[3]:
            self.velocity=2
        elif self.buttons[2] or self.buttons[1]:
            self.velocity=3
        elif self.buttons[0]:
            self.velocity=4

        # condiciones  generales del movimiento de los botones
        if(abs(self.axes[4])>0 and abs(self.axes[1])>0):
            new_axes = max(abs(self.axes[4]),abs(self.axes[1]))
            if((self.axes[4]>0 and self.axes[1]<0)):
                left_speed= new_axes/self.velocity
                right_speed= -new_axes/self.velocity
            elif (self.axes[1]>0 and self.axes[4]<0):
                left_speed = -new_axes/self.velocity
                right_speed = new_axes/self.velocity
            else:
                if(self.axes[4]>=0 and self.axes[1]>=0):
                    sign=1
                else:
                    sign=-1
            
                left_speed= sign*new_axes/self.velocity
                right_speed= sign*new_axes/self.velocity

            linear_vel  = (left_speed + right_speed)/2 # (m/s)
            angular_vel  = (left_speed - right_speed)/2 # (rad/s)
            
            self.twist.linear.x=min(linear_vel,0.5)
            self.twist.angular.z=min(angular_vel,0.5)
        else:
            self.twist.linear.x=0.0
            self.twist.angular.z=0.0
        self.publisher_vel.publish(self.twist)
            
            
            
                    
# args debe tener cierto valor para funcionar
# este código le da instrucciones al Simple_Drive
def main(args=None):
    rclpy.init(args=args)
    listener=Simple_Drive()
    # spin es un nodo de ejecución que escucha a otro
    rclpy.spin(listener)
    listener.destroy_node()
    rclpy.shutdown()
# para que funcione :)
if __name__ == '__main__':
    main()