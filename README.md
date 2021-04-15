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
from django.http import HttpResponse
from django_simple_profiler import django_profiler # as decorator
from django_simple_profiler import DjangoProfiler # as context manager


@django_profiler
def get_countries(request):
    for country in Country.objects.all():
        print(country)
    return HttpResponse("OK")

def get_countries(request):
    with DjangoProfiler() as dp:
        for country in Country.objects.all():
            print(country)
    return HttpResponse("OK")
```



