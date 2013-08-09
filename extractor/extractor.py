import os
import sys
import argparse
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description='Extract site pages.')
    parser.add_argument('site', metavar='site', type=str, nargs=1, help='site id, for example: theverge, npr, nytimes')
    return parser.parse_args()

def main():
    args = parse_args()

    # find url filea
    path = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', args.site[0]))
 
    with open(os.path.join(path, 'urls')) as f:
        urls = f.readlines()

    for id, url in enumerate(urls):
        url = url.strip()
        if not url:
            continue

        print '[extractor] #%03d: %s' % (id, url)
        subprocess.call('cd "%(data)s" && phantomjs "%(extractor)s" "%(url)s" "%(label)03d" > "%(label)03d.json" 2> "%(label)03d.log"' % {
            'data': path,
            'extractor': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'extractor.coffee'),
            'url': url,
            'label': id,
        }, shell=True)

if __name__ == '__main__':
    main()
