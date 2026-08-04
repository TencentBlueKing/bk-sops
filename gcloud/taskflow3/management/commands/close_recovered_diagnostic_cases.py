# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Close supplemental diagnostic cases whose task already finished, recovered or aged out."

    def add_arguments(self, parser):
        parser.add_argument("--chunk", type=int, default=None, help="cases scanned per page")
        parser.add_argument("--dry-run", action="store_true", help="only report how many cases would be closed")

    def handle(self, *args, **options):
        from gcloud.contrib.admin.diagnostics.supplement import sweep_recovered_cases

        scanned, resolved, aged_out = sweep_recovered_cases(chunk=options["chunk"], dry_run=options["dry_run"])
        prefix = "would_" if options["dry_run"] else ""
        self.stdout.write("scanned={} {}resolved={} {}ignored={}".format(scanned, prefix, resolved, prefix, aged_out))
