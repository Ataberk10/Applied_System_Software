# scripts/generate_embedding.py (create this file in your project root, e.g., djangofaceid/scripts/)
import cv2
import sys
import os

# Add project root to Python path to import face_analyzer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from recognizer.face_analyzer import (
    initialize_face_analyzer,
    get_face_embedding,
)  # Ensure correct import path
import numpy as np
import json


def main(image_path, output_json_path=None):
    # Initialize the analyzer (this will also download models if needed)
    try:
        analyzer = initialize_face_analyzer()
        if not analyzer:
            print("Failed to initialize face analyzer.")
            return
    except Exception as e:
        print(f"Error during initialization: {e}")
        return

    if not os.path.exists(image_path):
        print(f"Image path not found: {image_path}")
        return

    # Load the image using OpenCV
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print(f"Could not read image: {image_path}")
        return

    # Get embedding
    embedding = get_face_embedding(img_bgr)

    if embedding is not None:
        embedding_list = embedding.tolist()  # Convert numpy array to list for JSON
        print("Generated Embedding (first 10 values):", embedding_list[:10])
        print("Embedding shape:", embedding.shape)  # Should be (512,) for buffalo_l

        if output_json_path:
            with open(output_json_path, "w") as f:
                json.dump(embedding_list, f)
            print(f"Embedding saved to {output_json_path}")
        return embedding_list
    else:
        print("No embedding generated. No face detected or error occurred.")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python scripts/generate_embedding.py <path_to_image_file> [output_json_file]"
        )
    else:
        image_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        main(image_file, output_file)
