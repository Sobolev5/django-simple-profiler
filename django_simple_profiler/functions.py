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
    for query in queries:
        queries_table.append([query["sql"][:200]])
    table_data = queries_table
    len_queries = len(queries)
    table_instance = SingleTable(table_data, f" {lineno} top {len_queries} queries ")
    table_instance.inner_heading_row_border = False
    return table_instance.table


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
    @wraps(func)
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
                    prettify_sql = "\033[1;31m[{}]\033[0m {}".format(query["time"], query["sql"].replace('"', "").replace(",", ", "))
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


@contextmanager
def DjangoProfiler():
    if settings.DEBUG:

        current_line_no = inspect.stack()[2][2]
        current_function_name = inspect.stack()[2][3]
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
                prettify_sql = "\033[1;31m[{}]\033[0m {}".format(query["time"], query["sql"].replace('"', "").replace(",", ", "))
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
    else:
        yield
