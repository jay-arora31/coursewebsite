from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from .forms import RegisterForm
from .models import Course, Submodule, Video
import csv
import random
import string

def is_superuser(user):
    return user.is_superuser
@login_required
@user_passes_test(is_superuser)
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

@login_required
@user_passes_test(is_superuser)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course_title = course.title
    course.delete()
    messages.success(request, f"The course '{course_title}' has been successfully deleted.")
    return redirect('course_list')

@login_required
@user_passes_test(is_superuser)
def admin_home_view(request):
    total_courses = Course.objects.count()
    total_users = User.objects.count()
    total_videos = Video.objects.count()
    total_submodules = Submodule.objects.count()

    context = {
        "total_courses": total_courses,
        "total_users": total_users,
        "total_videos": total_videos,
        "total_submodules": total_submodules,
    }
    return render(request, "admin/adminhome.html", context)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect("adminhome")  # Redirect to admin dashboard
            else:
                return redirect("home")  # Redirect to user dashboard
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "home.html", {"user": request.user})

def home_view(request):
    return render(request, "home.html", {"user": request.user})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")

@login_required
@user_passes_test(is_superuser)
def course_list(request):
    courses = Course.objects.all()
    return render(request, "admin/courselist.html", {"courses": courses})

@login_required
def courses(request):
    courses = Course.objects.all()
    return render(request, "course_list.html", {"courses": courses})

@login_required(login_url='/login/')
def course_normal_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    submodules = course.submodules.all().prefetch_related("videos")
    return render(
        request,
        "course_details.html",
        {
            "course": course,
            "submodules": submodules,
        },
    )

@login_required(login_url='/login/')
@user_passes_test(is_superuser)
def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    submodules = Submodule.objects.filter(course=course)
    for submodule in submodules:
        submodule.videos.set(Video.objects.filter(submodule=submodule))
    context = {
        "course": course,
        "submodules": submodules,
    }
    return render(request, "admin/coursedetails.html", context)

@login_required
@user_passes_test(is_superuser)
def add_course(request):
    if request.method == "POST":
        try:
            title = request.POST.get("title")
            description = request.POST.get("description")
            thumbnail = request.FILES.get("thumbnail")
            if not title or not description or not thumbnail:
                messages.error(request, "All course fields are required.")
                return render(request, "admin/addcourse.html", {"error": "All course fields are required."})
            course = Course.objects.create(title=title, description=description, thumbnail=thumbnail)
            messages.success(request, "Course created successfully!")
            return redirect("course_list")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "admin/addcourse.html", {"error": f"An error occurred: {str(e)}"})
    return render(request, "admin/addcourse.html")

@login_required
@user_passes_test(is_superuser)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.title = request.POST.get("title")
        course.description = request.POST.get("description")
        if request.FILES.get("thumbnail"):
            course.thumbnail = request.FILES.get("thumbnail")
        course.save()
        submodule_ids = request.POST.getlist("submodule_ids[]")
        submodule_titles = request.POST.getlist("submodule_titles[]")
        submodule_descriptions = request.POST.getlist("submodule_descriptions[]")
        for idx, submodule_id in enumerate(submodule_ids):
            try:
                submodule = Submodule.objects.get(id=submodule_id)
                submodule.title = submodule_titles[idx]
                submodule.description = submodule_descriptions[idx]
                submodule.save()
                video_ids = request.POST.getlist(f"video_ids_{submodule_id}[]")
                video_titles = request.POST.getlist(f"video_titles_{submodule_id}[]")
                video_urls = request.POST.getlist(f"video_urls_{submodule_id}[]")
                video_durations = request.POST.getlist(f"video_durations_{submodule_id}[]")
                for vid_idx, video_id in enumerate(video_ids):
                    if video_id:
                        try:
                            video = Video.objects.get(id=video_id)
                            video.title = video_titles[vid_idx]
                            video.video_url = video_urls[vid_idx]
                            video.duration = int(video_durations[vid_idx]) if video_durations[vid_idx] else 0
                            video.save()
                        except Video.DoesNotExist:
                            continue
                    else:
                        Video.objects.create(
                            submodule=submodule,
                            title=video_titles[vid_idx],
                            video_url=video_urls[vid_idx],
                            duration=int(video_durations[vid_idx]) if video_durations[vid_idx] else 0
                        )
            except Submodule.DoesNotExist:
                continue
        new_submodule_titles = request.POST.getlist("new_submodule_titles[]")
        new_submodule_descriptions = request.POST.getlist("new_submodule_descriptions[]")
        new_submodule_map = {}
        for idx, title in enumerate(new_submodule_titles):
            if title.strip() and new_submodule_descriptions[idx].strip():
                new_submodule = Submodule.objects.create(
                    course=course,
                    title=title,
                    description=new_submodule_descriptions[idx]
                )
                new_submodule_map[f'new-{idx}'] = new_submodule
        new_video_titles = request.POST.getlist("new_video_titles[]")
        new_video_urls = request.POST.getlist("new_video_urls[]")
        new_video_durations = request.POST.getlist("new_video_durations[]")
        new_video_submodule_ids = request.POST.getlist("new_video_submodule_ids[]")
        for idx, title in enumerate(new_video_titles):
            if title.strip() and new_video_urls[idx].strip():
                submodule_id = new_video_submodule_ids[idx]
                if submodule_id.startswith('new-') and submodule_id in new_submodule_map:
                    submodule = new_submodule_map[submodule_id]
                    Video.objects.create(
                        submodule=submodule,
                        title=title,
                        video_url=new_video_urls[idx],
                        duration=int(new_video_durations[idx]) if new_video_durations[idx] else 0
                    )
        return redirect("course_detail", course_id=course.id)
    submodules = Submodule.objects.filter(course=course)
    return render(request, "admin/editcourse.html", {"course": course, "submodules": submodules})

import hashlib

def generate_password_based_on_email(email, length=8):
    # Create a hash of the email
    hash_object = hashlib.md5(email.encode())
    hashed_email = hash_object.hexdigest()
    
    # Take the first 'length' characters from the hashed email
    password = hashed_email[:length]
    
    return password

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
import csv

@login_required
@user_passes_test(is_superuser)
def bulk_register(request):
    if request.method == "POST" and request.FILES["csv_file"]:
        csv_file = request.FILES["csv_file"]
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)
        errors = []
        for row in reader:
            name = row.get("name")
            username = row.get("email")
            email = row.get("email")
            if not username or not email:
                errors.append(f"Missing data for user: {row}")
                continue
            password = generate_password_based_on_email(email)
            try:
                user = User.objects.create_user(first_name=name,username=username, email=email, password=password)
                # Customize the email content
                html_content = render_to_string("email_template.html", {"name":name,"username": username, "password": password})
                send_mail(
                    subject="Your Account Credentials",
                    message="Please use a compatible email client to view your credentials.",
                    from_email="jayarora3100@gmail.com",
                    recipient_list=[email],
                    html_message=html_content,
                )
            except Exception as e:
                errors.append(f"Error creating user {username}: {e}")
        if errors:
            messages.error(request, f"Some errors occurred: {errors}")
        else:
            messages.success(request, "Users registered successfully, and emails have been sent!")
        return redirect("bulk_register")
    return render(request, "admin/bulk_register.html")

@login_required
@user_passes_test(is_superuser)
def user_list(request):
    users = User.objects.all()
    return render(request, "admin/user_list.html", {"users": users})

@login_required
@user_passes_test(is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.save()
        messages.success(request, f"User {user.username} updated successfully!")
        return redirect("user_list")
    return render(request, "admin/edit_user.html", {"user": user})

@login_required
@user_passes_test(is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"User {user.username} deleted successfully!")
    return redirect("user_list")

def custom_404_view(request, exception):
    return render(request, "404.html", status=404)

@require_POST
@login_required
@user_passes_test(is_superuser)
def delete_submodule(request, submodule_id):
    try:
        submodule = get_object_or_404(Submodule, id=submodule_id)
        course_id = submodule.course.id
        submodule.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Submodule deleted successfully',
            'course_id': course_id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_POST
@login_required
@user_passes_test(is_superuser)
def delete_video(request, video_id):
    try:
        video = get_object_or_404(Video, id=video_id)
        submodule_id = video.submodule.id
        video.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Video deleted successfully',
            'submodule_id': submodule_id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@user_passes_test(is_superuser)
def reorder_submodule_video(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        try:
            submodule_order = request.POST.getlist("submodule_order[]")
            for index, submodule_id in enumerate(submodule_order):
                submodule = Submodule.objects.get(id=submodule_id, course=course)
                submodule.order = index
                submodule.save()
            for submodule in course.submodules.all():
                video_order = request.POST.getlist(f"video_order_{submodule.id}[]")
                for index, video_id in enumerate(video_order):
                    video = Video.objects.get(id=video_id, submodule=submodule)
                    video.order = index
                    video.save()
            messages.success(request, "Order updated successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        return redirect("course_detail", course_id=course.id)
    submodules = Submodule.objects.filter(course=course).order_by("order")
    return render(request, "admin/reorder.html", {"course": course, "submodules": submodules})
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib import messages
@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not check_password(current_password, request.user.password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('home')
        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('home')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('home')
        
        request.user.set_password(new_password1)
        request.user.save()
        
        messages.success(request, 'Password changed successfully.')
        return redirect('home')
    
    return redirect('home')



def privacy(request):
    return  render(request,'privacy.html')

def term(request):
    return  render(request,'term.html')


def refund(request):
    return  render(request,'refund.html')



def contact(request):
    return  render(request,'contact.html')



def about(request):
    return  render(request,'about.html')