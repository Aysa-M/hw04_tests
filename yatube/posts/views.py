from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from .forms import PostForm
from .models import Group, Post

count_per_page = settings.COUNT_PER_PAGE
LETTERS_FOR_TITLE = 30


def index(request):
    """Information which is showing up on the start page."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, count_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Information for displaying on the page with posts grouped by GROUPS."""
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).all()
    paginator = Paginator(post_list, count_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """
    The view shows a page profile of an authorised user.
    """
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).all()
    paginator = Paginator(post_list, count_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_quantity = post_list.count()
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_quantity': post_quantity,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """The view shows information about a current post."""
    post_profile = get_object_or_404(Post, pk=post_id)
    title = post_profile.text[:LETTERS_FOR_TITLE]
    context = {
        'post_profile': post_profile,
        'title': title,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """The view creates a new post by a special form."""
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', username=new_post.author)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """
    This view edits the post by its id and saves changes in database.
    """
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    if author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)
    is_edit = True
    context = {
        'form': form,
        'is_edit': is_edit,
    }

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)
