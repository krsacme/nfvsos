#!/usr/bin/env python

import argparse
from collections import deque
import logging
import os
import traceback
import sys


import checkers
from nfvsos.utilities import ImporterHelper
from nfvsos.checkers import import_plugin


LOG = logging.getLogger(__name__)


def main(argv=sys.argv[1:]):
    # Enable console logging
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    root_logger.addHandler(console_handler)

    # Arguments
    parser = argparse.ArgumentParser(
        description='Analyze the sosreport')
    parser.add_argument('sosdir', help='sos directory path')
    args = parser.parse_args(argv)

    if not os.path.isabs(args.sosdir):
        LOG.error("Provide absolute path of the sosreport directory (extracted)")
        sys.exit(1)
    if not os.path.isdir(args.sosdir):
        LOG.error("Provide the path of sosreport directory (extracted)")
        sys.exit(1)

    nfvsos = NfvSosAnalyzer(args.sosdir)
    nfvsos.load_plugins()
    nfvsos.analyze()


class NfvSosAnalyzer(object):

    def __init__(self, sosdir):
        self.sosdir = sosdir
        self.loaded_plugins = deque()
        self.raise_plugins = False
        self.exit_process = False

    def get_commons(self):
        return {}

    def _load(self, plugin_class):
        self.loaded_plugins.append((
            plugin_class.name(),
            plugin_class(self.get_commons())
        ))

    def handle_exception(self, plugname=None, func=None):
        if self.raise_plugins or self.exit_process:
            raise
        if plugname and func:
            self._log_plugin_exception(plugname, func)

    def _log_plugin_exception(self, plugin, method):
        trace = traceback.format_exc()
        msg = "caught exception in plugin method"
        LOG.error('%s "%s.%s()"' % (msg, plugin, method))
        LOG.error('%s' % trace)

    def load_plugins(self):
        import nfvsos.checkers
        helper = ImporterHelper(nfvsos.checkers)
        plugins = helper.get_modules()

        # validate and load plugins
        for plug in plugins:
            plugbase, ext = os.path.splitext(plug)
            try:
                plugin_classes = import_plugin(plugbase)
                if not len(plugin_classes):
                    # no valid plugin classes for this policy
                    continue

                # After all the checks add the item to the list
                self._load(plugin_classes[0])

            except Exception as e:
                traceback.print_exc()
                print(e)

    def analyze(self):
        for plugname, plug in self.loaded_plugins:
            try:
                plug.analyze(self.sosdir)
            except KeyboardInterrupt:
                raise
            except (OSError, IOError) as e:
                if e.errno in fatal_fs_errors:
                    self.ui_log.error("")
                    self.ui_log.error(" %s while setting up plugins"
                                      % e.strerror)
                    self.ui_log.error("")
                    self._exit(1)
                self.handle_exception(plugname, "setup")
            except:
                self.handle_exception(plugname, "setup")


if __name__ == "__main__":
    main()