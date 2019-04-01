import numpy as np
import matplotlib.pyplot as plt

class DraggableCircle:
    def __init__(self, circle):
        self.circle = circle
        self.press_shift = None

        #connect to all the events we need
        self.cidpress   = self.circle.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.circle.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion  = self.circle.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    # on button press we will see if the mouse is over us and store some data
    def on_press(self, event):
        if event.inaxes != self.circle.axes:
            print("yolo")
            return

        contains, attrd = self.circle.contains(event)
        if not contains:
            print("lolo")
            return
        
        print('event contains', self.circle.center)
        self.press_shift = np.array(self.circle.center) - np.array((event.xdata, event.ydata))

    # on motion we will move the circle if the mouse is over us
    def on_motion(self, event):
        if (self.press_shift is None) or (event.inaxes != self.circle.axes):
            return
        
        self.circle.center = tuple(np.array((event.xdata, event.ydata)) + self.press_shift)
        #self.circle.figure.canvas.draw()

    # on release we reset the press data
    def on_release(self, event):  
        self.press_shift = None
        self.circle.figure.canvas.draw()

    # disconnect all the stored connection ids
    def disconnect(self):
        self.circle.figure.canvas.mpl_disconnect(self.cidpress)
        self.circle.figure.canvas.mpl_disconnect(self.cidrelease)
        self.circle.figure.canvas.mpl_disconnect(self.cidmotion)

#fig, ax = plt.subplots()
#ax.set_xlim(0, 100)
#ax.set_ylim(0, 100)
#circles = [plt.Circle(np.random.uniform(0, 100, 2), 5, color='lightgreen') for i in range(20)]
#for circle in circles:
    #ax.add_artist(circle)

#drs = []
#for circle in circles:
    #dr = DraggableCircle(circle)
    #drs.append(dr)

#plt.show()
