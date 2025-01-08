from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


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


from django.http import HttpResponseForbidden


@login_required
def admin_home_view(request):
    if request.user.is_superuser:
        return render(request, "admin/adminhome.html", {"user": request.user})
    else:
        return HttpResponseForbidden("You are not authorized to view this page.")


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


from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Submodule, Video


# List all courses
def course_list(request):
    courses = Course.objects.all()
    return render(request, "admin/courselist.html", {"courses": courses})


# List all courses
def courses(request):
    courses = Course.objects.all()
    return render(request, "course_list.html", {"courses": courses})


def course_normal_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    submodules = course.submodules.all().prefetch_related("videos")
    print(submodules)
    return render(
        request,
        "course_details.html",
        {
            "course": course,
            "submodules": submodules,
        },
    )


# View course details including submodules and videos
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    submodules = course.submodules.all()  # Related submodules
    return render(
        request, "admin/coursedetail.html", {"course": course, "submodules": submodules}
    )


from django.shortcuts import render, redirect
from .models import Course, Submodule, Video


def add_course(request):
    if request.method == "POST":
        try:
            # Basic validation
            title = request.POST.get("title")
            description = request.POST.get("description")
            thumbnail = request.FILES.get("thumbnail")
            print(title)
            if not title or not description or not thumbnail:
                messages.error(request, "All course fields are required.")
                return render(
                    request,
                    "admin/addcourse.html",
                    {"error": "All course fields are required."},
                )

            # Create course
            course = Course.objects.create(
                title=title, description=description, thumbnail=thumbnail
            )
            messages.success(request, "Course created successfully!")
            return redirect("course_list")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(
                request,
                "admin/addcourse.html",
                {"error": f"An error occurred: {str(e)}"},
            )

    return render(request, "admin/addcourse.html")


def course_list(request):
    # Fetch all courses
    courses = Course.objects.all()

    # Render the course list page
    return render(
        request,
        "admin/courselist.html",
        {
            "courses": courses,
        },
    )


def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)  # Fetch the course by id
    submodules = Submodule.objects.filter(course=course)  # Get related submodules

    # Loop through submodules and assign related videos
    for submodule in submodules:
        submodule.videos.set(
            Video.objects.filter(submodule=submodule)
        )  # Use set() method for ManyToMany relationship

    context = {
        "course": course,
        "submodules": submodules,
    }

    return render(request, "admin/coursedetails.html", context)


def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        # Update course details
        course.title = request.POST.get("title")
        course.description = request.POST.get("description")
        if request.FILES.get("thumbnail"):
            course.thumbnail = request.FILES.get("thumbnail")
        course.save()

        # Handle existing submodules
        submodule_ids = request.POST.getlist("submodule_ids[]")
        submodule_titles = request.POST.getlist("submodule_titles[]")
        submodule_descriptions = request.POST.getlist("submodule_descriptions[]")

        for idx, submodule_id in enumerate(submodule_ids):
            try:
                submodule = Submodule.objects.get(id=submodule_id)
                submodule.title = submodule_titles[idx]
                submodule.description = submodule_descriptions[idx]
                submodule.save()

                # Update associated videos
                video_ids = request.POST.getlist(f"video_ids_{submodule_id}[]")
                video_titles = request.POST.getlist(f"video_titles_{submodule_id}[]")
                video_urls = request.POST.getlist(f"video_urls_{submodule_id}[]")
                video_durations = request.POST.getlist(
                    f"video_durations_{submodule_id}[]"
                )

                for vid_idx, video_id in enumerate(video_ids):
                    try:
                        video = Video.objects.get(id=video_id)
                        video.title = video_titles[vid_idx]
                        video.video_url = video_urls[vid_idx]
                        video.duration = (
                            int(video_durations[vid_idx])
                            if video_durations[vid_idx]
                            else 0
                        )
                        video.save()
                    except Video.DoesNotExist:
                        continue

            except Submodule.DoesNotExist:
                continue

        # Handle new submodules and their videos
        new_submodule_titles = request.POST.getlist("new_submodule_titles[]")
        new_submodule_descriptions = request.POST.getlist(
            "new_submodule_descriptions[]"
        )
        new_video_titles = request.POST.getlist("new_video_titles[]")
        new_video_urls = request.POST.getlist("new_video_urls[]")
        new_video_durations = request.POST.getlist("new_video_durations[]")
        new_video_submodule_ids = request.POST.getlist("new_video_submodule_ids[]")

        new_submodules = []
        for idx in range(len(new_submodule_titles)):
            if (
                new_submodule_titles[idx].strip()
                and new_submodule_descriptions[idx].strip()
            ):
                new_submodule = Submodule.objects.create(
                    course=course,
                    title=new_submodule_titles[idx],
                    description=new_submodule_descriptions[idx],
                )
                new_submodules.append(new_submodule)

        for idx in range(len(new_video_titles)):
            if new_video_titles[idx].strip() and new_video_urls[idx].strip():
                try:
                    submodule_id = new_video_submodule_ids[idx]
                    if submodule_id:
                        submodule = Submodule.objects.get(id=submodule_id)
                    else:
                        submodule = (
                            new_submodules[idx // 3]
                            if idx // 3 < len(new_submodules)
                            else None
                        )

                    if submodule:
                        Video.objects.create(
                            submodule=submodule,
                            title=new_video_titles[idx],
                            video_url=new_video_urls[idx],
                            duration=(
                                int(new_video_durations[idx])
                                if new_video_durations[idx]
                                else 0
                            ),
                        )
                except (Submodule.DoesNotExist, IndexError):
                    continue

        return redirect("course_detail", course_id=course.id)

    submodules = Submodule.objects.filter(course=course)
    return render(
        request, "admin/editcourse.html", {"course": course, "submodules": submodules}
    )


import csv
import random
import string
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages


def generate_random_password(length=8):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choices(characters, k=length))


from django.core.mail import send_mail
from django.template.loader import render_to_string


def bulk_register(request):
    if request.method == "POST" and request.FILES["csv_file"]:
        csv_file = request.FILES["csv_file"]
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        errors = []
        for row in reader:
            username = row.get("Username")
            email = row.get("Email")

            if not username or not email:
                errors.append(f"Missing data for user: {row}")
                continue

            # Generate a random password
            password = generate_random_password()

            try:
                # Create user
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )

                # Render HTML email
                html_content = render_to_string(
                    "email_template.html", {"username": username, "password": password}
                )

                # Send email with credentials
                send_mail(
                    subject="Your Account Credentials",
                    message="This is an HTML email. Please use a compatible email client.",
                    from_email="jayarora3100@gmail.com",
                    recipient_list=[email],
                    html_message=html_content,
                )
            except Exception as e:
                errors.append(f"Error creating user {username}: {e}")

        if errors:
            messages.error(request, f"Some errors occurred: {errors}")
        else:
            messages.success(
                request, "Users registered successfully, and emails have been sent!"
            )

        return redirect("bulk_register")

    return render(request, "admin/bulk_register.html")


from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


def user_list(request):
    """Display a list of users with options to edit or delete."""
    users = User.objects.all()
    return render(request, "admin/user_list.html", {"users": users})


def edit_user(request, user_id):
    """Edit user details."""
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


def delete_user(request, user_id):
    """Delete a user."""
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"User {user.username} deleted successfully!")
    return redirect("user_list")


from django.shortcuts import render


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)
