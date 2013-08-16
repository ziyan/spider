
__spider.namespace '__spider', (exports) ->
    'use strict'

    upload = (data) ->
        __spider.ui.info('Uploading ...')
        request = __spider.$.ajax
            type: 'POST'
            url: window.__spider_url + '/capture'
            dataType: 'json'
            crossDomain: true
            data: __spider.JSON.stringify(data)
            headers:
                'X-SPIDER': 'spider' # force a preflight

        request.done (data) ->
          if not data.selectors
            __spider.ui.success('Done! We are still learning. Try capture one more similar page. :)')
            return

          console.log __spider.$(data.selectors)

          __spider.$(data.selectors).css
            background: '#ffff00'

          __spider.ui.success('Done! Content highlighted :)')

        request.error (xhr, txt_status) ->
          __spider.ui.error('Something went wrong while uploading data: ' + txt_status)

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