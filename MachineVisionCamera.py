import cv2
import easygui
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from mpl_toolkits import mplot3d

class MachineVisionCamerasAFAM():
    def __init__(self, cameraNumber):
        self.cameraNumber = cameraNumber
        self.horizontalPosition = 0
        self.verticalPosition = 0

        # Create dialog box which creates conversion factor for given camera
        conversionFactor = float(easygui.enterbox("Please enter the numerical conversion factor for Camera #" + str(self.cameraNumber + 1) + " in micrometers/pixel:"))
        self.conversionFactor = conversionFactor

        # Set camera to input camera index
        cap = cv2.VideoCapture(cameraNumber)
        self.cap = cap

        # Fast frame rate, low accuracy
        # tracker = cv2.TrackerMOSSE_create()
        # Slow frame rate, high accuracy
        tracker = cv2.TrackerCSRT_create()

        easygui.msgbox("Please draw a bounding box around the object to be tracked and press ENTER.", "Instructions", "Okay")

        # Allows the user to draw a bounding box around the desired object to track
        success, self.img = cap.read()
        bbox = cv2.selectROI("Tracking", self.img, False)
        tracker.init(self.img, bbox)
        self.bbox = bbox
        self.tracker = tracker

    # Run this method in the "while True" section of code, for a given instance of this class
    def runCamera(self):
        def drawBox(img, bbox):
            # Get coordinates.
            # x is the pixel value corresponding to horizontal movement of the object.
            # (i.e. x = 0 is the far left of the screen, bigger number is further to the right)
            # y is the pixel value corresponding to vertical movement of the object.
            x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            cv2.rectangle(img, (x, y), ((x + w), (y + h)), (255, 0, 255), 3, 1)
            cv2.putText(img, "Tracking", (25, 75), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 255), 2)

        timer = cv2.getTickCount()
        success, self.img = self.cap.read()

        success, self.bbox = self.tracker.update(self.img)
        self.horizontalPosition = self.bbox[0] * self.conversionFactor
        self.verticalPosition = self.bbox[1] * self.conversionFactor

        if success:
            drawBox(self.img, self.bbox)
        else:
            cv2.putText(self.img, "Lost", (25, 75), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        cv2.putText(self.img, str(int(fps)), (25, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)




#Initialize camera objects
camera1 = MachineVisionCamerasAFAM(cameraNumber=0)
camera2 = MachineVisionCamerasAFAM(cameraNumber=1)

easygui.msgbox("This program WILL CRASH if you click on the 3D Graph MatplotLib View. If you need to see the graph better, please only drag the dual camera view around.", "WARNING", "Okay")
# Arrays for last 50 datapoints for animation
xline = []
yline = []
zline = []

# Animated 3D Image
fig = plt.gcf()
ax = plt.axes(projection='3d')

fig.suptitle('3D Live View', fontsize=16)
ax.set_xlabel("X Axis")
ax.set_ylabel("Y Axis")
ax.set_zlabel("Z Axis")
ax.invert_xaxis()
ax.invert_zaxis()
ax.plot3D(xline, yline, zline, 'gray')
fig.show()


while True:
    camera1.runCamera()
    print("Camera 1 X Coordinate (micrometers): " + str("%.2f" % camera1.horizontalPosition))
    print("Camera 1 Z Coordinate (micrometers): " + str("%.2f" % camera1.verticalPosition))

    camera2.runCamera()
    print("Camera 2 Y Coordinate (micrometers): " + str("%.2f" % camera2.horizontalPosition))
    print("Camera 2 Z Coordinate (micrometers): " + str("%.2f" % camera2.verticalPosition))

    # Shows two camera feeds side by side
    Hori = np.concatenate((camera1.img, camera2.img), axis=1)
    cv2.imshow('DUAL CAMERA VIEW', Hori)

    # Append last 50 datapoints to these arrays
    xline.append(round(float(camera1.horizontalPosition),2))
    yline.append(round(float(camera2.horizontalPosition),2))
    zline.append(round(float(camera1.verticalPosition),2))

    # Refresh animated line
    if ((len(xline) | len(yline) | len(zline)) > 50):
        xline.clear()
        yline.clear()
        zline.clear()
        ax.cla()
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")
        ax.set_zlabel("Z Axis")
        ax.invert_xaxis()
        ax.invert_zaxis()

    # Update 3D plot with latest datapoint and redraw canvas
    ax.plot3D(xline,yline, zline, 'gray')
    fig.canvas.draw()


    if cv2.waitKey(1) & 0xff == ord('q'):
        break

