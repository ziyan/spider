
__spider.namespace '__spider.ui', (exports) ->
    'use strict'

    build_ui = ->
        ui = __spider.$('div#__spider')
        return ui if ui.length

        ui = __spider.$('<div />')
        ui.attr
            id: '__spider'
        ui.css
            position: 'fixed'
            zIndex: 999999999
            top: 15
            left: 15
            background: '#2f96b4'
            color: 'white'
            fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif'
            fontSize: '14px'
            lineHeight: '20px'
            fontWeight: 'bold'
            padding: '10px 15px'
        ui.text('Loading ...')
        ui.insertBefore(__spider.$(document.body))
        return ui

    exports.info = (html) ->
        ui = build_ui()
        ui.css
            background: '#2f96b4'
        ui.html(html)

    exports.success = (html) ->
        ui = build_ui()
        ui.css
            background: '#51a351'
        ui.html(html)

    exports.error = (html) ->
        ui = build_ui()
        ui.css
            background: '#da4f49'
        ui.html(html)