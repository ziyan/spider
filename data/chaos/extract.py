import bs4
import os
import subprocess
import shutil

def main():
    extractor = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'extractor', 'extractor.coffee'))

    for id in range(0, 200):
        path = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'original', '%d.htm' % id))
        soup = bs4.BeautifulSoup(open(path, 'rb'))
        url = ''

        for link in soup.select('link[rel]'):
            rel = link.get('rel')
            href = link.get('href', '')

            if rel == ['canonical'] and href:
                url = href
                break

        if not url:
            for meta in soup.select('meta[property]'):
                property = meta.get('property')
                content = meta.get('content', '')

                if property == 'og:url' and content:
                    url = content
                    break

        if not url:
            for like in soup.find_all('fb:like'):
                href = like.get('href', '')
                if href:
                    url = href
                    break

        # For wolfarm alpha.
        if not url:
            for a in soup.select('a[title]'):
                title = a.get('title')
                href = a.get('href', '')

                if title.startswith('Permanent Link') and href:
                    url = href
                    break
        print '%d: %s' % (id, url)
        #print url
        #shutil.copy(
        #    os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'gold', '%d.txt' % id)),
        #    os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '%03d.txt' % id))
        #)
        continue
        if url:
            # print url
            # continue
            if os.path.exists(os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', '%03d.json' % id))):
                continue
            print '[extractor] #%03d: %s' % (id, url)
            subprocess.call('cd "%(path)s" && phantomjs "%(extractor)s" "%(url)s" "%(label)03d" > "%(label)03d.log" 2>&1' % {
                'path': os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')),
                'extractor': extractor,
                'url': url,
                'label': id,
            }, shell=True)


if __name__ == '__main__':
    main()
