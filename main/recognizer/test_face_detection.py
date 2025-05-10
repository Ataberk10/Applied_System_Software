# test_face_detection.py

import face_recognition
import cv2

def test_face_detection():
    try:
        image = face_recognition.load_image_file("data/0001.jpg")
        face_locations = face_recognition.face_locations(image)

        assert len(face_locations) > 0, " No face detected in test image!"
        print("Face detected successfully in test image.")
    except Exception as e:
        print(f"Test failed due to error: {e}")
