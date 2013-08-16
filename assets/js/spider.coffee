$ ->
    comma = (value) ->
        re = /\B(?=(\d{3})+(?!\d))/g
        return value.toString().replace(re, ',')

    $.getJSON 'https://spider.ziyan.net/stats', (data) ->
        $('header ul li:eq(0) strong').text comma(data.usage or 0)
        $('header ul li:eq(1) strong').text comma(data.sites or 0)
        $('header ul li:eq(2) strong').text comma(data.pages or 0)