import cv2

def getVideoShape(path):
    vcap = cv2.VideoCapture(path)

    if vcap.isOpened():
        return (
            int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )
    else:
        return None