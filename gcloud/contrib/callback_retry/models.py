# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from enum import Enum


class CallbackStatus(Enum):
    READY = "READY"  # 准备中
    SUCCESS = "SUCCESS"  # 回调成功
    FAILED = "FAILED"  # 回调失败
    REVOKED = "REVOKED"  # 已取消，当节点状态不为running时，则取消本次回调任务
    DISCARDED = "DISCARDED"  # 已丢弃，当同时来两次回调时，旧的回调会被丢弃，已新的回调为主


class CallbackRetryTask(models.Model):
    """
    回调重试任务
    """

    CALLBACK_STATUS_CHOICES = (
        (CallbackStatus.READY.value, _("准备回调")),
        (CallbackStatus.SUCCESS.value, _("回调成功")),
        (CallbackStatus.FAILED.value, _("回调失败")),
        (CallbackStatus.REVOKED.value, _("已取消")),
        (CallbackStatus.DISCARDED.value, _("丢弃")),
    )

    task_id = models.BigIntegerField(_("提单人"))
    # type = models.CharField(_("回调类型"), choices=CALLBACK_TYPE_CHOICES, default=CallbackType.JOB.value)
    node_id = models.CharField(_("任务实例节点ID"), max_length=255, blank=True, default="")
    version = models.CharField(_("版本"), max_length=64)
    data = models.JSONField(_("callback Data"), default=dict)
    status = models.CharField(
        _("回调状态"), max_length=32, choices=CALLBACK_STATUS_CHOICES, default=CallbackStatus.READY.value
    )
    count = models.IntegerField(_("回调次数"), default=0)
    error = models.TextField(_("异常信息"), blank=True, null=True)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    finish_time = models.DateTimeField(_("结束时间"), null=True, blank=True)

    class Meta:
        verbose_name = _("回调重试任务")
        verbose_name_plural = _("回调重试任务表")
        index_together = ["task_id", "node_id", "version", "status"]

    @classmethod
    def exists(cls, task_id, node_id, version, status=CallbackStatus.READY.value):
        return cls.objects.filter(task_id=task_id, node_id=node_id, version=version, status=status).exists()