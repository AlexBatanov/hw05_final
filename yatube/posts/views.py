from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Comment, Follow
from .constants import POSTS_LIMIT
from .forms import PostForm, CommentForm
from .utils import get_page_obj


@cache_page(20, key_prefix='index_page')
def index(request):
    '''Сортирует по дате и возвращает LIMIT обЪектов модели Post'''

    posts = Post.objects.select_related('author')

    context = {
        'page_obj': get_page_obj(request, posts, POSTS_LIMIT),
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''
    Проверяет наличие группы.
    возвращает LIMIT обЪектов модели Post
    принадлежащих заданной группе.
    '''

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    context = {
        'page_obj': get_page_obj(request, posts, POSTS_LIMIT),
        'group': group,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    '''
    Возвращает посты выбранного автора
    '''

    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)

    following = False
    if request.user.is_authenticated:
        following = bool(
            Follow.objects.filter(user=request.user).filter(author=author)
        )

    context = {
        'author': author,
        'page_obj': get_page_obj(request, posts, POSTS_LIMIT),
        'following': following
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''
    Возвращает выбранный пост.
    Автора поста и колтчесво постов автора
    '''

    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm(request.POST or None)

    context = {
        'post': post,
        'comments': comments,
        'form': form
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''
    Выводит форму для создания нового поста.
    при валидном заполнении переадресовывает на post_detail.
    добавляет в бд
    '''

    form = PostForm(request.POST or None)

    if form.is_valid():
        user = request.user
        post = form.save(commit=False)
        post.author = user
        post.save()

        return redirect('posts:profile', user)

    context = {
        'form': form,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    '''
    Возвращает заполненую форму поста автора для редактирования.
    сохраняет изменния в бд.
    изменяет вывод шаблона create_post.html
    '''

    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    if form.is_valid():
        form.save()

        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': True,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = get_object_or_404(User, pk=request.user.id)

    authors = []
    for follow in Follow.objects.filter(user=user):
        authors.append(follow.author)

    posts = Post.objects.filter(author__in=authors)

    context = {
        'page_obj': get_page_obj(request, posts, POSTS_LIMIT),
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user).filter(author=author)

    if not follow:
        if not request.user.username == username:
            Follow.objects.create(
                user=request.user,
                author=User.objects.get(username=username)
            )

    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(user=request.user).filter(author=author).delete()
    return redirect('posts:follow_index')
