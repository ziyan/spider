#url = 'http://www.theverge.com/2013/8/6/4594158/fitness-tracker-quantified-self-workout'
#url = 'http://www.amazon.com/gp/product/B004X1V1CS/ref=s9_simh_gw_p351_d0_i2?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=center-2&pf_rd_r=1AZ2019VKPDJGBSYZG8T&pf_rd_t=101&pf_rd_p=1389517282&pf_rd_i=507846'
#url = 'http://news.163.com/13/0807/09/95LRCHP20001124J.html'
#url = 'http://webdesign.tutsplus.com/tutorials/htmlcss-tutorials/the-role-of-table-layouts-in-responsive-web-design/'
#url = 'http://news.163.com/13/0807/11/95M23SMI0001124J.html'
#url = 'http://coffeescriptcookbook.com/chapters/classes_and_objects/class-methods-and-instance-methods'
#url = 'http://localhost:8888/'
#url = 'http://www.wired.com/business/2013/06/meditation-mindfulness-silicon-valley/'

system = require('system')
page = require('webpage').create()

page.viewportSize =
    width: 1600
    height: 4000

page.onResourceRequested = (request) ->
    system.stderr.write JSON.stringify request, undefined, 2
    system.stderr.write '\n\n'

page.onResourceReceived = (response) ->
    system.stderr.write JSON.stringify response, undefined, 2
    system.stderr.write '\n\n'

page.onConsoleMessage = (message) ->
    system.stderr.write message
    system.stderr.write '\n\n'

page.onLoadFinished = (status) ->
    # bail on network issue
    return phantom.exit() if status is not 'success'

    # inject javascripts helpers needed
    page.evaluate ->
        String.prototype.trim = -> @replace /^\s+|\s+$/g, ''

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

        spider.namespace 'spider.utils', (exports) ->
            'use strcit'

            exports.path = (element) ->
                path = []
                while element
                    name = element.tagName.toLowerCase()
                    classes = (c for c in element.classList)
                    id = element.id
                    path.splice 0, 0,
                        name: name
                        classes: classes
                        id: id
                    break if element is document.body
                    element = element.parentElement
                return path

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

    # extract basic data
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
    links = page.evaluate ->
        (link.href for link in document.querySelectorAll('a[href]'))

    # extract data
    texts = page.evaluate ->
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
            path = spider.utils.path(node)

            node.spider =
                element: path[path.length - 1]
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
    images = page.evaluate ->
        images = []
        for image in document.querySelectorAll('img[src]')
            bound = spider.utils.bound(image)
            continue unless bound.width * bound.height > 0
            path = spider.utils.path(image)
            images.push
                src: image.src
                element: path[path.length - 1]
                path: path
                bound: bound
                computed: spider.utils.computed(image)
        return images

    data.links = links
    data.texts = texts
    data.images = images

    # debug
    console.log JSON.stringify data, undefined, 2
    #console.log JSON.stringify data

    # debug
    page.render('test.jpg')

    phantom.exit()

# load page
page.open system.args[1]
