#!/usr/bin/env python

import argparse
import logging
import os
import sys

import conditions
import utils
import dpdk

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

    # Run Analyzers
    dpdk_obj = dpdk.DpdkTripleOAnalyzer(args.sosdir)
    dpdk_obj.analyze()


if __name__ == "__main__":
    main()
