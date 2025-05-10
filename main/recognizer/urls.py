# recognizer/urls.py
from django.urls import path
from . import views

app_name = "recognizer"  # Good practice for namespacing

urlpatterns = [
    path("", views.camera_feed_view, name="camera_feed"),
    path("process_frame/", views.process_frame_view, name="process_frame"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("login_attempts/", views.login_attempts_view, name="login_attempts"),
    path("logout/", views.logout_view, name="logout"),
    path("identities/add/", views.add_person_view, name="add_person"),
    path(
        "identities/remove/<int:person_id>/",
        views.remove_person_view,
        name="remove_person",
    ),
]
