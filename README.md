# Django simple profiler
Django simple profiler it is a useful tool for Django framework that allows you to profiling your views.

Example of use:
- decorate your views
- use as context manager

Requires DEBUG=True in settings.py (!)

```no-highlight
https://github.com/Sobolev5/django-simple-profiler
```

# How to install it
To install run:
```no-highlight
pip install django-simple-profiler
```


# example.py
```python
from django_simple_profiler import django_profiler # as decorator
from django_simple_profiler import django_profiler_full # as decorator with full queries
from django_simple_profiler import DjangoProfiler # as context manager


@django_profiler
def get_countries(request):
    for country in Country.objects.all():
        print(country)
    return HttpResponse("OK")

@django_profiler_full
def get_countries(request):
    for country in Country.objects.all():
        print(country)
    return HttpResponse("OK")

def get_countries(request):

    # simple
    with DjangoProfiler() as dp: 
        for country in Country.objects.all():
            print(country)

    # full queries
    with DjangoProfiler(full=True) as dp:
        for country in Country.objects.all():
            print(country)

    # with label
    with DjangoProfiler(label="ActiveCountries") as dp:
        for country in Country.objects.filter(active=True):
            print(country)

    # with label and full queries
    with DjangoProfiler(label="ActiveCountries", full=True) as dp:
        for country in Country.objects.filter(active=True):
            print(country)

    return HttpResponse("OK")
```

![](https://github.com/Sobolev5/django-simple-profiler/blob/master/screenshots/screen.png)

# Try my free time tracker
My free time tracker for developers [Workhours.space](https://workhours.space/). 