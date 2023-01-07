from django.core.paginator import Paginator


def get_page_obj(request, posts, limit_posts):
    paginator = Paginator(posts, limit_posts)
    page_namber = request.GET.get('page')

    return paginator.get_page(page_namber)
