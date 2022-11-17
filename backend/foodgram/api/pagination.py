from rest_framework.pagination import LimitOffsetPagination


class MyPagination(LimitOffsetPagination):
    offset_query_param = 'page'
