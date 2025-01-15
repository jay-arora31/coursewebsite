# Add to models.py
from django.db import models

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
    order = models.IntegerField(default=0)  # Add this field

    class Meta:
        ordering = ['order']  # Add this to maintain order

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Video(models.Model):
    submodule = models.ForeignKey(Submodule, related_name="videos", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.CharField(max_length=100, help_text="The Wistia media ID (e.g., 'nheca4ikpw')")
    duration = models.PositiveIntegerField(help_text="Duration in seconds", null=True, blank=True)
    order = models.IntegerField(default=0)  # Add this field
    wistia_id = models.CharField(max_length=100, help_text="The Wistia media ID (e.g., 'nheca4ikpw')")


    class Meta:
        ordering = ['order']  # Add this to maintain order
    class Meta:
        ordering = ['order']
    
    @property
    def embed_script(self):
        return f'<script src="https://fast.wistia.com/embed/medias/{self.video_url}.jsonp" async></script>'
    
    @property
    def player_script(self):
        return '<script src="https://fast.wistia.com/assets/external/E-v1.js" async></script>'
    
    @property
    def embed_code(self):
        return f'<div class="wistia_responsive_padding" style="padding:56.25% 0 0 0;position:relative;">' \
               f'<div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;">' \
               f'<div class="wistia_embed wistia_async_{self.video_url} videoFoam=true" style="height:100%;position:relative;width:100%">' \
               f'<div class="wistia_swatch" style="height:100%;left:0;opacity:0;overflow:hidden;position:absolute;top:0;transition:opacity 200ms;width:100%;">' \
               f'<img src="https://fast.wistia.com/embed/medias/{self.video_url}/swatch" style="filter:blur(5px);height:100%;object-fit:contain;width:100%;" alt="" aria-hidden="true" onload="this.parentNode.style.opacity=1;" />' \
               f'</div></div></div></div>'
    def __str__(self):
        return f"{self.submodule.title} - {self.title}"