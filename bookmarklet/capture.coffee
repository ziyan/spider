
__spider.namespace '__spider.capture', (exports) ->
    'use strict'

    upload = (data) ->
        request = __spider.$.ajax
            type: 'POST'
            url: window.__spider_url + '/capture'
            dataType: 'json'
            data: JSON.stringify(data)

        request.done (data) ->
          __spider.ui.success('Done! :)')

        request.error (xhr, txt_status) ->
          __spider.ui.error('Something went wrong while uploading data: ' + txt_status)

    capture = ->
        data = __spider.extractor.extract()
        __spider.ui.info('Uploading ...')

        setTimeout ->
            upload data
        , 50

    exports.run = ->
        if not window.__spider_url
            __spider.ui.error('Bookmarklet outdated!')
            return

        __spider.ui.info('Capturing ...')
        setTimeout capture, 50

__spider.$ ->
    __spider.capture.run()