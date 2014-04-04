
__spider.namespace '__spider.utils', (exports) ->
    'use strict'

    exports.is_valid = (value) ->
        re = /^[a-zA-Z][a-zA-Z0-9\-_]+$/
        return value and re.test(value)

    # get element description
    exports.element = (element, is_name_only) ->
        name = element.tagName.toLowerCase()
        return name if is_name_only

        classes = []
        for c in element.classList
            classes.push(c) if exports.is_valid(c)

        data =
            name: name
            id: if exports.is_valid(element.id) then element.id else ''
            classes: classes.sort()
        return data

    # generate tag path
    exports.path = (element, is_name_only) ->
        path = []
        while element
            break if element is document.body
            path.splice 0, 0, exports.element(element, is_name_only)
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
        defaults = document.defaultView.getComputedStyle(document.body)
        computed = document.defaultView.getComputedStyle(element)
        data = {}
        for key in computed
            # don't care about dimension, let bound track that
            continue if key in ['width', 'height', 'top', 'left', 'right', 'bottom']
            # don't care about webkit specific
            continue if key.charAt(0) is '-'
            # don't care about default value
            continue if computed[key] is defaults[key]
            data[key] = computed[key]
        
        return data

