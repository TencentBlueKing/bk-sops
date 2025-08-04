from django.contrib import admin

from gcloud.contrib.appexemption import models


@admin.register(models.AppExemption)
class AppExemptionAdmin(admin.ModelAdmin):
    list_display = ["app_code", "exemption_projects", "extra_info"]
    list_filter = ["app_code"]
    search_fields = ["app_code"]
