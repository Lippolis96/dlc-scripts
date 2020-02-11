import os
from ij.io import OpenDialog
from ij import IJ
from ij.gui import PointRoi 
#from ij import WindowManager as WM 
#import ij.macro.Functions # import makeSelection

########################
# Open file dialog
########################
od = OpenDialog("Select the file to import")
srcDir = od.getDirectory()
if srcDir is None:
	print("Cancelled by user")
else:
	filePathName = os.path.join(srcDir, od.getFileName())

	print("importing from file", filePathName)
	
	########################
	# Get data
	########################
	#text = File.openAsString(fileName).split("\n")
	f = open(filePathName, "r")
	text = f.readlines()
	
	#these are the column indexes
	header = text[0].rstrip().split(",")
	headerDict = dict([(header[i], i) for i in range(len(header))])
	iX = headerDict["X"]
	iY = headerDict["Y"]
	iSlice = headerDict["Slice"]
	oldSlice = 1
	
	xLst = []
	yLst = []
	
	# Loop over all lines
	IJ.getImage().setSlice(1)
	for i in range(1, len(text)):
		lineSplit = text[i].rstrip().split(",");
		x = float(lineSplit[iX])
		y = float(lineSplit[iY])
		sl = int(lineSplit[iSlice])

		# Separate input into slices
		if sl == oldSlice:	
			xLst += [x]
			yLst += [y]
		else:
			print "Reading slice",oldSlice, ":::", xLst, yLst

			# Place selection points on the frame
			# makeSelection("point", xLst, yLst);

			break
			
			for x1,y1 in zip(xLst, yLst):
				IJ.makePoint(x1, y1);
			

			#roi = PointRoi(0, 0)
			#
			#	roi.addPoint(IJ.getImage(), x1, y1)
			#	IJ.getImage().setRoi(roi)

			# Move to the next frame
			IJ.getImage().setSlice(sl+1)

			# Update point storage
			oldSlice = sl
			xLst = [x]
			yLst = [y]
	
	# Finish off the last trailing slice
	print "Reading slice",oldSlice, ":::", xLst, yLst
	for x1,y1 in zip(xLst, yLst):
		IJ.makePoint(x1, y1);
