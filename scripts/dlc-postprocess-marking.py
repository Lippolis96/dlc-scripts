import os, sys, json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
#from PIL import Image
import cv2

from lib.qt_wrapper import gui_fname, gui_fsave
from lib.parse_dlc_results import parse_dlc_csv
from lib.draggable import DraggableCircle

'''

GUI for manual correction of DLC tracking
   
===================
= Current features
===================
* Loads (.mp4) and (.avi) videos
* Loads (.csv) markings made by DLC
* Plots 1 frame at a time
* Plots marked points as circles
* Plots points with poor confidence in different style - hollow circles with stars inside :)
* Plots confidence of points on legend
* Can move to arbitrary frame by clicking slider in GUI
* Can move to next/previous frame with keys (see controls section)
* Can auto find frame with low threshold
* Can save markings back to (.csv) file
* Saves user variables to temporary file, allowing faster repeated folder access

===================
= Controls
===================
* [Key= Left]         loads previous frame (unless current frame is 0)
* [Key= Right]        loads next frame     (unless current frame is nFrames-1)
* [Key= Space]        finds and loads next frame, where there is at least one bad point
* [Key= -]            dereases circle size
* [Key= +]            increases circle size
* [Left mouse drag]   moves point to a new location
* [Left mouse drag]   marks point as good - Set confidence to 2 (200% because user has powers beyond math)
* [Right mouse click] marks point as bad  - Set confidence to 0 
* [Exact Frame Field] Enter exact frame number and press ENTER (frames are numbered from 0)
* [Save GUI button]   saves edits to CSV file
'''


class MyGui(object):
    def __init__(self):
        # Set constants
        self.circleRadius = 5
        self.circleRadiusDelta = 1
        
        # Attempt to import settings file
        settingsFilePath = "settings_postprocess_marking.json"
        if os.path.isfile(settingsFilePath):
            with open(settingsFilePath, 'r') as f:
                jsonData = json.load(f)
                self.tmp_pwd       = jsonData['tmp_pwd']         # Get most recently used path
                self.confThreshold = jsonData['confThreshold']   # Get confidence threshold
        else:
            self.tmp_pwd = "./"
            self.confThreshold = 0.99    # 1-p_value
        
        # Get video and the tracking file
        self.vidpath = gui_fname("Get video...", directory=self.tmp_pwd, filter="Video file (*.avi *.mp4)")
        self.vidname = os.path.basename(self.vidpath)
        if self.vidpath != '':
            self.tmp_pwd = os.path.dirname(self.vidpath)
        self.csvpath = gui_fname("Get tracking file...", directory=self.tmp_pwd, filter="Tracking file (*.csv)")
        if self.csvpath != '':
            self.tmp_pwd = os.path.dirname(self.csvpath)
        self.with_markings = self.csvpath != ''
        
        # Save most recent path to settings file
        with open(settingsFilePath, 'w') as f:
            json.dump({
                "tmp_pwd"       : self.tmp_pwd,
                "confThreshold" : self.confThreshold
            }, f)
        
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
        plt.axis('off')
        
        # Create Slider
        self.sliderax = self.fig.add_axes([0.10, 0.02, 0.6, 0.03])#, axisbg='yellow')
        self.slider = Slider(self.sliderax, 'Frame', 0, self.NFrames-1, valinit=0)
        self.slider.on_changed(self.changeFrame)
        self.slider.drawon = False
        
        # # Create Buttons
        # self.prev_ax = plt.axes([0.8,  0.015, 0.03, 0.035])
        # self.next_ax = plt.axes([0.83, 0.015, 0.03, 0.035])
        # self.prev_button = Button(self.prev_ax, '<')
        # self.next_button = Button(self.next_ax, '>')
        # self.prev_button.on_clicked(lambda event: self.changeFrameExternal(self.slider.val-1))
        # self.next_button.on_clicked(lambda event: self.changeFrameExternal(self.slider.val+1))
        
        # Create Frame input
        self.frameTextBoxaxes = self.fig.add_axes([0.8,  0.015, 0.06, 0.035])
        self.frameTextBox = TextBox(self.frameTextBoxaxes , 'exactFrame', initial='')
        self.frameTextBox.on_submit(lambda text: self.changeFrameExternal(int(text)))        
        
        # Additional functionality if CSV file provided
        if self.with_markings:
            # Parse tracking file
            self.nodeNames, self.X, self.Y, self.P = parse_dlc_csv(self.csvpath)
            self.NNodes = len(self.nodeNames)
            self.circleColors = plt.rcParams['axes.prop_cycle'].by_key()['color'][:self.NNodes]
            
            # Draw circles
            self.drawCircles(0)
            
            # Create marking-specific buttons
            self.save_ax = plt.axes([0.88, 0.015, 0.07, 0.035])
            self.save_button = Button(self.save_ax, 'Save')
            self.save_button.on_clicked(self.saveResults)
            
        # Create Key press reactions
        self.fig.canvas.mpl_connect('key_press_event', lambda event: self.keyPressReact(event))
        

    #def __del__(self):
        #self.capture.release()
        #cv2.destroyAllWindows()
        
        
    def keyPressReact(self, event):
        print('press', event.key)
        sys.stdout.flush()
        if event.key == 'left':
            self.changeFrameExternal(self.slider.val-1)
        elif event.key == 'right':
            self.changeFrameExternal(self.slider.val+1)
        elif (event.key == '-') and self.with_markings:
            self.updateCircleRadius(self.circleRadius - self.circleRadiusDelta)
        elif event.key == '+' and self.with_markings:
            self.updateCircleRadius(self.circleRadius + self.circleRadiusDelta)
        elif event.key == ' ' and self.with_markings:
            self.gotoNextBadFrameIdx()
        
        
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
            self.circles += [plt.Circle((self.X[frameIdx, i], self.Y[frameIdx, i]), self.circleRadius, color=self.circleColors[i])] 
            self.ax.add_artist(self.circles[i])
            self.draggable += [DraggableCircle(self.circles[i], triggerOnRelease=dragUpdate, triggerOnRightClick=delUpdate)]
            self.updateCirclePVal(self.circles[i], self.P[frameIdx, i])
            
        # Create new legend
        self.updateLegend(frameIdx)
        
        
    # Circle shape depends on whether it is a good or a bad circle
    def updateCirclePVal(self, c, p):
        if p < self.confThreshold:
            c.set_fill(False)
            c.set_hatch('*')
            c.set_linewidth(3)
        else:
            c.set_fill(True)
            c.set_hatch('')
            c.set_linewidth(1)

    
    def updateCircleRadius(self, r):
        self.circleRadius = r
        for circle in self.circles:
            circle.set_radius(r)
        self.fig.canvas.draw()
        

    def updateLegend(self, frameIdx):
        # TODO: Does the old legend need to be deleted?
        # self.ax.get_legend().remove()
        legendNames = ["["+ '{:.3f}'.format(p)+"] " + name for p, name in zip(self.P[frameIdx], self.nodeNames)]
        self.legend = self.ax.legend(self.circles, legendNames, title='Confidence')

        
    def changeFrame(self, sliderValue):    
        frameIdx = int(np.clip(sliderValue, self.slider.valmin, self.slider.valmax))
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frameIdx)
        success, img = self.capture.read()
        if success:
            print("Moving to frame", frameIdx, "/", self.NFrames)
            self.slider.val = frameIdx  # Already done automatically. Just to ensure slider value is always an integer
            self.slider.valtext.set_text('{:5d}'.format(frameIdx))
            self.l.set_data(img)
            if self.with_markings:
                self.drawCircles(frameIdx)
            self.fig.canvas.draw()
        else:
            print("Loading frame", frameIdx, "/", self.NFrames, "failed for some reason")
            
    def changeFrameExternal(self, frameIdx):
        self.slider.set_val(frameIdx)

    def updateLabel(self, frameIdx, labelIdx, x,y,p):
        self.X[frameIdx][labelIdx] = x
        self.Y[frameIdx][labelIdx] = y
        self.P[frameIdx][labelIdx] = p
        self.updateCirclePVal(self.circles[labelIdx], p)
        self.updateLegend(frameIdx)
        
        
    # Locate the next bad frame, and move to it
    def gotoNextBadFrameIdx(self):
        badFrameIdx = int(self.slider.val)
        while (badFrameIdx + 1 < self.NFrames):
            badFrameIdx += 1
            if np.min(self.P[badFrameIdx]) < self.confThreshold:
                self.changeFrameExternal(badFrameIdx)
                return
        
        if badFrameIdx != int(self.slider.val):
            self.changeFrameExternal(badFrameIdx)
        

        
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
