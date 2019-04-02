import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
#from PIL import Image
import cv2

from lib.qt_wrapper import gui_fname, gui_fsave
from lib.parse_dlc_csv import parse_dlc_csv
from lib.draggable import DraggableCircle

class MyGui(object):
    def __init__(self):
        # Get video and the tracking file
        self.vidpath = gui_fname("Get video...", directory='./', filter="Video file (*.avi)")
        self.vidname = os.path.basename(self.vidpath)
        self.tmp_pwd = os.path.dirname(self.vidpath)
        self.csvpath = gui_fname("Get tracking file...", directory=self.tmp_pwd, filter="Tracking file (*.csv)")
        self.tmp_pwd = os.path.dirname(self.csvpath)
        
        # Parse tracking file
        self.nodeNames, self.X, self.Y, self.P = parse_dlc_csv(self.csvpath)
        self.NNodes = len(self.nodeNames)
        self.circleColors = plt.rcParams['axes.prop_cycle'].by_key()['color'][:self.NNodes]
        
        # Read video, extract first frame 
        self.capture = cv2.VideoCapture(self.vidpath)
        self.NFrames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        success, img = self.capture.read()
        if not success:
            raise ValueError("Reading video file failed")
        
        # Create subplots
        self.fig, self.ax = plt.subplots(tight_layout=True)
        self.fig.canvas.set_window_title(self.vidname)
        self.l = plt.imshow(img)
        self.drawCircles(0)
        plt.axis('off')
        
        # Create Slider
        self.sliderax = self.fig.add_axes([0.10, 0.02, 0.6, 0.03])#, axisbg='yellow')
        self.slider = Slider(self.sliderax, 'Frame', 0, self.NFrames-1, valinit=0)
        self.slider.on_changed(self.changeFrame)
        self.slider.drawon = False
        
        # Create Buttons
        self.prev_ax = plt.axes([0.8,  0.015, 0.03, 0.035])
        self.next_ax = plt.axes([0.83, 0.015, 0.03, 0.035])
        self.save_ax = plt.axes([0.88, 0.015, 0.07, 0.035])
        self.prev_button = Button(self.prev_ax, '<')
        self.next_button = Button(self.next_ax, '>')
        self.save_button = Button(self.save_ax, 'Save')
        self.prev_button.on_clicked(lambda event: self.changeFrame(self.slider.val-1))
        self.next_button.on_clicked(lambda event: self.changeFrame(self.slider.val+1))
        self.save_button.on_clicked(self.saveResults)

    #def __del__(self):
        #self.capture.release()
        #cv2.destroyAllWindows()
        
    def drawCircles(self, frameIdx):
        # Delete old circles
        # TODO: Are the mouse reactions associated with each circle deleted correctly?
        if hasattr(self, 'circles'):
            for circle in self.circles:
                circle.remove()

        # Create new circles
        self.circles = []
        self.draggable = []
        for i in range(self.NNodes):
            dragUpdate = lambda pos, frameIdx=frameIdx, labelIdx=i: self.updateLabel(frameIdx, labelIdx, pos[0], pos[1], 2)
            delUpdate  = lambda pos, frameIdx=frameIdx, labelIdx=i: self.updateLabel(frameIdx, labelIdx, pos[0], pos[1], 0)
            self.circles += [plt.Circle((self.X[frameIdx, i], self.Y[frameIdx, i]), 5, color=self.circleColors[i])] 
            self.ax.add_artist(self.circles[i])
            self.draggable += [DraggableCircle(self.circles[i], triggerOnRelease=dragUpdate, triggerOnRightClick=delUpdate)]
            
        # Create new legend
        self.updateLegend(frameIdx)

    def updateLegend(self, frameIdx):
        # TODO: Does the old legend need to be deleted?
        # self.ax.get_legend().remove()
        legendNames = ["["+ '{:.3f}'.format(1-p)+"] " + name for p, name in zip(self.P[frameIdx], self.nodeNames)]
        self.legend = self.ax.legend(self.circles, legendNames)

    def changeFrame(self, sliderValue):    
        frameIdx = int(np.clip(sliderValue, self.slider.valmin, self.slider.valmax))
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frameIdx)
        success, img = self.capture.read()
        if success:
            self.slider.val = frameIdx
            self.slider.valtext.set_text('{:5d}'.format(frameIdx))
            self.l.set_data(img)
            self.drawCircles(frameIdx)
            self.fig.canvas.draw()
        else:
            print("Loading frame", frameIdx, " /", self.NFrames, "failed for some reason")

    def updateLabel(self, frameIdx, labelIdx, x,y,p):
        self.X[frameIdx][labelIdx] = x
        self.Y[frameIdx][labelIdx] = y
        self.P[frameIdx][labelIdx] = p
        self.updateLegend(frameIdx)
        
    def saveResults(self, event):
        resultsfile = gui_fsave("Choose tracking file name to save results...", self.tmp_pwd, "Tracking file (*.csv)")
        with open(self.csvpath, "r") as fin:
            with open(resultsfile, "w") as fout:
                # Copy first 3 lines as they are
                for line in fin.readlines()[:3]:
                    fout.write(line)
                
                for i in range(self.NFrames):
                    # The format for each line is [x1,y1,p1,x2,y2,p2,...] where numbers are label indices
                    line_list = [i] + list(np.vstack((self.X[i], self.Y[i], self.P[i])).transpose().flatten())
                    fout.write(",".join([str(el) for el in line_list])+"\n")
        print("Seems to have saved successfully, exiting...")
        exit()

    def show(self):
        plt.show()

p = MyGui()
p.show()

# Create Radio Radio
#rax = plt.axes([0.025, 0.5, 0.15, 0.15])#, facecolor=axcolor)
#radio = RadioButtons(rax, self.nodeNames, active=0)

#def reset(event):
    #sfreq.reset()
    #samp.reset()
#button.on_clicked(reset)
