from __future__ import print_function

import argparse
import sys
import os

from .util import make_registration_decorator, make_ckan_api, make_logger, authenticated_ckan_session
from .projects.arp.export import ARPExport
from .projects.amdb.export import AMDBExport
import requests

logger = make_logger(__name__)
register_command, command_fns = make_registration_decorator()


def setup_export_arp(subparser):
    subparser.add_argument('target_dir', type=str)


@register_command
def export_arp(ckan, args):
    """export ARP data"""
    def in_tree(path):
        return os.path.join(args.target_dir, path)
    session = authenticated_ckan_session(ckan)
    exporter = ARPExport()
    resources = exporter.get_resources(ckan)
    target_paths = set(t[1] for t in resources)
    for target_path in target_paths:
        try:
            os.makedirs(in_tree(target_path))
        except OSError:
            pass
    for url, target_path, target_filename, sha256 in resources:
        outf = in_tree(os.path.join(target_path, target_filename))
        # FIXME: stronger test that the target_filename is correct
        if os.access(outf, os.R_OK):
            continue
        tmpf = in_tree(os.path.join(target_path, '.ingest_' + target_filename))
        with open(tmpf, 'wb') as outfd:
            logger.info("starting download: %s" % (url))
            response = session.get(url, stream=True)
            for block in response.iter_content(8192):
                outfd.write(block)
        os.rename(tmpf, outf)
        logger.info("download complete: %s" % (url))


@register_command
def export_amdb(ckan, args):
    """export Australian Microbiome Database data"""
    def in_tree(args_target_dir, path):
        return os.path.join(args_target_dir, path)

    exporter = AMDBExport()
    resources, md5sums = exporter.get_resources(ckan)
    logger.info(len(resources))
    target_paths = set(t[1] for t in resources)
    # Creating folder structure
    logger.info("creating folder structure")
    for target_path in target_paths:
        try:
            os.makedirs(in_tree(args.target_dir, target_path))
        except OSError:
            pass
    logger.info("downloading datasets")
    for url, target_path, target_filename, sha256 in resources:

        outf = in_tree(args.target_dir, os.path.join(
            target_path, target_filename))
        # FIXME: stronger test that the target_filename is correct

        # Skipping download if already downloaded
        if os.access(outf, os.R_OK):
            continue

        logger.info("starting download: %s" % (url))
        response = requests.get(url, auth=(
            'CKAN_USERNAME', 'CKAN_PASSWORD'))
        with open(outf, 'wb') as outfd:
            for block in response.iter_content(8192):
                outfd.write(block)

        logger.info("download complete: %s" % (outf))

    # Generating md5sum.txt for every dataset
    for target_path, md5sum in md5sums.items():
        f = in_tree(args.target_dir, os.path.join(target_path, "md5sum.txt"))
        if os.access(f, os.R_OK):
            continue
        with open(f, 'w') as md5f:
            logger.info("Generating md5sum.txt in %s" % (target_path))
            md5f.write('\n'.join('{} {}'.format(x[0], x[1]) for x in md5sum))


export_arp.setup = setup_export_arp
export_amdb.setup = setup_export_arp


def version():
    import pkg_resources
    version = pkg_resources.require("bpaingest")[0].version
    print('''\
bpa-ckan-export, version %s

Copyright 2016 CCG, Murdoch University
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.''' % (version))
    sys.exit(0)


def usage(parser):
    parser.print_usage()
    sys.exit(0)


def commands():
    for fn in command_fns:
        name = fn.__name__.replace('_', '-')
        yield name, fn, getattr(fn, 'setup', None), fn.__doc__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true',
                        help='print version and exit')
    parser.add_argument('-k', '--api-key', required=True, help='CKAN API Key')
    parser.add_argument('-u', '--ckan-url', required=True,
                        help='CKAN base url')

    subparsers = parser.add_subparsers(dest='name')
    for name, fn, setup_fn, help_text in sorted(commands()):
        subparser = subparsers.add_parser(name, help=help_text)
        subparser.set_defaults(func=fn)
        if setup_fn is not None:
            setup_fn(subparser)
    args = parser.parse_args()
    if args.version:
        version()
    if 'func' not in args:
        usage(parser)
    ckan = make_ckan_api(args)
    args.func(ckan, args)
