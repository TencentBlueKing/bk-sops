# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Close supplemental diagnostic cases whose task already finished or recovered."

    def add_arguments(self, parser):
        parser.add_argument("--chunk", type=int, default=None, help="cases scanned per page")
        parser.add_argument("--dry-run", action="store_true", help="only report how many cases would be closed")

    def handle(self, *args, **options):
        from gcloud.contrib.admin.diagnostics.supplement import sweep_recovered_cases

        scanned, closed = sweep_recovered_cases(chunk=options["chunk"], dry_run=options["dry_run"])
        self.stdout.write("scanned={} {}={}".format(scanned, "closable" if options["dry_run"] else "closed", closed))
