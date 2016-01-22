#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
from __future__ import division

import argparse
import sys
import tempfile
import shutil
import os
import zipfile

known_products = {
    'pycharm': 'PyCharm50',
    'clion': 'CLion12'
}


def listfiles(path, prefix=None):
    files = []
    if prefix is None:
        prefix = path
        path = ""

    for filename in os.listdir(os.path.join(prefix, path)):
        absfile = os.path.join(prefix, path, filename)
        relfile = os.path.join(path, filename)
        if os.path.isdir(absfile):
            files += listfiles(relfile, prefix=prefix)
        else:
            files += [relfile]
    return files


def onerror_shutil(function, path, excinfo):
    print('[E] %s @ %s: ', (str(function), path, str(excinfo)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='dot-idea settings jar generator')
    parser.add_argument('product', type=str, choices=known_products.keys())
    parser.add_argument('--no-cleanup', default=False, action='store_true')
    args = parser.parse_args()

    product = args.product
    ident = known_products[product]
    print('Generating settings for %s [%s]' % (product, ident), file=sys.stderr)

    tmpdir = tempfile.mktemp() # NB:
    print('[D] Temp dir: %s' % tmpdir)

    srcdir = os.path.join(os.getcwd(), 'home', 'Library', 'Preferences', ident)
    shutil.copytree(srcdir, tmpdir)
    shutil.copyfile(os.path.join(os.getcwd(), 'plugins.'+product), os.path.join(tmpdir, 'installed.txt'))
    open(os.path.join(tmpdir, 'IntelliJ IDEA Global Settings'), 'a').close()

    allfiles = listfiles(tmpdir)
    print(allfiles)

    with zipfile.ZipFile(product + '-settings.jar', 'a') as jar:
        for f in allfiles:
            jar.write(os.path.join(tmpdir, f), f)

    if not args.no_cleanup:
        print('Cleaning up', file=sys.stderr)
        shutil.rmtree(tmpdir)
