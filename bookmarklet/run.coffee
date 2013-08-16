
__spider.namespace '__spider', (exports) ->
    'use strict'

    upload = (data) ->
        __spider.ui.info('Uploading ...')

        xhr = new XMLHttpRequest()
        xhr.open 'POST', window.__spider_url + '/capture', true
        xhr.setRequestHeader 'X-Spider', 'spider'
        xhr.setRequestHeader 'Content-Type', 'application/json'
        xhr.onreadystatechange = ->
            return if xhr.readyState != 4
            if xhr.status != 200 or not xhr.response
                __spider.ui.error('Something went wrong while uploading data.')
                return

            data = __spider.JSON.parse(xhr.response)
            if not data.selectors
                __spider.ui.success('Done! We are still learning. Try capture one more similar page. :)')
                return

            console.log __spider.$(data.selectors)

            __spider.$(data.selectors).css
                background: '#ffff00'

            __spider.ui.success('Done! Content highlighted :)')
        xhr.send __spider.JSON.stringify(data)

    capture = ->
        __spider.ui.info('Capturing ...')
        setTimeout ->
            data = __spider.extractor.extract()
            upload data
        , 50

    exports.run = ->
        return if not window.__spider_url
        return if window.__spider_run
        window.__spider_run = true

        capture()        

__spider.$ ->
    __spider.run()
