# VideoCollector/content/views.py
import more_itertools
import urllib
from content.models import Category, Video
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django import forms
from django.core.paginator import Paginator

# Creating a model form using modelform_factory
VideoForm = forms.modelform_factory(
    Video,
    fields=[
        "youtube_id",
        "title",
        "author",
        "view_count",
    ],
)


def home(request):
    categories = Category.objects.all()
    data = {"rows": more_itertools.chunked(categories, 3)}

    return render(request, "home.html", data)


def category(request, name):
    category = get_object_or_404(Category, name__iexact=name)

    if request.method == "GET":
        form = VideoForm()
    else:
        # POST
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save()
            video.categories.add(category)

    videos = Video.objects.filter(categories=category)
    data = {
        "category": category,
        "form": form,
        "rows": more_itertools.chunked(videos, 3),
    }

    return render(request, "category.html", data)


def play_video(request, video_id):
    data = {"video": get_object_or_404(Video, id=video_id)}

    return render(request, "play_video.html", data)


def feed(request):
    videos = Video.objects.all()
    paginator = Paginator(videos, 2)  # 2 videos per page
    page_num = int(request.GET.get("page", 1))

    if page_num < 1:
        page_num = 1
    elif page_num > paginator.num_pages:
        page_num = paginator.page(page_num)

    page = paginator.page(page_num)

    data = {
        "videos": page.object_list,
        "more_videos": page.has_next(),
        "next_page": page_num + 1,
    }

    if request.htmx:
        # import time

        # time.sleep(2)
        return render(request, "partials/feed_results.html", data)

    return render(request, "feed.html", data)


def add_video_form(request, name):
    category = get_object_or_404(Category, name__exact=name)
    data = {
        "category": category,
    }

    return render(request, "partials/add_video_form.html", data)


def add_video_link(request, name):
    category = get_object_or_404(Category, name__exact=name)
    data = {
        "category": category,
    }

    return render(request, "partials/add_video_link.html", data)


def search(request):
    search_text = request.GET.get("search_text", "")
    search_text = urllib.parse.unquote(search_text)
    search_text = search_text.strip()

    videos = None

    if search_text:
        parts = search_text.split()

        q = Q(title__icontains=parts[0]) | Q(author__icontains=parts[0])
        for part in parts[1:]:
            q |= Q(title__icontains=part) | Q(
                author__icontains=part
            )  # Union of Q objects

        videos = Video.objects.filter(q)

    data = {
        "search_text": search_text,
        "videos": videos,
    }

    if request.htmx:
        return render(request, "partials/search_results.html", data)

    return render(request, "search.html", data)


def about(request):
    return render(request, "partials/about.html")
