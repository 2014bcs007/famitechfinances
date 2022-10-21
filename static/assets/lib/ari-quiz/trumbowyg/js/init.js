;(function($) {
	if (!$.fn.trumbowyg)
		return ;
	
	var oldHadler = $.fn.trumbowyg;
	
	$.fn.trumbowyg = function(options, params) {
        options = options || {};

        if (options === Object(options) || !options) {
            if (!options)
                options = {};

            if (!options.svgPath && ARI_TRUMBOWYG.svgPath)
                options.svgPath = ARI_TRUMBOWYG.svgPath;

            if (!options.lang) {
                var currentLang = ARI_TRUMBOWYG.lang.toLowerCase(),
                    optLang = null;

                if (jQuery.trumbowyg.langs[currentLang]) {
                    optLang = currentLang;
                } else {
                    var mainLang = currentLang.split('_')[0];

                    if (jQuery.trumbowyg.langs[mainLang]) {
                        optLang = mainLang;
                    }
                }

                if (optLang)
                    options.lang = optLang;
            }
        }

        oldHadler.call(this, options, params);
	};
})(jQuery);