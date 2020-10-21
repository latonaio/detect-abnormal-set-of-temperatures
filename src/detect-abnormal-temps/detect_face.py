import sys
import cv2
from aion.logger import lprint

face_cascade_path = '/var/lib/aion/Runtime/detect-abnormal-set-of-temperatures/config/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)


def max_face(faces):
    if len(faces) <= 0:
        return None
    elif len(faces) == 1:
        return faces[0]
    mface = faces[0]
    for f in faces[1:]:
        _, _, w, h = mface
        size = w * h
        _, _, w, h = f
        if (size < w * h):
            mface = f
    return mface


def detect_face_area(image):
    src = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if src is not None:
        faces = face_cascade.detectMultiScale(src)
        lprint(f'found face: {len(faces)}')
        face = max_face(faces)
        if face is None:
            return (None, None)

        x, y, w, h = face
        return (x, y), (x + w, y + h)
