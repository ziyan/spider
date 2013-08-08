url = 'http://www.theverge.com/2013/8/6/4594158/fitness-tracker-quantified-self-workout'
#url = 'http://www.amazon.com/gp/product/B004X1V1CS/ref=s9_simh_gw_p351_d0_i2?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=center-2&pf_rd_r=1AZ2019VKPDJGBSYZG8T&pf_rd_t=101&pf_rd_p=1389517282&pf_rd_i=507846'
#url = 'http://news.163.com/13/0807/09/95LRCHP20001124J.html'
#url = 'http://webdesign.tutsplus.com/tutorials/htmlcss-tutorials/the-role-of-table-layouts-in-responsive-web-design/'
#url = 'http://news.163.com/13/0807/11/95M23SMI0001124J.html'
#url = 'http://coffeescriptcookbook.com/chapters/classes_and_objects/class-methods-and-instance-methods'
#url = 'http://localhost:8888/'
#url = 'http://www.wired.com/business/2013/06/meditation-mindfulness-silicon-valley/'

page = require('webpage').create()

page.onResourceRequested = (request) ->
    #console.log 'Request ' + JSON.stringify request, undefined, 2

page.onResourceReceived = (response) ->
    #console.log 'Receive ' + JSON.stringify response, undefined, 2

page.open url, ->
    links = page.evaluate ->
        (link.href for link in document.querySelectorAll('a[href]'))

    nodes = page.evaluate ->
        try
            String.prototype.trim = -> @replace /^\s+|\s+$/g, ''

            build_tag_path = (element) ->
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

            nodes = []

            # walk over all text in the page
            walker = document.createTreeWalker document.body, NodeFilter.SHOW_TEXT, null, false
            while text = walker.nextNode()
                continue unless text.nodeValue.trim().length > 0

                # container node
                node = text.parentElement
                continue unless node.offsetWidth * node.offsetHeight > 0

                # find the parent node that is a block
                while node
                    computed = document.defaultView.getComputedStyle(node)
                    width = parseInt(computed.width)
                    height = parseInt(computed.height)
                    break if width * height > 0
                    node = node.parentElement
                continue unless node

                # have we seen this node?
                if node.spider
                    node.spider.text.push text.nodeValue
                    continue

                # collect features
                path = build_tag_path(node)
                computed = document.defaultView.getComputedStyle(node)

                node.spider =
                    node: path[path.length - 1]
                    path: path
                    text: [text.nodeValue]
                    html: node.innerHTML
                    offset:
                        width: node.offsetWidth
                        height: node.offsetHeight
                        top: node.offsetTop
                        left: node.offsetLeft
                    computed:
                        width: computed.width
                        height: computed.height
                        color: computed.color
                        lineHeight: computed.lineHeight
                        fontSize: computed.fontSize
                        fontWeight: computed.fontWeight
                        fontFamily: computed.fontFamily
                        fontStyle: computed.fontStyle
                        opacity: computed.opacity
                nodes.push node.spider

                node.style.border = '1px solid red'

            return nodes

        catch e
            return e

    page.render('test.jpg')

    console.log JSON.stringify nodes, undefined, 2

    phantom.exit()
