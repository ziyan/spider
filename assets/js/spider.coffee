$ ->

    comma = (value) ->
        re = /\B(?=(\d{3})+(?!\d))/g
        return value.toString().replace(re, ',')

    $.getJSON 'https://spider.ziyan.net/stats', (data) ->
        $('header ul li:eq(0) strong').text comma(data.usage or 0)
        $('header ul li:eq(1) strong').text comma(data.sites or 0)
        $('header ul li:eq(2) strong').text comma(data.pages or 0)

    window['GoogleAnalyticsObject'] = 'ga'
    window.ga = window.ga or (-> (window.ga.q = window.ga.q or []).push arguments)
    window.ga.l = 1 * new Date()

    element = document.createElement('script')
    script = document.getElementsByTagName('script')[0]
    element.async = 1
    element.src = '//www.google-analytics.com/analytics.js'
    script.parentNode.insertBefore element, script

    window.ga 'create', 'UA-34085887-2', 'ziyan.github.io'
    window.ga 'send', 'pageview'