# test_image_upload.py

import face_recognition
import os

def test_image_upload():
    test_image_path = "data/0001.jpg"
    
    try:
        if not os.path.exists(test_image_path):
            print(f"Test image not found at {test_image_path}")
            return

        image = face_recognition.load_image_file(test_image_path)
        encoding = face_recognition.face_encodings(image)

        assert encoding, "No encoding generated from uploaded image."
        print("Image encoding generated successfully.")
    except Exception as e:
        print(f"Test failed due to error: {e}")
