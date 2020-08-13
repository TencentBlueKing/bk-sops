# -*- coding: utf-8 -*-

import six
import abc


class ListResult(object):
    def __init__(self, results, count):
        """
        :param results: 返回的结果
        :param count: 总记录数
        """
        self.count = count
        self.results = results

    def to_dict(self):
        return {"count": self.count, "results": self.results}

    def to_list(self):
        return self.results


@six.add_metaclass(abc.ABCMeta)
class ResourceProvider(object):
    @abc.abstractmethod
    def list_attr(self, **options):
        """
        处理来自 iam 的 list_attr 请求
        return: ListResult
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def list_attr_value(self, filter, page, **options):
        """
        处理来自 iam 的 list_attr_value 请求
        return: ListResult
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def list_instance(self, filter, page, **options):
        """
        处理来自 iam 的 list_instance 请求
        return: ListResult
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def fetch_instance_info(self, filter, **options):
        """
        处理来自 iam 的 fetch_instance_info 请求
        return: ListResult
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def list_instance_by_policy(self, filter, page, **options):
        """
        处理来自 iam 的 list_instance_by_policy 请求
        return: ListResult
        """
        raise NotImplementedError()
