

'''  list de fonctions   '''
# __init()__
# init_proc()
# _get_res_image()
# _calcu_angle(dx, dy)
# _image_cap()
# image_proc()
# calcule_angle_curr()
# calcule_angle_target()

import pyrealsense2 as rs
import numpy as np
import cv2
import math

kernel = np.ones((7,7),np.int8)
Init = False
pipeline = None
color_image = np.zeros((480,640,3),np.uint8)
output_image = np.zeros((480,640,3),np.uint8)
mouse_x = 0
mouse_y = 0

class ImageProc:

    def __init__(self):
        self.cx = 0 
        self.cy = 0
        self.target_x = 0
        self.target_y = 0
        self.rect_x = 0 
        self.rect_y = 0
        self.state = 1
        """La valeur par default est l'orange."""
        self.l_valeur = np.array([0, 110, 114])
        self.h_valeur = np.array([16, 255, 255])
        pass

    def get_posx(self):
        return self.cx

    def get_posy(self):
        return self.cy

    def set_tarx(self,target_x):
        self.target_x = target_x

    def set_tary(self,target_y):
        self.target_y = target_y

    def set_couleur(self,String):
        if(String == "Vert"):
            self.l_valeur = np.array([53,91,69])
            self.h_valeur = np.array([91,255,244])
        if(String == "Rouge"):
            pass
        if(String == "Violet"):
            pass 
        if(String == "Noir"):
            pass

    @staticmethod
    def init_proc():
        global Init, pipeline
        pipeline = rs.pipeline()
        config = rs.config()
        #config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline.start(config)
        Init = True

    @staticmethod
    def image_cap():
        global color_image, output_image
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        output_image = color_image

        
    def _get_res_image(self):
        #pour separer les coleurs deffierent.
        hsv_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        # afin de trouver les regions de couleur.
        mask = cv2.inRange(hsv_image,self.l_valeur,self.h_valeur)
        # afin de trouver les images de resultat.
        result = cv2.bitwise_and(color_image,color_image,mask=mask)
        # pour trouver les images de gris.
        res_gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        # afin de bien recuperer les images de binare.
        ret,res_binary = cv2.threshold(res_gray,0,255,cv2.THRESH_BINARY)
        # pour bien trouver les region.
        res_close = cv2.morphologyEx(res_binary, cv2.MORPH_CLOSE, kernel,iterations=9)
        res_in_rect = res_close - res_binary 
        res_in_rect = cv2.erode(res_in_rect,kernel,iterations=1)
        res_erode = cv2.erode(res_close,kernel,iterations=1)
        return res_erode, res_in_rect

    def _calcu_angle(self,dx,dy):
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

    def image_proc(self):
        """Faut appller le init_proc() tout d'abord."""
        res_erode, res_in_rect = self._get_res_image()

        Moment_rect = cv2.moments(res_in_rect)
        if (Moment_rect["m00"] != 0):
            self.rect_x = int(Moment_rect["m10"] / Moment_rect["m00"])
            self.rect_y = int(Moment_rect["m01"] / Moment_rect["m00"])

        # afin de trouver les centres de la rectangulaire.
        cnts, hierarchy = cv2.findContours(res_erode,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for i in cnts:
            #Moment = cv2.moments(cnts)
            moment = cv2.moments(res_erode)
            self.cx = int(moment["m10"] / moment["m00"])
            self.cy = int(moment["m01"] / moment["m00"])
            cv2.circle(output_image,(self.cx,self.cy),7,(255,255,255),-1)
            cv2.putText(output_image, "center", (self.cx, self.cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            #print(cX,cY)

    '''
    Pour bien calculer les angles.
    Faut bien mettre les paramettres.
    '''
    # retourne l'angle dans ce moment.
    def calcule_angle_curr(self):
        dx = self.rect_x - self.cx
        dy = self.rect_y - self.cy
        angle_curr = self._calcu_angle(dx, dy)
        return angle_curr

    def calcule_angle_target(self):
        dx = mouse_x-self.cx
        dy = mouse_y-self.cy
        angle_target = self._calcu_angle(dx, dy)
        return angle_target

    # pour le mission 2
    def calcule_angle_target_target(self):
        dx = self.target_x - self.cx
        dy = self.target_y - self.cy
        angle_target = self._calcu_angle(dx, dy)
        return angle_target

    '''
    Dessiner la ligne entre la position de robot et le but.
    paramettre: cX, cY, mouse_x, mouse_y.
    Faut l'appller apres le capteur d'image.
    '''
    def dessin_info(self):
        cv2.circle(output_image,(mouse_x,mouse_y),6,(0,0,255),-1)
        cv2.line(output_image,(self.cx,self.cy),(mouse_x,mouse_y),(0,0,255))
        cv2.arrowedLine(output_image,(self.cx,self.cy),(self.rect_x,self.rect_y),(0,0,255))
        pass

########[test]########
    '''
    faut bien le mettre dans un boucle.
    '''
    def _window_default(self, text='Window default'):
        cv2.namedWindow(text)
        cv2.imshow(text, self.color_image)
        key = cv2.waitKey(1)
        if(key == 27):
            self.state = 0

    def _get_state(self):
        pass
        return self.state

    '''
    L'ordre de bien executer les image proc.
    c'est juste un conseille

    retourne le code -1 ou 1
    '''
    def _exe_main(self):
        if(self.Init == False):
            print("No init")
            return -1
        self.image_cap() # recuperer l'image.
        self.image_proc()  # calcule les valeurs de base.
        self._window_default()
        
        
    

    

    

    
