system = require('system')
fs = require('fs')
page = require('webpage').create()

# set a big enough viewport size,
# this needs to be static
page.viewportSize =
    width: 1600
    height: 4000

# debug info
page.onResourceRequested = (request) ->
    system.stderr.write JSON.stringify request, undefined, 2
    system.stderr.write '\n\n'

# debug info
page.onResourceReceived = (response) ->
    system.stderr.write JSON.stringify response, undefined, 2
    system.stderr.write '\n\n'

# debug info
page.onConsoleMessage = (message) ->
    system.stderr.write message
    system.stderr.write '\n\n'

# handle page loadd
page.onLoadFinished = (status) ->

    # bail on network issue
    return phantom.exit() if status is not 'success'

    # inject javascripts helpers needed
    page.evaluate ->
        String.prototype.trim = -> @replace /^\s+|\s+$/g, ''

        # namespace creation
        ((window) ->
            'use strict'

            window.__slice = [].slice

            namespace = (target, name, block) ->
                [target, name, block] = [window, arguments...] if arguments.length < 3
                top = target
                target = target[item] or= {} for item in name.split '.'
                block target, top

            namespace 'spider', (exports, top) ->
                exports.namespace = namespace

        )(window)

        # spider.utils
        spider.namespace 'spider.utils', (exports) ->
            'use strict'

            exports.nth = (element) ->
                parent = element.parentElement
                id = parent.id
                parent.id = 'spider' + parseInt(Math.random() * 100000)
                children = document.querySelectorAll('#' + parent.id + ' > ' + element.tagName)
                parent.id = id
                for el, index in children
                    return index + 1 if el is element
                return 0

            # get element description
            exports.element = (element) ->
                name = element.tagName.toLowerCase()

                # classes
                classes = ('.' + c for c in (c for c in element.classList).sort()).join('')

                # id
                id = if element.id then '#' + element.id else ''

                # nth-of-type
                nth = exports.nth(element)
                nth = if nth > 0 then ':nth-of-type(' + nth + ')' else ''

                return name + id + classes + nth

            # generate tag path
            exports.path = (element) ->
                path = []
                while element
                    break if element is document.body
                    path.splice 0, 0, exports.element(element)
                    element = element.parentElement
                return path.join(' > ')

            # calculate block bound
            exports.bound = (element) ->
                scrollTop = document.documentElement.scrollTop or document.body.scrollTop
                scrollLeft = document.documentElement.scrollLeft or document.body.scrollLeft
                rect = element.getBoundingClientRect()
                bound =
                    width: rect.width
                    height: rect.height
                    left: rect.left + scrollLeft
                    top: rect.top + scrollTop 
                return bound

            # calculate computed css
            exports.computed = (element) ->
                computed = document.defaultView.getComputedStyle(element)
                data = {}
                for key in computed
                    # don't care about dimension, let bound track that
                    continue if key in ['width', 'height', 'top', 'left', 'right', 'bottom']
                    # don't care about webkit specific
                    continue if key.charAt(0) is '-'
                    data[key] = computed[key]
                return data

    # extract page basic data
    data = page.evaluate ->
        
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
            body:
                scroll:
                    top: document.documentElement.scrollTop or document.body.scrollTop
                    left: document.documentElement.scrollLeft or document.body.scrollLeft
                bound: spider.utils.bound(document.body)
                computed: spider.utils.computed(document.body)
        return data

    # extract links
    data.links = page.evaluate ->
        (link.href for link in document.querySelectorAll('a[href]'))

    # extract data
    data.texts = page.evaluate ->
        texts = []

        # walk over all text in the page
        walker = document.createTreeWalker document.body, NodeFilter.SHOW_TEXT, null, false
        while text = walker.nextNode()
            continue unless text.nodeValue.trim().length > 0

            # container node
            node = text.parentElement
            bound = spider.utils.bound(node)
            continue unless bound.width * bound.height > 0

            # find the parent node that is a block
            while node
                computed = document.defaultView.getComputedStyle(node)
                break if parseInt(computed.width) * parseInt(computed.height) > 0
                node = node.parentElement
            continue unless node

            # have we seen this node?
            if node.spider
                node.spider.text.push text.nodeValue
                continue

            # collect features
            element = spider.utils.element(node)
            path = spider.utils.path(node)

            node.spider =
                element: element
                path: path
                text: [text.nodeValue]
                html: node.innerHTML
                bound: spider.utils.bound(node)
                computed: spider.utils.computed(node)
            texts.push node.spider

            # debug
            # node.style.border = '1px solid red'

        return texts

    # extract images
    data.images = page.evaluate ->
        images = []
        for image in document.querySelectorAll('img[src]')
            bound = spider.utils.bound(image)
            continue unless bound.width * bound.height > 0
            element = spider.utils.element(image)
            path = spider.utils.path(image)
            
            images.push
                src: image.src
                element: element
                path: path
                bound: bound
                computed: spider.utils.computed(image)
        return images

    # write json
    fs.write(system.args[2] + '.json', JSON.stringify(data, undefined, 2))

    # debug
    # page.render(system.args[2] + '.png')

    # done
    phantom.exit()

# argument check
unless system.args.length is 3
    system.stderr.write 'Usage: phantomjs ' + system.args[0] + ' <url> <label>\n\n'
    phantom.exit()

# load page
page.open system.args[1]

