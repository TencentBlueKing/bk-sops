# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
class Host(models.Model):
    ip = models.CharField( max_length=100,verbose_name='主机IP')
    os = models.CharField( max_length=100, verbose_name='系统')
    partition = models.CharField(max_length=100, verbose_name='分区')

    class Meta:
        verbose_name = "主机"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ip

# 相应数据库可以参照
class DiskUsage(models.Model):
    value = models.IntegerField('磁盘使用率')
    add_time = models.DateTimeField('录入时间', auto_now=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="DiskUsage") # 如果你没有外键Host注释 这句