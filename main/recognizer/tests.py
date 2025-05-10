from django.test import TestCase

from test_face_detection import test_face_detection
from test_image_upload import test_image_upload

def run_all_tests():
    print("Running Face Detection Tests...")
    test_face_detection()

    print("\nRunning Image Upload Tests...")
    test_image_upload()

if __name__ == "__main__":
    run_all_tests()
