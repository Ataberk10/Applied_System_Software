# recognizer/forms.py
from django import forms
from .models import AuthorizedPerson


class AuthorizedPersonForm(forms.ModelForm):
    # Add a dedicated field for the image upload
    face_image = forms.ImageField(
        required=True,
        help_text="Upload a clear, frontal face image.",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = AuthorizedPerson
        fields = ["name", "face_image"]  # 'embedding' will be handled by the view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter full name"}
        )
        self.fields["face_image"].widget.attrs.update({"class": "form-control-file"})
