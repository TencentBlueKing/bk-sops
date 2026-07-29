# -*- coding: utf-8 -*-

import json

from django.core.management.base import BaseCommand

from gcloud.contrib.admin.diagnostics.evidence import build_task_evidence


class Command(BaseCommand):
    help = "Export task diagnostic evidence package."

    def add_arguments(self, parser):
        parser.add_argument("task_id", type=int)
        parser.add_argument("--node-id", default="")
        parser.add_argument("--output", default="")

    def handle(self, *args, **options):
        evidence = build_task_evidence(options["task_id"], options["node_id"])
        content = json.dumps(evidence, ensure_ascii=False, indent=2, default=str)

        if options["output"]:
            with open(options["output"], "w") as fp:
                fp.write(content)
            self.stdout.write(options["output"])
        else:
            self.stdout.write(content)
