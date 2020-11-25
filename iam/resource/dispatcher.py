# -*- coding: utf-8 -*-

import six
import abc


@six.add_metaclass(abc.ABCMeta)
class ResourceApiDispatcher(object):
    @abc.abstractmethod
    def register(self, provider_type, provider):
        raise NotImplementedError()
