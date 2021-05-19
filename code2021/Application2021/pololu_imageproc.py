import pyrealsense2 as rs
import numpy as np
import cv2
import math

kernel = np.ones((3,3),np.int8)

class imageproc(object):
    color_image = np.zeros((480,640,3),np.uint8)
    Init = False
    pipeline = None
    mouse_x = 0
    mouse_y = 0

    def __init__(self):
        self.cX = 0 
        self.cY = 0 
        self.Circle_x = 0 
        self.Circle_y = 0
        self.state = 1
        pass

    def init_proc(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        #config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(config)
        self.Init = True

    def get_res_image(self):
        hsv_image = cv2.cvtColor(self.color_image, cv2.COLOR_BGR2HSV)
        l_orange = np.array([0,110,114])
        h_orange = np.array([16,255,255])
        mask = cv2.inRange(hsv_image,l_orange,h_orange)
        result = cv2.bitwise_and(self.color_image,self.color_image,mask=mask)
        res_gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        ret,res_binary = cv2.threshold(res_gray,0,255,cv2.THRESH_BINARY)
        res_erode = cv2.erode(res_binary,kernel,iterations=1)
        return res_erode

    def Calcu_angle(self,dx,dy):
        if(dy != 0):
            angle = math.atan(abs(dx)/abs(dy))
            if(dx > 0 and dy < 0):
                angle = angle
            elif(dx > 0 and dy > 0):
                angle = math.pi - angle
            elif(dx < 0 and dy > 0):
                angle = math.pi + angle
            elif(dx < 0 and dy < 0):
                angle = 2*math.pi - angle
            #print(int(angle*180/math.pi))
            return int(angle*180/math.pi)
    
    def ImageCap(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        # Convert images to numpy arrays
        self.color_image = np.asanyarray(color_frame.get_data())

    '''
    calcule les valeurs de base
    retourne la position de robot et la position de circle.
    '''
    # faut appller le init_proc() tout d'abord.
    def ImageProc(self):

        res_erode = self.get_res_image()

        circles = cv2.HoughCircles(res_erode,cv2.HOUGH_GRADIENT,1,20,
                            param1=100,param2=19,minRadius=0,maxRadius=100)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # draw the outer circle
                cv2.circle(self.color_image,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(self.color_image,(i[0],i[1]),2,(0,0,255),3)
                self.Circle_x = i[0]
                self.Circle_y = i[1]

        cnts, hierarchy = cv2.findContours(res_erode,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for i in cnts:
            #Moment = cv2.moments(cnts)
            Moment = cv2.moments(res_erode)
            self.cX = int(Moment["m10"] / Moment["m00"])
            self.cY = int(Moment["m01"] / Moment["m00"])
            cv2.circle(self.color_image,(self.cX,self.cY),7,(255,255,255),-1)
            cv2.putText(self.color_image, "center", (self.cX, self.cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            #print(cX,cY)

    '''
    Pour bien calculer les angles.
    Faut bien mettre les paramettres.
    '''
    # retourne l'angle dans ce moment.
    def Calcule_angle_curr(self):
        dx = self.Circle_x - self.cX
        dy = self.Circle_y - self.cY
        angle_curr = self.Calcu_angle(dx, dy)
        return angle_curr

    def Calcule_angle_target(self):
        dx = self.mouse_x-self.cX
        dy = self.mouse_y-self.cY
        angle_target = self.Calcu_angle(dx, dy)
        return angle_target

    '''
    Dessiner la ligne entre la position de robot et le but.
    paramettre: cX, cY, mouse_x, mouse_y.
    Faut l'appller apres le capteur d'image.
    '''
    def dessin_info(self):
        cv2.circle(self.color_image,(self.mouse_x,self.mouse_y),6,(0,0,255),-1)
        cv2.line(self.color_image,(self.cX,self.cY),(self.mouse_x,self.mouse_y),(0,0,255))
        cv2.arrowedLine(self.color_image,(self.cX,self.cY),(self.Circle_x,self.Circle_y),(0,0,255))
        pass

    '''
    faut bien le mettre dans un boucle.
    '''
    def window_default(self, text='Window default'):
        cv2.namedWindow(text)
        cv2.imshow(text, self.color_image)
        key = cv2.waitKey(1)
        if(key == 27):
            self.state = 0

    def get_state(self):
        pass
        return self.state

    '''
    L'ordre de bien executer les image proc.
    c'est juste un conseille

    retourne le code -1 ou 1
    '''
    def exe_main(self):
        if(self.Init == False):
            print("No init")
            return -1
        self.ImageCap() # recuperer l'image.
        self.ImageProc()  # calcule les valeurs de base.
        self.window_default()
        
        
    

    

    

    
