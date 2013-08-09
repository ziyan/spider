system = require('system')
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

            # get element description
            exports.element = (element) ->
                name = element.tagName.toLowerCase()
                classes = (c for c in element.classList)
                id = element.id
                data =
                    name: name
                    classes: classes
                    id: id
                return data

            # generate tag path
            exports.path = (element) ->
                path = []
                while element
                    path.splice 0, 0, exports.element(element)
                    break if element is document.body
                    element = element.parentElement
                return path

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
                data =
                    width: computed.width
                    height: computed.height
                    color: computed.color
                    lineHeight: computed.lineHeight
                    fontSize: computed.fontSize
                    fontWeight: computed.fontWeight
                    fontFamily: computed.fontFamily
                    fontStyle: computed.fontStyle
                    opacity: computed.opacity
                return data

    # extract page basic data
    data = page.evaluate ->
        data =
            url: window.location.href
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
            node.style.border = '1px solid red'

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

    # debug
    console.log JSON.stringify data, undefined, 2
    #console.log JSON.stringify data

    # debug
    page.render(system.args[2] + '.png')

    # done
    phantom.exit()

# argument check
unless system.args.length is 3
    system.stderr.write 'Usage: phantomjs ' + system.args[0] + ' <url> <label>\n\n'
    phantom.exit()

# load page
page.open system.args[1]

