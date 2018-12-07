import os       # allows file operations and direct command line execution

qtCompilePrefStr = 'pyuic5 '\
                   + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dlcgui.ui')\
                   + ' -o ' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dlcgui.py')
print(qtCompilePrefStr)
os.system(qtCompilePrefStr)