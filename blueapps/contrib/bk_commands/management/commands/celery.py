from __future__ import absolute_import, unicode_literals

from optparse import make_option as Option

from celery.bin import celery

from blueapps.contrib.bk_commands.management.app import app
from blueapps.contrib.bk_commands.management.base import CeleryCommand

base = celery.CeleryCommand(app=app)


class Command(CeleryCommand):
    """The celery command."""

    help = "celery commands, see celery help"
    options = (
        Option("-A", "--app", default=None),
        Option("--broker", default=None),
        Option("--loader", default=None),
        Option("--config", default=None),
        Option("--workdir", default=None, dest="working_directory"),
        Option("--result-backend", default=None),
        Option("--no-color", "-C", action="store_true", default=None),
        Option("--quiet", "-q", action="store_true"),
    )
    if base.get_options() is not None:
        options = options + CeleryCommand.options + base.get_options()

    def run_from_argv(self, argv):
        argv = self.handle_default_options(argv)
        base.execute_from_commandline(["{0[0]} {0[1]}".format(argv)] + argv[2:],)
