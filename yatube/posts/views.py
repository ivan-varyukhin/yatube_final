﻿from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect

from django.conf import settings

from posts.models import Post, Group, User

from posts.forms import PostForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_LIMIT)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    post_list = group.posts.all()

    paginator = Paginator(post_list, settings.POSTS_LIMIT)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'group': group,
        'title': str(group),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)

    post_list = (
        Post.objects.select_related("author", "group")
        .filter(author=profile)
        .all()
    )

    paginator = Paginator(post_list, settings.POSTS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    posts_count = post_list.count()

    context = {
        'profile': profile,
        'page_obj': page_obj,
        'paginator': paginator,
        'posts_count': posts_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_title = str(post)
    context = {
        'author': post.author,
        'post': post,
        'post_title': post_title,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    form = PostForm()
    context = {
        'form': form,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, "posts/create_post.html", context)