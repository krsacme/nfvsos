#!/usr/bin/env python

import argparse
from collections import deque
import logging
import os
from textwrap import wrap, fill
import traceback
import sys


import checkers
from nfvsos.utilities import ImporterHelper
from nfvsos.checkers import import_plugin


LOG = logging.getLogger(__name__)


def main(argv=sys.argv[1:]):
    # Enable console logging
    log_formatter = logging.Formatter(
        "%(levelname)s: %(module)s:  %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
    for handler in logging.root.handlers:
        handler.addFilter(logging.Filter('nfvsos'))


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
    nfvsos.show_result()


class NfvSosAnalyzer(object):

    def __init__(self, sosdir):
        self.sosdir = sosdir
        self.loaded_plugins = deque()
        self.raise_plugins = False
        self.exit_process = False

    def get_commons(self):
        return {
            'sosdir': self.sosdir
        }

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
                plug.analyze()
            except KeyboardInterrupt:
                raise
            except (OSError, IOError) as e:
                if e.errno in fatal_fs_errors:
                    self.ui_log.error("")
                    self.ui_log.error(" %s while analyzing logs"
                                      % e.strerror)
                    self.ui_log.error("")
                    self._exit(1)
                self.handle_exception(plugname, "analyze")
            except:
                self.handle_exception(plugname, "analyze")

    def show_result(self):
        outputs = self.get_results()
        for name, obj in outputs.items():
            print("-" * 79)
            print("Checker({0}) Failed({1}) Passed({2})".format(
                name, len(obj['failed']), len(obj['passed'])))
            if obj['failed']:
                self.wrap_print(">FAILED<", obj['failed'])
            if obj['passed']:
                self.wrap_print("PASSED", obj['passed'])
        print("-" * 79)

    def wrap_print(self, text, items):
        for item in items:
            wrapped = wrap(' * ' + text + ': ' + item, 77)
            print(wrapped[0])
            if len(wrapped) > 1:
                print('\n'.join('   ' + j for j in wrapped[1:]))

    def get_results(self):
        outputs = {}
        for plugname, plug in self.loaded_plugins:
            try:
                obj = {}
                obj['failed'] = plug.failed()
                obj['passed'] = plug.passed()
                obj['status'] = plug.status()
                outputs.update({plugname: obj})
            except KeyboardInterrupt:
                raise
            except (OSError, IOError) as e:
                if e.errno in fatal_fs_errors:
                    self.ui_log.error("")
                    self.ui_log.error(" %s while analyzing logs"
                                      % e.strerror)
                    self.ui_log.error("")
                    self._exit(1)
                self.handle_exception(plugname, "analyze")
            except:
                self.handle_exception(plugname, "analyze")
        return outputs


if __name__ == "__main__":
    main()
