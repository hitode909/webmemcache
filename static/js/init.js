$(function() {
    $.fn.extend({
        log: function(message) {
            var elem = $(this).logElement();
            elem.text(elem.text() + (new Date()) + ': ' + uneval(message) + "\n");
            return 'LOGGED';
        },
        logElement: function() {
            if ($("div.log", this).length > 0) {
                return $("div.log pre", this);
            }
            var elem = $('<div></div>').addClass('log')
            var pre = $('<pre></pre>');
            elem.append(pre);
            this.append(elem);
            return pre;
        },
        setupForm: function() {
            if ($('form', this).length > 0) return false;
            var source = $(this).text();
            var $form = $('<form><textarea class="code">' + source + '</textarea><input type="submit" value="eval"></input>')
            $form.data('source', source);
            $(this).replaceWith($form);
            $form.submit(function() {
                var code = $("textarea.code", this).attr('value');
                try {
                    var self = this;
                    var log = function(m) {
                        return $(self).log(m);
                    }
                    var res = eval(code);
                    if (res != 'LOGGED') log(res);
                } catch(e) {
                    $(this).log(e);
                }
                return false;
            });
        }
    });
    $('div.can-exec').click(function() {
        $(this).setupForm();
    });
});
