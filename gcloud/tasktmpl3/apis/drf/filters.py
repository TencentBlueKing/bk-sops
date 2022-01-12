# -*- coding: utf-8 -*-
from rest_framework.filters import OrderingFilter


class TemplateOrderingFilter(OrderingFilter):
    ordering_param = "order_by"
