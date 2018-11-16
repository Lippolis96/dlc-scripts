import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2

#########################
# CONSTANTS
#########################
FRAME_X_LIM = [100, 750]
FRAME_Y_LIM = [100, 750]
FRAME_X_SIZE = FRAME_X_LIM[1] - FRAME_X_LIM[0]
FRAME_Y_SIZE = FRAME_Y_LIM[1] - FRAME_Y_LIM[0]

COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

def getPoint(dframe, row, cols, xlim, ylim):
    x = int(df.at[row, cols[0]] - xlim[0])
    y = int(df.at[row, cols[1]] - ylim[0])
    return (x, y)


#########################
# Open CSV file with PANDAS
#########################
dataFileName = sys.argv[1]
print("Opening file ::: ", dataFileName)
df = pd.read_csv(dataFileName, sep=',', header=None, dtype=float, skiprows=3)
colX = np.array([1, 4, 7, 10, 13])
colY = np.array([2, 5, 8, 11, 14])
nRows = len(df)
nPoints = len(colX)


#########################
# Statistical analysis of goodness of joints
#########################
# Compute velocity per frame of each tracked point via v(t) = sqrt((x(t+dt) - x(t))^2 + (y(t+dt) - y(t))^2)
#   - Find CDF of velocities for each tracked point, plot it
# Compute length of each joint via L(t) = sqrt((x1(t) - x2(t))^2 + (y1(t) - y2(t))^2)
#   - Plot joint length as a function of time
#   - Compute how many times at least one joint is more than 2 times different from its mean value. Those joints are for sure bad
#########################

V = np.zeros((nRows, nPoints))
L = np.zeros((nRows, nPoints-1))
prob = np.linspace(nRows, 1, nRows-1)
fig, ax = plt.subplots(ncols=2)
for iPoint in range(nPoints):
    X = np.array(df[colX[iPoint]])
    Y = np.array(df[colY[iPoint]])
    VX = X[1:] - X[:-1]
    VY = Y[1:] - Y[:-1]
    V[1:, iPoint] = np.sqrt(VX**2 + VY**2)
    ax[0].semilogy(np.sort(V[1:, iPoint]), prob, label=str(iPoint))

    if iPoint < nPoints-1:
        Xnew = np.array(df[colX[iPoint+1]])
        Ynew = np.array(df[colY[iPoint+1]])
        L[:, iPoint] = np.sqrt((X - Xnew)**2 + (Y - Ynew)**2)
        ax[1].plot(L[:, iPoint], label=str(iPoint))

ax[0].set_xlabel("velocity in pixel")
ax[0].set_ylabel("CDF of number of frames")
ax[1].set_xlabel("frame index")
ax[1].set_ylabel("Joint length")
ax[0].legend()
ax[1].legend()
plt.show()

LAVG = np.average(L, axis = 0)
print("Average lengths of joints are", LAVG)

SHIT_JOINTS = np.zeros(nRows).astype(bool)
for iPoint in range(nPoints-1):
    SHIT_JOINTS = np.logical_or(SHIT_JOINTS, L[:, iPoint] > 2 * LAVG[iPoint])
    SHIT_JOINTS = np.logical_or(SHIT_JOINTS, L[:, iPoint] < 0.5 * LAVG[iPoint])

print("Total number of frames with bad joints", np.sum(SHIT_JOINTS))



#########################
# Draw circles and lines, save video
#########################

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('stickman.avi',fourcc, 100.0, (FRAME_X_SIZE, FRAME_Y_SIZE), isColor=True)

for iFrame in range(nRows):
    pic = np.zeros((FRAME_X_SIZE, FRAME_Y_SIZE, 3), dtype=np.uint8)
    for iPoint in range(nPoints):
        p1 = getPoint(df, iFrame, (colX[iPoint], colY[iPoint]), FRAME_X_LIM, FRAME_Y_LIM)
        if V[iFrame, iPoint] > 70:
            pic = cv2.circle(pic, p1, 10, COLOR_RED, 2)
        else:
            pic = cv2.circle(pic, p1, 10, COLOR_BLUE, 2)


    for iPoint in range(nPoints-1):
        p1 = getPoint(df, iFrame, (colX[iPoint], colY[iPoint]), FRAME_X_LIM, FRAME_Y_LIM)
        p2 = getPoint(df, iFrame, (colX[iPoint+1], colY[iPoint+1]), FRAME_X_LIM, FRAME_Y_LIM)
        if (L[iFrame, iPoint] > 2*LAVG[iPoint]) or (L[iFrame, iPoint] < 0.5*LAVG[iPoint]):
            pic = cv2.line(pic, p1, p2, COLOR_RED, 2)
        else:
            pic = cv2.line(pic, p1, p2, COLOR_GREEN, 2)

    out.write(pic)#frame.transpose())  # OPENCV is col-major :(

    # cv2.imshow("cool", pic)
    # cv2.waitKey(0)
    # plt.figure()
    # plt.imshow(pic/255)
    # plt.show()

# Release everything if job is finished
out.release()
cv2.destroyAllWindows()