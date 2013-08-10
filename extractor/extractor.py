import os
import argparse
import subprocess


def get_extractor_path():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'extractor.coffee')

def get_data_path(site):
    return os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', site))

def load_urls(path):
    with open(os.path.join(path, 'urls')) as f:
        urls = f.readlines()
    return urls

def main(args):

    extractor = get_extractor_path()
    path = get_data_path(args.site[0])
    urls = load_urls(path)

    # extract data from each url
    for id, url in enumerate(urls):
        url = url.strip()
        if not url:
            continue

        print '[extractor] #%03d: %s' % (id, url)
        subprocess.call('cd "%(path)s" && phantomjs "%(extractor)s" "%(url)s" "%(label)03d" > "%(label)03d.json" 2> "%(label)03d.log"' % {
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
