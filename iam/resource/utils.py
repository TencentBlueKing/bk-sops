# -*- coding: utf-8 -*-

from iam.collection import FancyDict


def get_filter_obj(filter_data, filter_keys):
    filter_obj = FancyDict()
    _filter_data = filter_data or {}
    for key in filter_keys:
        filter_obj[key] = _filter_data.get(key)
    return filter_obj


class Page(object):
    def __init__(self, limit, offset):
        self.limit = limit
        self.offset = offset

    @property
    def slice_from(self):
        return self.offset

    @property
    def slice_to(self):
        if self.limit == 0:
            return None
        return self.offset + self.limit


def get_page_obj(page_data):
    return Page(limit=page_data.get("limit", 0), offset=page_data.get("offset", 0))
