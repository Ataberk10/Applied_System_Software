# DIP392-TeamRed

For Applied System Software Class

Team Members
* Eymen Ucdal (231ADB006)
* Tufan Yilmaz (231ADB089)
* Ata Mert Pekcan (231ADB010)
* Ali Can Eygay (231ADB027)
* Renas Alp (211ADB112)
* Ataberk Akcin (211AIB121)
* Babak Gasimzade (221ADB125)
# The Face Recognition-Based Access Control System 

This is a Django-powered The Face Recognition-Based Access Control System  application that demonstrates a basic face recognition authentication system. Users can "log in" by presenting their face to the camera. The system also includes features for managing authorized identities and viewing login attempt history. It utilizes the InsightFace library for face detection and recognition.

## Features

*   **Live Camera Feed:** Displays a real-time video stream from the user's webcam.
*   **Face Capture:** Allows capturing a frame from the camera feed upon an "Open Door" command.
*   **Face Recognition:**
    *   Detects faces in the captured frame.
    *   Extracts facial embeddings using InsightFace (buffalo_l model).
    *   Compares captured embeddings against a database of authorized individuals.
*   **Session-Based "Login":** If a recognized face matches an authorized individual, a session is established, granting access to a dashboard.
*   **Dashboard:**
    *   Displays a welcome message.
    *   **Login Attempts Log:** Shows a history of all login attempts, including the captured image, timestamp, authorization status, and recognized person (if any).
    *   **Identity Management:** Allows adding new authorized individuals and removing existing ones.
*   **Identity Management:**
    *   **Add Person:** Upload a clear, frontal face image and associate it with a name. The system extracts and stores the facial embedding.
    *   **Remove Person:** Delete an authorized individual from the system.
*   **Responsive Design (Basic):** Utilizes Bootstrap 5 for improved styling and basic responsiveness.

## Technology Stack

*   **Backend:** Python, Django
*   **Face Recognition:** InsightFace, ONNX Runtime, OpenCV-Python, NumPy
*   **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
*   **Database:** SQLite (default for Django, can be changed)

## Prerequisites

*   Python (3.8 or higher recommended)
*   `pip` (Python package installer)
*   A webcam connected to your computer
*   A modern web browser that supports `getUserMedia` API (e.g., Chrome, Firefox, Edge)

## Setup and Installation

1.  **Clone the Repository (or create project manually):**
    If you have this project in a Git repository:
    ```bash
    git clone <repository-url>
    cd djangofaceid
    ```
    If you followed the step-by-step guide, you already have the project directory (`djangofaceid`).

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    # Navigate to your project directory (e.g., djangofaceid)
    cd djangofaceid

    # Create a virtual environment
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```
    You should see `(venv)` at the beginning of your command prompt.

3.  **Install Dependencies:**
    Create a `requirements.txt` file in your project root with the following content:
    ```txt
    Django>=3.2,<4.3 # Or your specific Django version
    Pillow>=9.0.0
    insightface>=0.7.0
    onnxruntime>=1.10.0 # For CPU. Use onnxruntime-gpu if you have a compatible NVIDIA GPU and CUDA setup.
    numpy>=1.20.0
    opencv-python>=4.5.0
    ```
    Then install the packages:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: The first time InsightFace runs, it will download pre-trained models (e.g., `buffalo_s`). This requires an internet connection and might take a few minutes.*

4.  **Configure Media Files:**
    *   In `faceidproject/settings.py`, ensure `MEDIA_URL` and `MEDIA_ROOT` are set:
        ```python
        MEDIA_URL = '/media/'
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
        ```
    *   Create the `media` directory in your project root (`djangofaceid/media`):
        ```bash
        mkdir media
        cd media
        mkdir captures       # For captured login attempt images
        mkdir profile_pics   # (Optional) If you extend to save profile images for authorized persons
        cd ..
        ```

5.  **Apply Database Migrations:**
    Django uses migrations to set up and update your database schema.
    ```bash
    python manage.py makemigrations recognizer
    python manage.py migrate
    ```

6.  **Create a Superuser (for Admin Panel Access):**
    This allows you to access the Django admin interface to manage data directly.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set a username, email (optional), and password.

## Running the Application

1.  **Ensure your virtual environment is active.**
    ```bash
    # If not active:
    # Windows: venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    ```

2.  **Start the Django Development Server:**
    ```bash
    python manage.py runserver
    ```
    By default, the server will run on `http://127.0.0.1:8000/`.

3.  **Access the Application:**
    Open your web browser and navigate to `http://120.0.0.1:8000/`.
    *   The browser will likely ask for permission to use your camera. **Allow it.**

## Using the Application

1.  **Initial State:** The first page shows the live camera feed and an "Open The Door" button.

2.  **Adding an Authorized Person (First Time):**
    *   Since no one is authorized yet, you'll need to add at least one person to test the login.
    *   **Option 1 (Admin Panel - Manual Embedding - For initial setup if Add Person UI is not yet used):**
        *   Log into the admin panel: `http://127.0.0.1:8000/admin/` with your superuser credentials.
        *   Go to "Recognizer" -> "Authorized persons" -> "Add authorized person +".
        *   Enter a name.
        *   For the "Embedding" field, you'll need to generate a face embedding from an image of the person. You can use the `scripts/generate_embedding.py` script (if you created it as per the tutorial) or a similar method. Paste the JSON list of numbers into this field.
        *   Save the person.
    *   **Option 2 (Using the Add Person UI - Recommended after first login):**
        *   To use this, you need to be "logged in". If this is the very first time, you might need to temporarily bypass the login check for `add_person_view` or log in with a manually added admin user (from Option 1).
        *   Once "logged in" (e.g., as admin), go to the Dashboard -> "Manage Identities" tab.
        *   Click "Add New Person".
        *   Enter the person's name and upload a clear, frontal face image.
        *   Click "Save Person". The system will process the image, extract the embedding, and save the person.

3.  **"Logging In" with Face ID:**
    *   Go to the main page (`http://127.0.0.1:8000/`).
    *   Ensure the face of an authorized person is clearly visible in the camera.
    *   Click the "Open The Door" button.
    *   The system will capture the frame, perform face recognition.
    *   If successful, you'll be redirected to the `/dashboard/`.
    *   If unsuccessful, an "Access Denied" message will appear.

4.  **Dashboard:**
    *   **Login Attempts:** View a list of all login attempts, including the image, timestamp, and outcome.
    *   **Manage Identities:**
        *   See a list of currently authorized individuals.
        *   Add new people using the "Add New Person" button.
        *   Remove existing people using the "Remove" button next to their name (a confirmation prompt will appear).

5.  **Logging Out:**
    Click the "Logout" button on the dashboard to end the session and return to the camera feed page.

## Project Structure
```
djangofaceid/
├── faceidproject/ # Django project configuration
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py # Project settings
│ ├── urls.py # Project-level URL routing
│ └── wsgi.py
├── media/ # For user-uploaded files (captured images, profile pics)
│ └── captures/
├── recognizer/ # Django app for face recognition logic
│ ├── init.py
│ ├── admin.py # Admin panel configuration for models
│ ├── apps.py # App configuration (loads InsightFace model)
│ ├── forms.py # Django forms (e.g., for adding persons)
│ ├── migrations/ # Database migration files
│ ├── models.py # Database models (AuthorizedPerson, LoginAttempt)
│ ├── tests.py # Main test runner script that calls all individual test modules
│ ├── test_face_detection.py # Tests whether the face detection function correctly identifies faces in images
│ ├── test_image_upload.py # Tests if uploaded face images are correctly processed and encoded for recognition
│ ├── templates/ # HTML templates
│ │ └── recognizer/
│ │ ├── add_person.html
│ │ ├── camera_feed.html
│ │ └── dashboard.html
│ ├── urls.py # App-level URL routing
│ ├── views.py # View functions (request handling logic)
│ └── face_analyzer.py # InsightFace model initialization and helper functions
├── scripts/ # (Optional) Utility scripts
│ └── generate_embedding.py
├── manage.py # Django's command-line utility
├── README.md # This file
└── requirements.txt # Python package dependencies
```


## Key Configuration Points

*   **`recognizer/face_analyzer.py`:**
    *   `SIMILARITY_THRESHOLD`: This value in the `compare_faces` function is crucial for recognition accuracy. It may need tuning (0.3 - 0.6 is a common range for cosine similarity with ArcFace models, lower means less strict).
    *   `FaceAnalysis(name='buffalo_l', ...)`: Specifies the InsightFace model used. `providers` can be adjusted for CPU/GPU.
*   **`faceidproject/settings.py`:** Standard Django settings, `MEDIA_ROOT`, `MEDIA_URL`.
*   **Model Download Location:** InsightFace models are typically downloaded to `~/.insightface/models/` (or `%USERPROFILE%\.insightface\models` on Windows).

## Troubleshooting

*   **Camera Not Working:** Ensure your webcam is connected and not being used by another application. Check browser permissions for camera access.
*   **"No face detected"**: Ensure good lighting and a clear view of the face. The image quality might be an issue.
*   **"Access Denied" for an authorized person:**
    *   The `SIMILARITY_THRESHOLD` might be too high (too strict).
    *   The quality of the stored embedding image vs. the live capture might differ significantly. Try re-adding the person with a very clear, well-lit, frontal image.
    *   Check the console for similarity scores printed during comparison (you might need to add print statements for debugging).
*   **InsightFace Model Download Issues:** Ensure you have a stable internet connection when running the app for the first time. Check the console for download progress or errors.
*   **CSRF Errors (403 Forbidden):** Ensure the `csrftoken` is correctly handled in JavaScript POST requests (the provided `getCookie` function and `X-CSRFToken` header should manage this).
*   **Module Not Found Errors:** Ensure all dependencies in `requirements.txt` are installed in your active virtual environment.

## Future Enhancements

*   **Liveness Detection:** Implement anti-spoofing measures to prevent using photos or videos.
*   **Multiple Face Images per User:** Allow uploading several images for each authorized person to create a more robust average embedding.
*   **Error Handling and UX:** More detailed error messages and a smoother user experience.
*   **User Roles and Permissions:** More granular access control for identity management.
*   **Asynchronous Processing:** Offload face recognition to background tasks (e.g., Celery) for better performance under load.
*   **Alternative Face Recognition Models:** Experiment with other models or libraries.
*   **Database Optimization:** For a large number of users, consider vector databases (e.g., FAISS, Milvus) for faster similarity searches.
