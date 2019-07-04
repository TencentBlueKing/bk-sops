# -*- coding: utf-8 -*-

from ..base import ComponentAPI


class CollectionsMyAPI(object):
    def __init__(self, client):
        self.client = client

        self.get_dfinfo = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/self-service-api/host/get_dfinfo_lanhaibin/',
            description=u"磁盘使用率查询"
        )
