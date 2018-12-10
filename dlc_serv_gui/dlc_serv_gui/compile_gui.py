import os       # allows file operations and direct command line execution
from subprocess import run


path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'dlcgui.ui')
pyFile = os.path.join(path, 'dlcgui.py')
qtCompilePrefStr = 'pyuic5 '+ uiFile + ' -o ' + pyFile
print(qtCompilePrefStr)
os.system(qtCompilePrefStr)

# command = 'python -m PyQt5.uic.pyuic '+uiFile+' -o '+pyFile+' -x'
# exec(command)

run(['pyuic5', uiFile, '-o', pyFile])