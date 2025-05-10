from django.db import models
from django.conf import settings
import os
import json
# Create your models here.


class AuthorizedPerson(models.Model):
    name = models.CharField(max_length=100)
    # Storing embeddings as a JSON string of a list of floats
    # For multiple face images per person, this could be a list of embeddings.
    # For simplicity now, one embedding per person.
    embedding = models.TextField(blank=True, null=True)  # Store as JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # You might add a profile image later:
    # profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.name

    def set_embedding(self, embedding_list):
        self.embedding = json.dumps(embedding_list)

    def get_embedding(self):
        if self.embedding:
            return json.loads(self.embedding)
        return None


class LoginAttempt(models.Model):
    # Use FileField to store the path relative to MEDIA_ROOT
    captured_image = models.FileField(upload_to="captures/")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_authorized = models.BooleanField(default=False)
    recognized_person = models.ForeignKey(
        AuthorizedPerson,
        on_delete=models.SET_NULL,  # If person is deleted, keep log but set person to NULL
        null=True,
        blank=True,
    )
    details = models.TextField(
        blank=True, null=True
    )  # For storing any extra info/errors

    def __str__(self):
        return f"Attempt at {self.timestamp} - Authorized: {self.is_authorized}"

    # Property to get the full URL of the image
    @property
    def image_url(self):
        if self.captured_image and hasattr(self.captured_image, "url"):
            return self.captured_image.url
        return None
