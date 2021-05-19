
# app version 0.0.1——>0.0.2
#   ——>0.0.4(support the other color)
#   ——>1.0.0
#

#from PyQt5.QtCore import Qt
from math import sqrt
import math
from numpy.lib.function_base import delete
from pololu_imageproc import ImageProc
from pololu_xbee import XbeeApp
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
import pololu_imageproc

# daemon.
img_proc = ImageProc()
img_org_proc = ImageProc()
# pour initialiser le camera.
img_vert_proc = ImageProc()
img_vert_proc.set_couleur("Vert")
img_violet_proc = ImageProc()
img_violet_proc.set_couleur("Violet")

img_proc.init_proc()

# le deamon pour le Xbee.
xbee = XbeeApp()
xbee_org = XbeeApp()
xbee_vert = XbeeApp()
listbox = None
para = 1
mission_state = -1

"""Pour info: 1:Orange, 2:Vert ..."""
robot_info = {'robot_1': 0, 'robot_2': 0,
              'robot_3': 0, 'robot_4': 0}

"""Pour state de app: mission, robot_num"""
app_state = {'mission': 0, 'robot_num': 0}

robot_pos = {'robot_1_x': 0, 'robot_1_y': 0, 
            'robot_2_x': 0, 'robot_2_y': 0,
            'robot_3_x': 0, 'robot_3_y': 0,
            'robot_4_x': 0, 'robot_4_y': 0}

t_mission_1 = None

# les actions pour la mission_1.
def _mission_1_action(img_proc, xbee_instance):
    """Input est un process d'image."""
    start_follow_line = False
    angle_curr = img_proc.calcule_angle_curr()
    angle_target = img_proc.calcule_angle_target()

    if ((angle_curr is not None) and (angle_target is not None)):
        if(abs(angle_curr - angle_target) < 15):
            print("Go Stright!!")
            xbee_instance.send_msg("gfd")
        else:
            if(angle_curr - angle_target > 0):
                print("Turn Left and dAngle:",angle_curr - angle_target)
                xbee_instance.send_msg("glf")
            else:
                print("Turn Right and dAngle:",angle_curr - angle_target)
                xbee_instance.send_msg("grt")

    if(math.sqrt((img_proc.cx - pololu_imageproc.mouse_x)*(img_proc.cx - pololu_imageproc.mouse_x)\
        +(img_proc.cy - pololu_imageproc.mouse_y)*(img_proc.cy - pololu_imageproc.mouse_y))<= 20):
        print("Fini Mission_1")
        xbee_instance.send_msg("stp")
        return True

    return False

def _mission_1_thread():
    Org_fini = True
    Vert_fini = True
    state_box.delete(0,0)
    state_box.insert(0,"  RUNNING")
    xbee.init_port("COM25", 9600)
    print("-------")
    if (robot_info['robot_1'] == 1):
        Org_fini = False
        xbee_org.init_device("0013A20041BAEAD6")
        xbee_org.send_msg("rdy")
    if (robot_info['robot_2'] == 1):
        Vert_fini = False
        xbee_vert.init_device("0013A20041BAEAC1")
        xbee_vert.send_msg("rdy")

    time.sleep(2)
    while(Org_fini == False or Vert_fini == False):
        time.sleep(0.2)
        if (robot_info['robot_1'] == 1):
            Org_fini = _mission_1_action(img_org_proc, xbee_org)
        if (robot_info['robot_2'] == 1):
            time.sleep(0.1)
            Vert_fini = _mission_1_action(img_vert_proc, xbee_vert)

    state_box.delete(0,0)
    state_box.insert(0,"  BUSY")
    xbee.end_com()
    state_box.delete(0,0)
    state_box.insert(0,"  IDLE")
    pass

def _mission_2_action():
    pass

def _mission_2_thread():
    list_robot = []
    list_xbee = []
    list_pos = []
    robot_num = 0
    main_x = 0
    main_y = 0
    if (robot_info['robot_1'] == 1):
        xbee_org.init_device("0013A20041BAEAD6")
        xbee_org.send_msg("rdy")
        list_robot.append(img_org_proc)
        list_xbee.append(xbee_org)
        robot_num = robot_num + 1
    if (robot_info['robot_2'] == 1):
        xbee_vert.init_device("0013A20041BAEAC1")
        xbee_vert.send_msg("rdy")
        list_robot.append(img_vert_proc)
        list_xbee.append(xbee_vert)
        robot_num = robot_num + 1
    if (robot_info['robot_3'] == 1):
        #list_robot.append(img_violet_proc)
        robot_num = robot_num + 1
        pass

    if(robot_num == 0):
        print("No robot selected>>>")
        return
    while(True):
        time.sleep(0.1)   # 10Hz

        for i in list_robot:
            list_pos.append((i.get_posx,i.get_posy))

        list_robot[0].set_tarx(pololu_imageproc.mouse_x)
        list_robot[0].set_tary(pololu_imageproc.mouse_y)
        for i in range(1,len(list_robot)):
            list_robot[i].set_tarx(list_pos[i-1][0])
            list_robot[i].set_tary(list_pos[i-1][1])


        for i,xbee in zip(list_robot, list_xbee):
            angle_curr = i.calcule_angle_curr()
            angle_target = i.calcule_angle_target_target()

            if ((angle_curr is not None) and (angle_target is not None)):
                if(abs(angle_curr - angle_target) < 15):
                    print("Go Stright!!")
                    xbee.send_msg("gfd")
            else:
                if(angle_curr - angle_target > 0):
                    print("Turn Left and dAngle:",angle_curr - angle_target)
                    xbee.send_msg("glf")
                else:
                    print("Turn Right and dAngle:",angle_curr - angle_target)
                    xbee.send_msg("grt")

            if(math.sqrt((i.cx - i.target_x)*(i.cx - i.target_x)\
                +(i.cy - i.target_x)*(i.cy - i.target_x))<= 100):
                xbee.send_msg("stp")
        pass


def _mission_3_thread():
    state_box.delete(0,0)
    state_box.insert(0,"  RUNNING")
    xbee.init_port("COM25", 9600)
    print("-------")
    xbee_org.init_device("0013A20041BAEAD6")
    xbee_vert.init_device("0013A20041BAEAC1")
    xbee_org.send_msg("rdy")
    xbee_vert.send_msg("rdy")
    time.sleep(1)
    xbee_org.send_msg('gfd')
    xbee_vert.send_msg('gfd')
    time.sleep(1)
    xbee_org.send_msg('grt')
    xbee_vert.send_msg('grt')
    time.sleep(0.5)
    xbee_org.send_msg('gfd')
    xbee_vert.send_msg('gfd')
    time.sleep(1)
    xbee_org.send_msg('glf')
    xbee_vert.send_msg('glf')
    time.sleep(0.5)
    xbee_org.send_msg('gfd')
    xbee_vert.send_msg('gfd')
    time.sleep(1)
    xbee_org.send_msg('grt')
    xbee_vert.send_msg('grt')
    time.sleep(3)
    xbee_org.send_msg('stp')
    xbee_vert.send_msg('stp')
    time.sleep(1)
    state_box.delete(0,0)
    state_box.insert(0,"  BUSY")
    xbee.end_com()
    state_box.delete(0,0)
    state_box.insert(0,"  IDLE")
    pass

def cmd_mission_1():
    global mission_state, t_mission_1
    mission_state = 1
    info_box.delete(0,0)
    info_box.insert(0,"Mission_state: " + str(mission_state))
    t_mission_1 = threading.Thread(target= _mission_1_thread)
    t_mission_1.start()
    pass

def cmd_mission_2():
    global mission_state
    mission_state = 2
    info_box.delete(0,0)
    info_box.insert(0,"Mission_state: " + str(mission_state))
    t_mission_2 = threading.Thread(target= _mission_2_thread)
    t_mission_2.start()
    pass

def cmd_mission_3():
    global mission_state
    mission_state = 3
    info_box.delete(0,0)
    info_box.insert(0,"Mission_state: " + str(mission_state))
    t_mission_3 = threading.Thread(target= _mission_3_thread)
    t_mission_3.start()
    pass

def cmd_exit_mission():
    global mission_state, t_mission_1
    mission_state = -1
    info_box.delete(0,0)
    info_box.insert(0,"Mission_state: " + str(mission_state))
    pass

def cmd_photo():
    pass

def cmd_remote():
    root_page_remote = Tk()
    root_page_remote.geometry("300x300")
    root_page_remote.title("Remote")
    pass

def chk_cmd_1():
    if(var1.get() == 1):
        robot_info['robot_1'] = 1
    elif(var1.get() == 0):
        robot_info['robot_1'] = 0

def chk_cmd_2():
    if(var2.get() == 1):
        robot_info['robot_2'] = 1
    elif(var2.get() == 0):
        robot_info['robot_2'] = 0

def chk_cmd_3():
    if(var3.get() == 1):
        robot_info['robot_3'] = 1
    elif(var3.get() == 0):
        robot_info['robot_3'] = 0

def chk_cmd_4():
    if(var4.get() == 1):
        robot_info['robot_4'] = 1
    elif(var4.get() == 0):
        robot_info['robot_4'] = 0

def draw_point(event):
    pololu_imageproc.mouse_x = event.x
    pololu_imageproc.mouse_y = event.y
    pass

def cmd_web():
    webbrowser.open("https://www.pololu.com/category/111/m3pi-robot")
    pass

def cmd_info_timer():
    while(True): 
        listbox.insert(1,"Angle de robot: "+str(img_org_proc.calcule_angle_curr()))
        listbox.insert(2,"Angle de but: " +str(img_org_proc.calcule_angle_target()))
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
    t = threading.Thread(target=cmd_info_timer)
    t.start()
    listbox.pack()
    root_page_start.mainloop()
    delete(t)
    pass

def test_serial_thread():
    xbee.init_port("COM25", 9600)
    xbee_vert.init_device("0013A20041BAEAC1")
    xbee_org.init_device("0013A20041BAEAD6")
    xbee_vert.func_test_1()
    xbee_org.func_test_1()
    xbee.end_com()
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

    label_1 = Label(root_about_us, text= "Equipe Pololu Copyright")
    label_1.pack()
    label_2 = Label(root_about_us, text= "Version 1.0.2")
    label_2.pack()
    label_3 = Label(root_about_us, text= "Copyright 2021")
    label_3.pack()
    btn_git = Button(root_about_us, text = "Page Github", command=cmd_git)
    btn_git.place(x=110, y=200)
    root_about_us.mainloop()
    pass

def cmd_git():
    pass

root = Tk()
root.geometry("1000x600")
# il faut pas changer la taille de la fenetre.
root.resizable(0,0)
root.title("Pololu 2021")

mainmenu = Menu(root)
mainmenu.add_command(label = "Photo", command= cmd_photo)
mainmenu.add_command(label = "Remote", command = cmd_remote)  
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
info_box = Listbox(leftframe,height=1,relief=SUNKEN)
info_box.insert(0,"Mission_state: " + str(mission_state))
info_box.place(x=350,y=5)
state_box = Listbox(leftframe,height=1,relief=SUNKEN)
state_box.insert(0,"  IDEL")
state_box.place(x=450,y=5)
btn_mission_exit = Button(leftframe, text = "Mission Exit", command=cmd_exit_mission)
btn_mission_exit.place(x=600,y=0)

var1 = IntVar() 
var2 = IntVar() 
var3 = IntVar() 
var4 = IntVar() 
chk_bttn_1 = Checkbutton(rightframe, text="Robot No1",variable=var1, command=chk_cmd_1)
chk_bttn_1.pack()
chk_bttn_2 = Checkbutton(rightframe, text="Robot No2",variable=var2, command=chk_cmd_2)
chk_bttn_2.pack()
chk_bttn_3 = Checkbutton(rightframe, text="Robot No3",variable=var3, command=chk_cmd_3)
chk_bttn_3.pack()
chk_bttn_4 = Checkbutton(rightframe, text="Robot No4",variable=var4, command=chk_cmd_4)
chk_bttn_4.pack()

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

def get_pos():
    if(robot_info['robot_1'] == 1):
        robot_pos['robot_1_x'] = img_org_proc.get_posx()
        robot_pos['robot_1_y'] = img_org_proc.get_posy()
    if(robot_info['robot_2'] == 1):
        robot_pos['robot_2_x'] = img_vert_proc.get_posx()
        robot_pos['robot_2_y'] = img_vert_proc.get_posy()
    if(robot_info['robot_3'] == 1):
        robot_pos['robot_3_x'] = img_violet_proc.get_posx()
        robot_pos['robot_3_y'] = img_violet_proc.get_posy()
    pass

def img_process():
    """traiter les images de vert et orange."""
    img_proc.image_cap()

    if(robot_info['robot_1'] == 1):
        img_org_proc.image_proc()
    if(robot_info['robot_2'] == 1):
        img_vert_proc.image_proc()
    #pour les dessiner separament.
    if(robot_info['robot_1'] == 1):
        img_org_proc.dessin_info()
    if(robot_info['robot_2'] == 1):
        img_vert_proc.dessin_info()

    img_temp = cv2.cvtColor(pololu_imageproc.output_image, cv2.COLOR_BGR2RGBA)
    current_image = Image.fromarray(img_temp)
    image_tk = ImageTk.PhotoImage(image=current_image)

    panel.imgtk = image_tk
    panel.config(image=image_tk)
    # apres 20ms on execute encore une fois.
    root.after(20, img_process)

if __name__ == '__main__':

    try:

        img_process()
        root.mainloop()

    finally:
        
        # Stop streaming
        pololu_imageproc.pipeline.stop()
 