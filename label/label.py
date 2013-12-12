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

    extractor = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'label.py')
    path = utils.get_data_path(args.site[0])
    urls = utils.load_urls(path)

    # load each JSON file from chaos.
    # Read each block of that file.
    # [P2] Sort the blocks by their size.
    # Also load the gold-text of that file.
    # If matching between gold-text and that element text is
    #   above a certain threshold, label that block as 1.
    # [P2] remove the matching part from gold-text.
    # Rewrite the blocks to another json file.

    # extract data from each url

    # load data
    data = [utils.load_data(path, id) for id, url in enumerate(urls)]
    goldText = [utils.load_gold_text(path, id) for id, url in enumerate(urls)]
    for page in data:
        for text in page['texts']:
            fullText = 
            


def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Extract site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())