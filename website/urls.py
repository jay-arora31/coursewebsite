from django.urls import path
from .views import *

urlpatterns = [
    path("", home_view, name="home"),  # Home Page
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("adminhome/", admin_home_view, name="adminhome"),  # Admin Home Page
    path("add/", add_course, name="add_course"),  # URL for adding a course
    path(
        "list/", course_list, name="course_list"
    ),  # URL to list all courses (if needed)
    path("delete_course/<int:course_id>/", delete_course, name="delete_course"),
    path("courses/", courses, name="courses"),
    path("courses/<int:course_id>/", course_detail, name="course_detail"),
    path("course-detail/<int:course_id>/", course_normal_detail, name="course_details"),
    path("courseedit/<int:course_id>/", edit_course, name="edit_course"),
    path(
        "reorder_submodule_video/<int:course_id>/",
        reorder_submodule_video,
        name="reorder_submodule_video",
    ),
    path("bulk-upload/", bulk_register, name="bulk_register"),
    path("users/", user_list, name="user_list"),
    path("users/edit/<int:user_id>/", edit_user, name="edit_user"),
    path("users/delete/<int:user_id>/", delete_user, name="delete_user"),
    path("privacy/", privacy, name="privacy"),
    path("term/", term, name="term"),
    path("refund/", refund, name="refund"),
    path(
        "submodule/<int:submodule_id>/delete/",
        delete_submodule,
        name="delete_submodule",
    ),
    path("video/<int:video_id>/delete/", delete_video, name="delete_video"),
    path("change-password/", change_password, name="change_password"),
]

from django.conf.urls import handler404
from website.views import custom_404_view  # Replace `website` with your app name

handler404 = custom_404_view
