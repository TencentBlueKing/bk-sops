# -*- coding: utf-8 -*-

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class ResourceApiDispatcher(object):
    @abc.abstractmethod
    def register(self, provider_type, provider):
        raise NotImplementedError()
