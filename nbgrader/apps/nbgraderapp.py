#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import logging
import os

from IPython.utils.traitlets import Unicode, List
from IPython.core.application import BaseIPythonApplication
from IPython.core.profiledir import ProfileDir
from IPython.config.application import catch_config_error

_examples = """
nbgrader --help
nbgrader --help-all
nbgrader --NBGraderApp.overwrite=True

nbgrader --log-level=DEBUG
"""

class NBGraderApp(BaseIPythonApplication):

    name = Unicode('nbgrader')
    description = Unicode(u'A system for assigning and grading notebooks')
    version = Unicode(u'0.1')
    examples = Unicode(_examples)
    ipython_dir = "/tmp/nbgrader"

    def _log_level_default(self):
        return logging.INFO

    # The classes added here determine how configuration will be documented
    classes = List()

    def _classes_default(self):
        """This has to be in a method, for TerminalIPythonApp to be available."""
        return [
            ProfileDir
        ]

    subcommands = dict(
        assign=(
            'nbgrader.apps.assignapp.AssignApp',
            "Create a students version of a notebook"
        ),
        autograde=(
            'nbgrader.apps.autogradeapp.AutogradeApp',
            "Autograde a notebook by running it"
        ),
        formgrade=(
            'nbgrader.apps.formgradeapp.FormgradeApp',
            "Grade a notebook using an HTML form"
        ),
        record=(
            'nbgrader.apps.recordapp.RecordApp',
            "Record scores from graded notebooks into a database"
        ),
    )

    @catch_config_error
    def initialize(self, argv=None):
        if not os.path.exists(self.ipython_dir):
            self.log.warning("Creating IPython directory: {}".format(self.ipython_dir))
            os.mkdir(self.ipython_dir)
        super(NBGraderApp, self).initialize(argv)
        self.stage_default_config_file()

    def start(self):
        # This starts subapps
        super(NBGraderApp, self).start()

def main():
    NBGraderApp.launch_instance()
