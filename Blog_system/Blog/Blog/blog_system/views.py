from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from .models import Post
from .forms import PostForm


def index(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "index.html", {"posts": posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "post_detail.html", {"post": post})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user   # tie post to logged-in user
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()

    return render(request, "post_form.html", {"form": form, "mode": "create"})

@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Only the author can edit
    if post.author != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, "post_form.html", {"form": form, "mode": "edit", "post": post})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        raise PermissionDenied

    if request.method == "POST":
        post.delete()
        return redirect("index")

    return render(request, "post_confirm_delete.html", {"post": post})
