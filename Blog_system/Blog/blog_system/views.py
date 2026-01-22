from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from .models import Post,Comment
from .forms import PostForm, CommentForm

@login_required
def index(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "index.html", {"posts": posts})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related("user").order_by("-created_at")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect("post_detail", pk=post.pk)
    else:
        comment_form = CommentForm()

    return render(
        request,
        "post_detail.html",
        {"post": post, "comments": comments, "comment_form": comment_form},
    )

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
            post.author = request.user 
            post.save()
            form.save_m2m()
            return redirect("index")
    else:
        form = PostForm()

    return render(request, "post_form.html", {"form": form, "mode": "create"})

@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)

    
    if post.author != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = PostForm(instance=post)

    return render(request, "post_form.html", {"form": form, "mode": "edit", "post": post})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user  and not  request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        post.delete()
        return redirect("index")

    return render(request, "post_confirm_delete.html", {"post": post})

@login_required
def comment_delete(request, post_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk, post_id=post_pk)

    if comment.user != request.user  and not  request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        comment.delete()
        return redirect("post_detail", pk=post_pk)

    return render(request, "comment_confirm_delete.html", {"comment": comment})
