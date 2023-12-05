# Code design by Quantum Robotics, author <quantumrobotics.itesm@gmail.com
#
# Mainteiners: Eduardo Chavez <eduardochavezmartin10@gmail.com>
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
        super().__init__('simple_drive_teleop')
        # publican un mensaje y crean un publicador
        self.publisher_vel = self.create_publisher(Twist, 'cmd_vel', 10)
        self.publisher_angl = self.create_publisher(Float64, 'angle_swr', 10)
        # create_subscription manda un mensaje a otro lado 
        self.subscriber_joy = self.create_subscription(Joy,"joy", self.callbackjoy,10)
        self.subscriber_joy
        # crear suscripcion a un mensaje booleano de web interface
        self.subscriber_webInt = self.create_subscription(Bool,"SD_WI", self.callbackwi,10)
        self.subscriber_webInt
        self.angle_srw = Float64()
        self.active = True
        # el inicio de las posiciones de los botones
        self.buttons, self.axes = [0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0]
        # velocidad mínima
        self.velocity=0.33  
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
        self.active = bool(data)

    def control(self):
        if self.active:
    # botones asignados a la velicidad, baja, media y alta
        #Velocity selector
            if self.buttons[3]:
                self.velocity=1
            elif self.buttons[2] or self.buttons[1]:
                self.velocity=0.5
            elif self.buttons[0]:
                self.velocity=0.33

            # condiciones  generales del movimiento de los botones
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
                # publica los ángulos de las llantas
                self.flag+=1
                if self.flag==1:    
                    self.publisher_vel.publish(self.twist)
                    self.publisher_angl.publish(self.angle_srw)
                
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