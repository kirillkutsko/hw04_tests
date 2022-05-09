from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import SlugField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post
from .utils import paginator

User = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    """Вернуть HttpResponse объекта главной страницы"""
    post_list = Post.objects.select_related("group")
    page_obj = paginator(request, post_list)
    return render(request, "posts/index.html", {'page_obj': page_obj})


def group_posts(request: HttpRequest, slug: SlugField) -> HttpResponse:
    """Вернуть HttpResponse объекта страницы группы"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related("group", "author")
    page_obj = paginator(request, post_list)
    context = {"group": group, "page_obj": page_obj}
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("group")
    page_obj = paginator(request, post_list)
    context = {
        "author": author,
        "page_obj": page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/post_detail.html', {"post": post})


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post.pk)
    is_edit = True
    context = {
        "form": form,
        "post_id": post_id,
        "is_edit": is_edit,
    }
    return render(
        request,
        "posts/create_post.html",
        context
    )
