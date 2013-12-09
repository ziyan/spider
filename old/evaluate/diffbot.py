#!/usr/bin/env python

import os
import sys

lib_path = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'lib'))
if lib_path not in sys.path:
    sys.path[0:0] = [lib_path]

import utils
import os
import argparse
import urllib, urllib2
import simplejson as json

def main(args):

    path = utils.get_data_path(args.site[0])
    urls = utils.load_urls(path)

    # extract data from each url
    data = []
    for id, url in enumerate(urls):
        url = url.strip()
        if not url:
            continue

        print '[diffbot] #%03d: %s' % (id, url)
        response = urllib2.urlopen('http://www.diffbot.com/api/article?' + urllib.urlencode({
            'url': url,
            'token': '4bc6e407da88dd8723c70a5297cdf7fb',
            'timeout': '60000',
        }))

        data.append(json.loads(response.read()))

    with open(os.path.join(path, 'diffbot.json'), 'w') as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf8'))

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Extract site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
