import inspect
import math
import os
import time
from contextlib import contextmanager
from functools import wraps
import psutil
from colorclass import Color
from django.conf import settings
from django.db import connection
from django.db import reset_queries
from terminaltables import SingleTable

"""

Django simple profiler by Sobolev Andrey
https://github.com/Sobolev5

requires DEBUG=True in settings.py

Example:

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

"""


def _convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    x = int(math.floor(math.log(size_bytes, 1024)))
    y = math.pow(1024, x)
    z = round(size_bytes / y, 2)
    return "{} {}".format(z, size_name[x])


def _get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def _table_response_timing(lineno, total_time, total_queries_time, queries_count):
    table_data = [
        [Color("{green}Total time:{/green}"), f"{total_time}s           "],
        [Color("{yellow}Database queries time:{/yellow}"), f"{total_queries_time}s          "],
        [Color("{cyan}Queries count:{/cyan}"), f"{queries_count}            "],
    ]
    table_instance = SingleTable(table_data, f" {lineno} time ")
    table_instance.inner_heading_row_border = False
    return table_instance.table


def _table_response_queries(lineno, queries):
    queries_table = []
    if not queries:
        queries_table.append(["No sql queries"])
    else:
        for query in queries:
            queries_table.append([query["sql"][:200]])
    table_data = queries_table
    len_queries = len(queries)
    if not queries:
        table_instance = SingleTable(table_data, f" queries ")
    else:
        table_instance = SingleTable(table_data, f" {lineno} top {len_queries} queries ")
    table_instance.inner_heading_row_border = False
    return table_instance.table


def _single_line_response_queries(lineno, queries):
    len_queries = len(queries)
    print(f"{lineno} {len_queries} queries:\n")
    for query in queries:
        print(query["sql"])


def _table_response_memory(lineno, memory_before, memory_after, memory_difference):
    table_data = [
        [Color("{green}Memory before:{/green}"), f"{_convert_size(memory_before)}           "],
        [Color("{yellow}Memory after:{/yellow}"), f"{_convert_size(memory_after)}           "],
        [Color("{cyan}Memory difference:{/cyan}"), f"{_convert_size(memory_difference)}         "],
    ]
    table_instance = SingleTable(table_data, f" {lineno} memory ")
    table_instance.inner_heading_row_border = False
    return table_instance.table


def django_profiler(func):
    def wrapper(*args, **kwargs):    
        if settings.DEBUG:
            current_line_no = func.__code__.co_firstlineno
            current_function_name = func.__name__
            lineno = f"{current_function_name} [{current_line_no}]"
            time_start = time.process_time()
            memory_before = _get_process_memory()
            reset_queries()
            response = func(*args, **kwargs)
            memory_after = _get_process_memory()
            total_queries_time = 0.0
            queries_count = len(connection.queries)
            queries_list = []
            for query in connection.queries:
                if query["sql"]:
                    prettify_sql = "[{}] {}".format(query["time"], query["sql"].replace('"', "").replace(",", ", "))
                    total_queries_time += float(query["time"])
                    queries_list.append({"sql": (f"{prettify_sql}\n"), "time": float(query["time"])})
            queries_list = sorted(queries_list, key=lambda x: -x["time"])
            total_request_time = time.process_time() - time_start
            total_request_time = f"{round(total_request_time, 4)}"
            print()
            print(_table_response_timing(lineno, total_request_time, total_queries_time, queries_count))
            print()
            print(_table_response_queries(lineno, queries_list[:10]))
            print()
            print(_table_response_memory(lineno, memory_before, memory_after, memory_after - memory_before))
            print()
            return response

        else:
            response = func(*args, **kwargs)
            return response

    return wrapper


def django_profiler_full(func):
    def wrapper(*args, **kwargs):    
        if settings.DEBUG:
            current_line_no = func.__code__.co_firstlineno
            current_function_name = func.__name__
            lineno = f"{current_function_name} [{current_line_no}]"
            time_start = time.process_time()
            memory_before = _get_process_memory()
            reset_queries()
            response = func(*args, **kwargs)
            memory_after = _get_process_memory()
            total_queries_time = 0.0
            queries_count = len(connection.queries)
            queries_list = []
            for query in connection.queries:
                if query["sql"]:
                    prettify_sql = "[{}] {}".format(query["time"], query["sql"].replace('"', "").replace(",", ", "))
                    total_queries_time += float(query["time"])
                    queries_list.append({"sql": (f"{prettify_sql}\n"), "time": float(query["time"])})
            queries_list = sorted(queries_list, key=lambda x: -x["time"])
            total_request_time = time.process_time() - time_start
            total_request_time = f"{round(total_request_time, 4)}"
            print()
            print(_table_response_timing(lineno, total_request_time, total_queries_time, queries_count))
            print()
            _single_line_response_queries(lineno, queries_list)
            print()
            print(_table_response_memory(lineno, memory_before, memory_after, memory_after - memory_before))
            print()
            return response

        else:
            response = func(*args, **kwargs)
            return response

    return wrapper

@contextmanager
def DjangoProfiler(label=None, full=None):
    if settings.DEBUG:

        current_line_no = inspect.stack()[2][2]
        current_function_name = inspect.stack()[2][3]

        if label:
            lineno = f"\033[1;31m{label}\033[0m [{current_line_no}]"
        else:
            lineno = f"{current_function_name} [{current_line_no}]"

        time_start = time.process_time()
        memory_before = _get_process_memory()
        reset_queries()
        yield
        memory_after = _get_process_memory()
        total_queries_time = 0.0
        queries_count = len(connection.queries)
        queries_list = []
        for query in connection.queries:
            if query["sql"]:
                prettify_sql = "[{}] {}".format(query["time"], query["sql"].replace('"', "").replace(",", ", "))
                total_queries_time += float(query["time"])
                queries_list.append({"sql": (f"{prettify_sql}\n"), "time": float(query["time"])})
        queries_list = sorted(queries_list, key=lambda x: -x["time"])
        total_request_time = time.process_time() - time_start
        total_request_time = f"{round(total_request_time, 4)}"
        print()
        print(_table_response_timing(lineno, total_request_time, total_queries_time, queries_count))
        print()
        if full:
            _single_line_response_queries(lineno, queries_list)
        else:
            print(_table_response_queries(lineno, queries_list[:10]))
        print()
        print(_table_response_memory(lineno, memory_before, memory_after, memory_after - memory_before))
        print()
    else:
        yield
