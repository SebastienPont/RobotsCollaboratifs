#version 0.0.1——>0.0.2

from math import sqrt
import math
from numpy.lib.function_base import delete
from pololu_imageproc import imageproc
from pololu_xbee import Xbee_app
from tkinter import *
from digi.xbee.devices import XBeeDevice
import pyrealsense2 as rs
import numpy as np
import cv2
import PIL.ImageTk as ImageTk
import PIL.Image as Image
import webbrowser
import threading
import time

imgproc = imageproc()
imgproc.init_proc()

xbee_1 = Xbee_app()
listbox = None
para = 1
mission_state = -1

t_mission_1 = None

def Mission_1_Thread():
    global t_mission_1
    StateBox.delete(0,0)
    StateBox.insert(0,"  RUNNING")
    Start_follow_line = True
    xbee_1.Init_device()
    xbee_1.Send_Msg("rdy")
    time.sleep(2)
    while(True):
        time.sleep(0.2)
        angle_curr = imgproc.Calcule_angle_curr()
        angle_target = imgproc.Calcule_angle_target()
        
        if ((angle_curr is not None) and (angle_target is not None)):
            if(abs(angle_curr - angle_target) < 10):
                print("Go Stright!!")
                xbee_1.Send_Msg("gfd")
                Start_follow_line = True
            else:
                if(Start_follow_line == True):
                    if(angle_curr - angle_target > 0):
                        print("Turn Left and dAngle:",angle_curr - angle_target)
                        xbee_1.Send_Msg("glf")
                    else:
                        print("Turn Right and dAngle:",angle_curr - angle_target)
                        xbee_1.Send_Msg("grt")
                else:
                    print("Turn Right!!")
                    xbee_1.Send_Msg("grt")

        if(math.sqrt((imgproc.cX - imgproc.mouse_x)*(imgproc.cX - imgproc.mouse_x)\
            +(imgproc.cY - imgproc.mouse_y)*(imgproc.cY - imgproc.mouse_y))<= 20):
            print("Fini Mission_1")
            xbee_1.Send_Msg("stp")
            #delete(t_mission_1)
            break
    StateBox.delete(0,0)
    StateBox.insert(0,"  BUSY")
    xbee_1.End_com()
    StateBox.delete(0,0)
    StateBox.insert(0,"  IDLE")
    pass

def cmd_mission_1():
    global mission_state, t_mission_1
    mission_state = 1
    InfoBox.delete(0,0)
    InfoBox.insert(0,"Mission_state: " + str(mission_state))
    t_mission_1 = threading.Thread(target=Mission_1_Thread)
    t_mission_1.start()
    pass

def cmd_mission_2():
    global mission_state
    mission_state = 2
    InfoBox.delete(0,0)
    InfoBox.insert(0,"Mission_state: " + str(mission_state))
    pass

def cmd_mission_3():
    global mission_state
    mission_state = 3
    InfoBox.delete(0,0)
    InfoBox.insert(0,"Mission_state: " + str(mission_state))
    pass

def cmd_exit_mission():
    global mission_state, t_mission_1
    mission_state = -1
    InfoBox.delete(0,0)
    InfoBox.insert(0,"Mission_state: " + str(mission_state))
    pass

def cmd_Photo():
    pass

def chk_cmd():
    pass

def draw_point(event):
    imgproc.mouse_x = event.x
    imgproc.mouse_y = event.y
    pass

def cmd_web():
    webbrowser.open("https://www.pololu.com/category/111/m3pi-robot")
    pass

# python multi thread
def cmd_Info_timer():
    while(True): 
        listbox.insert(1,"Angle de robot: "+str(imgproc.Calcule_angle_curr()))
        listbox.insert(2,"Angle de but: " +str(imgproc.Calcule_angle_target()))
        time.sleep(0.2)
        listbox.delete(0,2)

    
def cmd_start():
    global listbox
    root_page_start = Tk()
    root_page_start.geometry("300x300")
    root_page_start.title("Start page")

    frame = Frame(root_page_start)
    frame.pack()

    label = Label(root_page_start, text="Les Infos du robot")
    label.pack()

    listbox = Listbox(root_page_start)
    t = threading.Thread(target=cmd_Info_timer)
    t.start()
    listbox.pack()
    root_page_start.mainloop()
    delete(t)
    pass

def test_serial_thread():
    xbee_1.Init_device()
    xbee_1.Func_test_1()
    xbee_1.End_com()
    delete(t_test_serial)

def cmd_test_serial():
    global t_test_serial
    t_test_serial = threading.Thread(target=test_serial_thread)
    t_test_serial.start()
    print("Test fini")
    pass

# concevoir une fenêtre d'enfant.
def cmd_about_us():
    root_about_us = Tk()
    root_about_us.geometry("300x300")
    root_about_us.title("About us")

    label_1 = Label(root_about_us, text="Equipe Pololu Copyright")
    label_1.pack()
    label_2 = Label(root_about_us, text="Version 0.0.2")
    label_2.pack()
    root_about_us.mainloop()
    pass

def Img_process():
    imgproc.ImageCap()
    imgproc.ImageProc()
    imgproc.dessin_info()
    #BGR to RGBA
    img_temp = cv2.cvtColor(imgproc.color_image, cv2.COLOR_BGR2RGBA)
    current_image = Image.fromarray(img_temp)
    imagetk = ImageTk.PhotoImage(image=current_image)

    panel.imgtk = imagetk
    panel.config(image=imagetk)
    # apres 15ms on execute encore une fois.
    root.after(20, Img_process)

root = Tk()
root.geometry("1000x600")
# il faut pas changer la taille de la fenetre.
root.resizable(0,0)
root.title("Pololu 2021")

mainmenu = Menu(root)
mainmenu.add_command(label = "Photo", command= cmd_Photo)  
mainmenu.add_command(label = "Exit", command= root.destroy)

root.config(menu = mainmenu)

leftframe = Frame(root)
leftframe.pack(side=LEFT)

rightframe = Frame(root)
rightframe.pack(side=RIGHT)

panel = Label(leftframe)
panel.pack(padx = 40, pady= 40)
panel.bind('<Button-1>', draw_point)

btn_mission_1 = Button(leftframe, text = "Mission 1", command=cmd_mission_1)
btn_mission_1.place(x=50,y=0)
btn_mission_2 = Button(leftframe, text = "Mission 2", command=cmd_mission_2)
btn_mission_2.place(x=150,y=0)
btn_mission_3 = Button(leftframe, text = "Mission 3", command=cmd_mission_3)
btn_mission_3.place(x=250,y=0)
InfoBox = Listbox(leftframe,height=1,relief=SUNKEN)
InfoBox.insert(0,"Mission_state: " + str(mission_state))
InfoBox.place(x=350,y=5)
StateBox = Listbox(leftframe,height=1,relief=SUNKEN)
StateBox.insert(0,"  IDEL")
StateBox.place(x=450,y=5)
btn_mission_exit = Button(leftframe, text = "Mission Exit", command=cmd_exit_mission)
btn_mission_exit.place(x=600,y=0)


Var1 = IntVar()
Var2 = IntVar()
Var3 = IntVar()
Var4 = IntVar()
chkBttn_1 = Checkbutton(rightframe, text="Robot No1",variable=Var1, command=chk_cmd)
chkBttn_1.pack()
chkBttn_2 = Checkbutton(rightframe, text="Robot No2",variable=Var2, command=chk_cmd)
chkBttn_2.pack()
chkBttn_3 = Checkbutton(rightframe, text="Robot No3",variable=Var3, command=chk_cmd)
chkBttn_3.pack()
chkBttn_4 = Checkbutton(rightframe, text="Robot No4",variable=Var4, command=chk_cmd)
chkBttn_4.pack()

panel_logo = Label(rightframe)
panel_logo.pack(padx=40,pady=40)
load = Image.open("polytech.jpg")
load = load.resize((200,200))
load = np.array(load)
#img_temp = cv2.cvtColor(load, cv2.COLOR_BGR2RGBA)
current_image = Image.fromarray(load)
imagetk = ImageTk.PhotoImage(image=current_image)
panel_logo.imgtk = imagetk
panel_logo.config(image=imagetk)


root.config(cursor="arrow")
btn_func1 = Button(rightframe, text = "Start", command=cmd_start)
btn_func1.pack(fill="both", expand=False, padx=40,pady=10)
btn_serial = Button(rightframe, text = "Test Serial", command=cmd_test_serial)
btn_serial.pack(fill="both", expand=False, padx=40,pady=10)
btn_about = Button(rightframe, text = "About us", command=cmd_about_us)
btn_about.pack(fill="both", expand=False, padx=40,pady=10)
btn_web = Button(rightframe, text = "Viste the website", command=cmd_web)
btn_web.pack(fill="both", expand=False, padx=40,pady=10)


if __name__ == '__main__':

    try:

        Img_process()
        root.mainloop()

    finally:

        # Stop streaming
        imgproc.pipeline.stop()
 