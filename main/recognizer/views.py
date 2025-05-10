import base64
import os
import uuid  # To generate unique filenames

import cv2  # For OpenCV
import numpy as np
from django.conf import settings
from django.contrib import messages  # For displaying messages
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone  # For timestamps
from django.views.decorators.csrf import csrf_exempt

from .face_analyzer import compare_faces, get_face_analyzer, get_face_embedding
from .forms import AuthorizedPersonForm
from .models import AuthorizedPerson, LoginAttempt


# Create your views here.
def camera_feed_view(request):
    if request.session.get("is_face_logged_in"):
        return redirect(
            "recognizer:dashboard"
        )  # Redirect to dashboard if already "logged in"
    return render(request, "recognizer/camera_feed.html")


@csrf_exempt  # Temporarily disable CSRF for testing, OR ensure JS sends token
def process_frame_view(request):
    if request.method == "POST":
        image_data_url = request.POST.get("image_data")
        if not image_data_url:
            return JsonResponse(
                {"status": "error", "message": "No image data received."}, status=400
            )

        try:
            # Decode the base64 image data
            format, imgstr = image_data_url.split(";base64,")
            ext = format.split("/")[-1]
            image_bytes = base64.b64decode(imgstr)

            # Convert bytes to OpenCV image (numpy array)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Reads in BGR format

            if img_cv is None:
                return JsonResponse(
                    {"status": "error", "message": "Could not decode image."},
                    status=400,
                )

            # --- Face Recognition Logic ---
            # Initialize analyzer (it's a singleton, safe to call)
            face_analyzer_app = get_face_analyzer()
            if not face_analyzer_app:
                LoginAttempt.objects.create(
                    details="Face analyzer not available during attempt."
                )
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Face recognition service not available.",
                    },
                    status=500,
                )

            current_embedding_np = get_face_embedding(
                img_cv
            )  # This uses the global FACE_APP

            recognized_person_obj = None
            is_authorized_attempt = False
            match_details = "No face detected or no match found."
            similarity_score = 0.0

            if current_embedding_np is not None:
                authorized_persons = AuthorizedPerson.objects.filter(
                    embedding__isnull=False
                ).exclude(embedding__exact="")

                best_match_person = None
                highest_similarity = -1  # Cosine similarity ranges from -1 to 1

                for person in authorized_persons:
                    stored_embedding_list = person.get_embedding()
                    if stored_embedding_list:
                        stored_embedding_np = np.array(stored_embedding_list)
                        # Perform comparison
                        match, current_sim = compare_faces(
                            current_embedding_np, stored_embedding_np
                        )
                        if match and current_sim > highest_similarity:
                            highest_similarity = current_sim
                            best_match_person = person

                if best_match_person:
                    is_authorized_attempt = True
                    recognized_person_obj = best_match_person
                    match_details = f"Recognized: {best_match_person.name} (Similarity: {highest_similarity:.4f})"
                    similarity_score = (
                        highest_similarity  # Store this for logging perhaps
                    )
                else:
                    match_details = "Face detected, but no authorized match found."
                    if highest_similarity > -1:  # A face was detected and compared
                        match_details += (
                            f" (Highest similarity to known: {highest_similarity:.4f})"
                        )

            else:  # No face detected by get_face_embedding
                match_details = "No face detected in the captured image."

            # --- Save the captured image as a FileField for the LoginAttempt ---
            # Generate a unique filename
            capture_filename = f"capture_{uuid.uuid4()}.{ext}"

            # Create a ContentFile for the Django FileField
            django_file = ContentFile(image_bytes, name=capture_filename)

            # Create LoginAttempt record
            login_attempt = LoginAttempt.objects.create(
                captured_image=django_file,  # This will save to MEDIA_ROOT/captures/
                is_authorized=is_authorized_attempt,
                recognized_person=recognized_person_obj,
                details=match_details,
            )

            print(f"Login attempt logged: {match_details}")

            if is_authorized_attempt:
                # For now, just a message. Later, we'll handle actual login session.
                # Set a session variable to indicate "login"
                request.session["is_face_logged_in"] = True
                request.session["logged_in_user_name"] = recognized_person_obj.name
                request.session.set_expiry(3600)  # e.g., 1 hour session

                return JsonResponse(
                    {
                        "status": "success",
                        "message": f"Welcome, {recognized_person_obj.name}! Access granted.",
                        "redirect_url": "/dashboard/",  # We will create this URL and view next
                    }
                )
            else:
                return JsonResponse(
                    {"status": "failure", "message": f"Access Denied. {match_details}"}
                )

        except Exception as e:
            import traceback

            print(f"Error processing frame: {e}\n{traceback.format_exc()}")
            # Log an attempt with error if possible
            LoginAttempt.objects.create(details=f"Error during processing: {e}")
            return JsonResponse(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=500,
            )

    return JsonResponse(
        {"status": "error", "message": "Invalid request method."}, status=405
    )


def dashboard_view(request):
    if not request.session.get("is_face_logged_in"):
        # If not "logged in" via face, redirect to the camera feed page
        return redirect("recognizer:camera_feed")

    user_name = request.session.get("logged_in_user_name", "User")

    # Fetch login attempts for the "Login Attempts" tab
    login_attempts_list = LoginAttempt.objects.all().order_by("-timestamp")[
        :50
    ]  # Get latest 50

    # Fetch authorized persons for the "Manage Identities" tab (preview)
    authorized_persons_list = AuthorizedPerson.objects.all().order_by("name")

    context = {
        "user_name": user_name,
        "attempts": login_attempts_list,
        "authorized_persons": authorized_persons_list,
    }
    return render(request, "recognizer/dashboard.html", context)


def logout_view(request):
    # Clear session data related to face login
    if "is_face_logged_in" in request.session:
        del request.session["is_face_logged_in"]
    if "logged_in_user_name" in request.session:
        del request.session["logged_in_user_name"]
    # request.session.flush() # Alternatively, to clear the entire session

    return redirect("recognizer:camera_feed")


def login_attempts_view(request):
    # if not request.session.get('is_face_logged_in'):
    #     return redirect('recognizer:camera_feed')
    # attempts = LoginAttempt.objects.all().order_by('-timestamp')
    # return render(request, 'recognizer/login_attempts.html', {'attempts': attempts})
    return JsonResponse({"message": "Login attempts placeholder - to be implemented"})


def add_person_view(request):
    if not request.session.get("is_face_logged_in"):  # Or check for admin/staff status
        return redirect("recognizer:camera_feed")

    if request.method == "POST":
        form = AuthorizedPersonForm(request.POST, request.FILES)
        if form.is_valid():
            person_name = form.cleaned_data["name"]
            uploaded_image = form.cleaned_data["face_image"]

            try:
                # Convert uploaded image to OpenCV format
                image_bytes = uploaded_image.read()
                nparr = np.frombuffer(image_bytes, np.uint8)
                img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img_cv is None:
                    messages.error(
                        request,
                        "Could not process the uploaded image. Please try a different image.",
                    )
                    return render(request, "recognizer/add_person.html", {"form": form})

                # Get face embedding
                face_analyzer_app = get_face_analyzer()
                if not face_analyzer_app:
                    messages.error(
                        request,
                        "Face recognition service is not available. Cannot process image.",
                    )
                    return render(request, "recognizer/add_person.html", {"form": form})

                embedding = get_face_embedding(img_cv)

                if embedding is not None:
                    # Create and save the AuthorizedPerson instance
                    new_person = AuthorizedPerson(name=person_name)
                    new_person.set_embedding(embedding.tolist())  # Store as list
                    # You might want to save the profile image itself too
                    # new_person.profile_image = uploaded_image # If you have such a field
                    new_person.save()
                    messages.success(
                        request,
                        f"Successfully added {person_name} with their face profile.",
                    )
                    return redirect(
                        "recognizer:dashboard"
                    )  # Redirect to dashboard, perhaps to manage-identities tab
                else:
                    messages.error(
                        request,
                        "No face detected in the uploaded image, or an error occurred. Please use a clear, frontal face image.",
                    )

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                print(f"Error adding person: {e}")
        # else:
        # Form is not valid, errors will be displayed by the template
        # messages.error(request, "Please correct the errors below.")

    else:  # GET request
        form = AuthorizedPersonForm()

    return render(request, "recognizer/add_person.html", {"form": form})


def remove_person_view(request, person_id):
    if not request.session.get("is_face_logged_in"):  # Or check for admin/staff status
        return redirect("recognizer:camera_feed")

    try:
        person = AuthorizedPerson.objects.get(id=person_id)
        person_name = person.name

        # You might want to add a confirmation step here in a real app
        if request.method == "POST":  # Ensure it's a POST request for deletion
            person.delete()
            messages.success(request, f"Successfully removed {person_name}.")
            return redirect(
                "recognizer:dashboard"
            )  # Or redirect back to the manage identities tab
        else:
            # If GET, perhaps redirect or show an error, or display a confirmation page
            # For this setup, we redirect as the form in template handles POST
            messages.warning(request, "Removal must be done via POST request.")
            return redirect("recognizer:dashboard")
        # For GET request, show a confirmation page or just redirect if no confirmation page
        # For simplicity, we'll make it POST-only for actual deletion via a link acting as a form submit (less ideal)
        # A better way is a confirmation page with a POST form.
        # However, the link in dashboard.html implies a GET request for removal.
        # Let's allow GET for removal for simplicity here, but note it's not best practice.

        person.delete()  # If allowing GET for delete (simpler for now)
        messages.success(request, f"Successfully removed {person_name}.")
        return redirect("recognizer:dashboard")

    except AuthorizedPerson.DoesNotExist:
        messages.error(request, "Person not found.")
        return redirect("recognizer:dashboard")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("recognizer:dashboard")

    # If you want a confirmation page for GET:
    # return render(request, 'recognizer/confirm_remove_person.html', {'person': person})
