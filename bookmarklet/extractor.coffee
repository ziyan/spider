
__spider.namespace '__spider.extractor', (exports) ->
    'use strict'

    exports.extract_meta = ->

        # find title and description
        titles = (title.innerText for title in document.querySelectorAll('title'))
        descriptions = (meta.content for meta in document.querySelectorAll('meta[name="description"]'))
        
        # open graph title and description
        titles.push (meta.content for meta in document.querySelectorAll('meta[name="og:title"], meta[property="og:title"]'))...
        descriptions.push (meta.content for meta in document.querySelectorAll('meta[name="og:description"], meta[property="og:description"]'))...
        
        # twitter title and description
        titles.push (meta.content for meta in document.querySelectorAll('meta[name="twitter:title"], meta[property="twitter:title"]'))...
        descriptions.push (meta.content for meta in document.querySelectorAll('meta[name="twitter:description"], meta[property="twitter:description"]'))...

        data =
            url: window.location.href
            titles: titles
            descriptions: descriptions
        return data

    exports.extract_body = ->

        # computed style for body
        computed = {}
        for key in document.defaultView.getComputedStyle(document.body)
            # don't care about webkit specific
            continue if key.charAt(0) is '-'
            # don't care about default value
            computed[key] = document.defaultView.getComputedStyle(document.body)[key]

        body =
            scroll:
                top: document.documentElement.scrollTop or document.body.scrollTop
                left: document.documentElement.scrollLeft or document.body.scrollLeft
            bound: __spider.utils.bound(document.body)
            computed: computed
        return body

    exports.extract_links = ->
        (link.href for link in document.querySelectorAll('a[href]'))

    exports.extract_texts = ->
        texts = []

        # walk over all text in the page
        walker = document.createTreeWalker document.body, NodeFilter.SHOW_TEXT, null, false
        while text = walker.nextNode()
            continue unless text.nodeValue.trim().length > 0

            # container node
            node = text.parentElement
            bound = __spider.utils.bound(node)
            continue unless bound.width * bound.height > 0

            # find the parent node that is a block
            while node
                computed = document.defaultView.getComputedStyle(node)
                break if parseInt(computed.width) * parseInt(computed.height) > 0
                node = node.parentElement
            continue unless node

            # have we seen this node?
            if node.__spider
                node.__spider.text.push text.nodeValue
                continue

            # collect features
            node.__spider =
                element: __spider.utils.element(node)
                path: __spider.utils.path(node, true)
                selector: __spider.utils.path(node)
                text: [text.nodeValue]
                html: node.innerHTML
                bound: __spider.utils.bound(node)
                computed: __spider.utils.computed(node)
            texts.push node.__spider

        return texts

    exports.extract_images = ->
        images = []
        for node in document.querySelectorAll('img[src]')
            bound = __spider.utils.bound(node)
            continue unless bound.width * bound.height > 0
            
            images.push
                src: node.src
                element: __spider.utils.element(node)
                path: __spider.utils.path(node, true)
                selector: __spider.utils.path(node)
                bound: bound
                computed: __spider.utils.computed(node)
        return images

    exports.extract = ->
        data = exports.extract_meta()
        data['body'] = exports.extract_body()
        data['links'] = exports.extract_links()
        data['texts'] = exports.extract_texts()
        data['images'] = exports.extract_images()
        return data
