;(function($, undefined) {
    if (undefined === $.fn['ariCloner'])
        return ;

    var ie9 = /MSIE\s/.test(navigator.userAgent) && parseFloat(navigator.appVersion.split("MSIE")[1]) < 10,
        blank_image = !ie9
            ? "data:image/svg+xml;charset=utf-8,%3Csvg xmlns%3D'http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg' viewBox%3D'0 0 {{width}} {{height}}'%2F%3E"
            : 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';

    $.fn.ariCloner.defaults.confirmModal = function(message, callback) {
        AppHelper.confirm(message, callback);
    };

    $.fn.ariCloner.defaults.dataTypes = $.extend(
        true,
        $.fn.ariCloner.defaults.dataTypes, {
            'image': {
                set: function (val, key, el, item, dataItem) {
                    if (val > 0) {
                        var metaColumn = el.attr('data-ref-column'),
                            container = el.closest('.ari-wp-image-container'),
                            imgHolder = container.find('.ari-wp-image-holder'),
                            lazyLoad = imgHolder.attr('data-lazy-load') !== undefined;

                        if (metaColumn && dataItem[metaColumn]) {
                            var metaData = dataItem[metaColumn];

                            if (metaData.url) {
                                var img = $('<img />')
                                    .appendTo(imgHolder);

                                if (!lazyLoad)
                                    img.attr('src', metaData.url);
                                else {
                                    var width = 100,
                                        height = 100;

                                    if (metaData.width > 0 && metaData.height > 0) {
                                        width = metaData.width;
                                        height = metaData.height;

                                        img.attr('width', metaData.width);
                                        img.attr('height', metaData.height);
                                    }

                                    img.attr('src', blank_image.replace('{{width}}', width).replace('{{height}}', height));
                                    img.attr('data-url', metaData.url);

                                    imgHolder.addClass('ari-lazy-load');
                                };

                                container.addClass('has-image');
                            }
                        }
                    }

                    el.val(val);
                },

                get: function (el, key, item) {
                    return el.val();
                }
            }
        }
    );

    $.fn.ariCloner.defaults.messages = $.extend(
        $.fn.ariCloner.defaults.messages,
        ARI_QUIZ_CLONER.messages || {}
    );
})(jQuery);