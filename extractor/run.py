#!/usr/bin/env python

import os
import sys

lib_path = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'lib'))
if lib_path not in sys.path:
    sys.path[0:0] = [lib_path]

import utils
import os
import argparse
import subprocess

def main(args):

    extractor = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'extractor.coffee')
    path = utils.get_data_path(args.site[0])
    urls = utils.load_urls(path)

    # extract data from each url
    for id, url in enumerate(urls):
        url = url.strip()
        if not url:
            continue

        # skip already extracted
        if os.path.exists(os.path.join(path, '%03d.json' % id)):
            continue

        print '[extractor] #%03d: %s' % (id, url)
        subprocess.call('cd "%(path)s" && phantomjs "%(extractor)s" "%(url)s" "%(label)03d" > "%(label)03d.log" 2>&1' % {
            'path': path,
            'extractor': extractor,
            'url': url,
            'label': id,
        }, shell=True)

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Extract site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
