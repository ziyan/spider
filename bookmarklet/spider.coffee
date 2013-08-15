# namespace creation
((window) ->
    'use strict'

    namespace = (target, name, block) ->
        [target, name, block] = [window, arguments...] if arguments.length < 3
        top = target
        target = target[item] or= {} for item in name.split '.'
        block target, top

    namespace '__spider', (exports, top) ->
        exports.namespace = namespace

)(window)

# make sure we don't override existing $ or jQuery
__spider.$ = jQuery.noConflict(true)
