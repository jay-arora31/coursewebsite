from django.contrib import admin
from .models import Course, Submodule, Video

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ('title', 'video_url', 'duration')


class SubmoduleInline(admin.TabularInline):
    model = Submodule
    extra = 1
    fields = ('title', 'description')
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('created_at',)
    inlines = [SubmoduleInline]
    fieldsets = (
        (None, {
            "fields": ("title", "description", "thumbnail"),
        }),
    )


@admin.register(Submodule)
class SubmoduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    inlines = [VideoInline]
    fieldsets = (
        (None, {
            "fields": ("course", "title", "description"),
        }),
    )


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'submodule', 'duration')
    search_fields = ('title', 'submodule__title')
    list_filter = ('submodule',)
    fieldsets = (
        (None, {
            "fields": ("submodule", "title", "video_url", "duration"),
        }),
    )
