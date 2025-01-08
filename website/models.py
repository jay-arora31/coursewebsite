from django.db import models

# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="course_thumbnails/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Submodule(models.Model):
    course = models.ForeignKey(Course, related_name="submodules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Video(models.Model):
    submodule = models.ForeignKey(Submodule, related_name="videos", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    duration = models.PositiveIntegerField(help_text="Duration in seconds", null=True, blank=True)

    def __str__(self):
        return f"{self.submodule.title} - {self.title}"