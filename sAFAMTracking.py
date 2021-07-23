import cv2
import easygui

conversionFactor = float(easygui.enterbox("Please enter the numerical conversion factor, in micrometers/pixel:"))

cap = cv2.VideoCapture('D:\GIT\sAFAM\safam-main\sAFAM Control\Python_interface\Python Interface for DAC\cover glass slide\Video1-10.avi')

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

#Fast frame rate, low accuracy
#tracker = cv2.TrackerMOSSE_create()
#Slow frame rate, high accuracy
tracker = cv2.TrackerCSRT_create()

def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


success, img = cap.read()
#frame75 = rescale_frame(img, percent=25)
#img = frame75
bbox = cv2.selectROI("Tracking", img, False)
tracker.init(img, bbox)

def drawBox(img, bbox):

    # Get coordinates.
    # x is the pixel value corresponding to horizontal movement of the object.
    # (i.e. x = 0 is the far left of the screen, bigger number is further to the right)
    # y is the pixel value corresponding to vertical movement of the object.
    x,y,w,h = int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])
    cv2.rectangle(img,(x,y),((x+w),(y+h)),(255,0,255),3,1)
    cv2.putText(img, "Tracking", (25, 75), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 255), 2)


while True:
    timer = cv2.getTickCount()
    success, img = cap.read()
    #frame75 = rescale_frame(img, percent=25)
    #img = frame75

    xCoordinate = bbox[0] * conversionFactor
    yCoordinate = bbox[1] * conversionFactor

    xCoordinateString = "X Coordinate (micrometers): " + str("%.2f" % xCoordinate)
    yCoordinateString = "Y Coordinate (micrometers): " + str("%.2f" % yCoordinate)


    success, bbox = tracker.update(img)

    if success:
        drawBox(img, bbox)
    else:
        cv2.putText(img, "Lost", (25, 75), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)

    fps = cv2.getTickFrequency()/(cv2.getTickCount()-timer)
    cv2.putText(img, str(int(fps)), (25,50), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0,0,255),2)
    cv2.putText(img, xCoordinateString, (150, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 2)
    cv2.putText(img, yCoordinateString, (150, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 2)

    cv2.imshow("Tracking",img)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break