# coding:utf-8

from ..base import ComponentAPI


class CollectionsDiskUsage(object):
    """Collections of Disk Usage APIS"""

    def __init__(self, client):
        self.client = client

        self.get_disk_usage = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/self-service-api/earlybird/apis/get_disk_usage/',
            description=u'获取磁盘分区容量记录'
        )