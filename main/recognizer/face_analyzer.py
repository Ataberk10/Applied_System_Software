# recognizer/face_analyzer.py
import insightface
from insightface.app import FaceAnalysis
import numpy as np
import os

# --- Global variable to hold the FaceAnalysis app ---
# This ensures the model is loaded only once.
FACE_APP = None


def initialize_face_analyzer():
    global FACE_APP
    if FACE_APP is None:
        print("Initializing InsightFace FaceAnalysis model...")
        try:
            # Specify the models you want to use. 'buffalo_l' is a good general-purpose model.
            # It includes detection, alignment, recognition.
            # You can specify `providers=['CUDAExecutionProvider', 'CPUExecutionProvider']`
            # if you have GPU and want to prioritize it.
            app = FaceAnalysis(
                name="buffalo_s",
                root=os.path.join(os.path.expanduser("~"), ".insightface"),
                providers=["CPUExecutionProvider"],
            )
            app.prepare(
                ctx_id=0, det_size=(640, 640)
            )  # ctx_id=0 for CPU, det_size for detection model
            FACE_APP = app
            print("InsightFace FaceAnalysis model initialized.")
        except Exception as e:
            print(f"Error initializing InsightFace: {e}")
            # Handle cases where model download might fail or other issues
            raise  # Re-raise the exception to indicate failure
    return FACE_APP


def get_face_analyzer():
    """
    Returns the initialized FaceAnalysis app.
    Initializes it if it hasn't been already.
    """
    if FACE_APP is None:
        return initialize_face_analyzer()
    return FACE_APP


def get_face_embedding(image_np):
    """
    Detects faces in an image and returns the embedding of the first detected face.
    Args:
        image_np (numpy.ndarray): Image in BGR format (as read by cv2.imread).
    Returns:
        numpy.ndarray: Face embedding, or None if no face is detected or error.
    """
    app = get_face_analyzer()
    if app is None:
        print("Face analyzer not available.")
        return None
    try:
        faces = app.get(image_np)  # image_np should be BGR
        if faces and len(faces) > 0:
            # For simplicity, we'll take the first detected face.
            # You might want to select the largest face or handle multiple faces.
            return faces[0].normed_embedding
        else:
            print("No faces detected.")
            return None
    except Exception as e:
        print(f"Error getting face embedding: {e}")
        return None


def compare_faces(embedding1, embedding2, threshold=1.0):  # Adjust threshold as needed
    """
    Compares two face embeddings using cosine similarity.
    InsightFace's `normed_embedding` are L2 normalized, so dot product is cosine similarity.
    A higher value means more similar.
    A common threshold for arcface models (like buffalo_l) is around 0.5-0.6 for verification,
    but distance (1-similarity) is often used.
    Let's use distance and a threshold. distance = 1 - similarity.
    So, if distance < threshold, they are considered a match.
    The `FaceAnalysis.get` method returns faces, and `FaceAnalysis.sim` could also be used
    if you have multiple embeddings. For direct comparison of two embeddings:
    """
    if embedding1 is None or embedding2 is None:
        return False, 0.0

    # Embeddings from insightface are already L2 normalized.
    # Cosine similarity is the dot product.
    similarity = np.dot(embedding1, embedding2)

    # A common practice is to use a distance threshold.
    # For example, if similarity needs to be > 0.5, then distance < 0.5
    # For buffalo_l, a similarity of >0.6 is often a good starting point for a match.
    # Let's define similarity threshold based on common ArcFace metrics.
    # For cosine similarity:
    # threshold_similarity = 0.28 # A low threshold for testing, typically 0.4-0.6 for good matches
    # We are comparing normalized embeddings. The output of np.dot is the cosine similarity.
    # A typical threshold for cosine similarity for face verification is often > 0.5 or > 0.6.
    # Let's set a similarity threshold.
    # Recommended thresholds from InsightFace for buffalo_l (cosine similarity):
    # TAR @ FAR=1e-3: 0.31
    # TAR @ FAR=1e-4: 0.40
    # TAR @ FAR=1e-5: 0.48
    # TAR @ FAR=1e-6: 0.54
    # Let's pick 0.4 as a starting point.
    SIMILARITY_THRESHOLD = 0.40  # You MUST tune this value based on your tests.

    # print(f"Comparing embeddings. Similarity: {similarity:.4f}, Threshold: {SIMILARITY_THRESHOLD}")

    if similarity > SIMILARITY_THRESHOLD:
        return True, similarity  # Match
    else:
        return False, similarity  # No match
