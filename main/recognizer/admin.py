from django.contrib import admin
from .models import AuthorizedPerson, LoginAttempt
from django.utils.html import format_html


# Register your models here.
class AuthorizedPersonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
        "has_embedding_display",
    )  # 'profile_image_thumb'
    # If you add profile_image to the model:
    # fields = ('name', 'profile_image', 'profile_image_display', 'embedding_display')
    # readonly_fields = ('profile_image_display', 'embedding_display')
    fields = ("name", "embedding_display")  # Keep it simple for now
    readonly_fields = ("embedding_display",)

    def has_embedding_display(self, obj):
        return bool(obj.embedding)

    has_embedding_display.boolean = True
    has_embedding_display.short_description = "Has Embedding"

    def embedding_display(self, obj):
        if obj.embedding:
            emb = obj.get_embedding()
            return f"Vector (Length: {len(emb)})" if emb else "Not Set"
        return "Not Set"

    embedding_display.short_description = "Face Embedding Data"


class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "is_authorized", "recognized_person", "image_thumb")
    list_filter = ("is_authorized", "timestamp")
    readonly_fields = ("image_thumb_display", "details_multiline")

    def image_thumb(self, obj):
        if obj.captured_image:
            return format_html(
                '<img src="{}" width="50" height="50" />', obj.captured_image.url
            )
        return "No Image"

    image_thumb.short_description = "Captured"

    def image_thumb_display(self, obj):
        if obj.captured_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.captured_image.url,
            )
        return "No Image"

    image_thumb_display.short_description = "Captured Image"

    def details_multiline(self, obj):
        return format_html("<pre>{}</pre>", obj.details)

    details_multiline.short_description = "Details"


admin.site.register(AuthorizedPerson, AuthorizedPersonAdmin)
admin.site.register(LoginAttempt, LoginAttemptAdmin)
