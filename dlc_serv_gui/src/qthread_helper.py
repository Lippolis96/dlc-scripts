from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread

# Custom stream to replace sys.stdout. Uses Queue for thread-safety
class WriteStream(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass


# A QObject (to be run in a QThread) which sits waiting for data to come through a Queue.Queue().
# It blocks until data is available, and one it has got something from the queue, it sends
# it to the "MainThread" by emitting a Qt Signal
class MyReceiver(QObject):
    mysignal = pyqtSignal(str)

    def __init__(self, queue, textfn, *args,**kwargs):
        QObject.__init__(self,*args,**kwargs)
        self.queue = queue
        self.mysignal.connect(textfn)

    @pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)


# Convert a function to a runable object
class ObjectFunction(QObject):
    def __init__(self, f, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.f = f

    @pyqtSlot()
    def run(self):
        self.f()


# Create a thread and run provided object function in that thread
# IMPORTANT: returned task and thread must be immediately saved somewhere
@pyqtSlot()
def createRunThread(taskObject):
    thread = QThread()
    taskObject.moveToThread(thread)
    thread.started.connect(taskObject.run)
    thread.start()
    return thread
