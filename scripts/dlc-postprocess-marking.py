import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
#from PIL import Image
import cv2

from lib.qt_wrapper import gui_fname
from lib.parse_dlc_csv import parse_dlc_csv
from lib.draggable import DraggableCircle

class MyGui(object):
    def __init__(self):
        # Get video and the tracking file
        self.vidpath = gui_fname("Get video...", directory='./', filter="Video file (*.avi)")
        tmp_pwd = os.path.dirname(self.vidpath)
        self.csvpath = gui_fname("Get tracking file...", directory=tmp_pwd, filter="Tracking file (*.csv)")
        
        # Parse tracking file
        self.nodeNames, self.X, self.Y, self.P = parse_dlc_csv(self.csvpath)
        self.circleColors = plt.rcParams['axes.prop_cycle'].by_key()['color'][:len(self.nodeNames)]
        
        # Read video, extract first frame 
        self.capture = cv2.VideoCapture(self.vidpath)
        self.NFrames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        success, img = self.capture.read()
        if not success:
            raise ValueError("Reading video file failed")
        
        # Create subplots
        self.fig, self.ax = plt.subplots()
        self.l = plt.imshow(img)
        self.drawCircles(0)
        plt.axis('off')
        
        # Create Slider
        self.sliderax = self.fig.add_axes([0.2, 0.02, 0.6, 0.03], axisbg='yellow')
        self.slider = Slider(self.sliderax, 'Frame', 0, self.NFrames-1, valinit=0)
        self.slider.on_changed(self.update)
        self.slider.drawon = False

    #def __del__(self):
        #self.capture.release()
        #cv2.destroyAllWindows()
        
    def drawCircles(self,idx):
        if hasattr(self, 'circles'):
            for circle in self.circles:
                circle.remove()

        self.circles = [plt.Circle((x, y), 5, color=c) for x,y,c in zip(self.X[idx], self.Y[idx], self.circleColors)]
        for circle in self.circles:
            self.ax.add_artist(circle)
        self.draggable = [DraggableCircle(circle) for circle in self.circles]
        
        legendNames = ["["+ '{:.3f}'.format(1-p)+"] " + name for p, name in zip(self.P[idx], self.nodeNames)]
        self.legend = self.ax.legend(self.circles, legendNames)


    def update(self, value):    
        idx = int(value)
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, img = self.capture.read()
        if success:
            self.l.set_data(img)
            self.drawCircles(idx)
            self.slider.valtext.set_text('{}'.format(idx))
            self.fig.canvas.draw()
        else:
            print("Loading frame", idx, " /", self.NFrames, "failed for some reason")

    def show(self):
        plt.show()

p = MyGui()
p.show()

#resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
#button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

# Create Radio Radio
#rax = plt.axes([0.025, 0.5, 0.15, 0.15])#, facecolor=axcolor)
#radio = RadioButtons(rax, self.nodeNames, active=0)

#def reset(event):
    #sfreq.reset()
    #samp.reset()
#button.on_clicked(reset)




#def colorfunc(label):
    #l.set_color(label)
    #fig.canvas.draw_idle()
#radio.on_clicked(colorfunc)

#plt.show()
