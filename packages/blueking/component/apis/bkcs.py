# -*- coding: utf-8 -*-


from ..base import ComponentAPI


class CollectionsBKCS(object):
    """Collections of JOB APIS"""

    def __init__(self, client):
        self.client = client

        self.get_host_capacity = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi/bkcs/get_host_capacity/',
            description=u'查询磁盘容量'
        )
