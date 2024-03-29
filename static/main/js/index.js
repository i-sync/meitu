// awesome.js

// patch for lower-version IE:

if (! window.console) {
    window.console = {
        log: function() {},
        info: function() {},
        error: function () {},
        warn: function () {},
        debug: function () {}
    };
}

// patch for string.trim():

if (! String.prototype.trim) {
    String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g, '');
    };
}

if (! Number.prototype.toDateTime) {
    var replaces = {
        'yyyy': function(dt) {
            return dt.getFullYear().toString();
        },
        'yy': function(dt) {
            return (dt.getFullYear() % 100).toString();
        },
        'MM': function(dt) {
            var m = dt.getMonth() + 1;
            return m < 10 ? '0' + m : m.toString();
        },
        'M': function(dt) {
            var m = dt.getMonth() + 1;
            return m.toString();
        },
        'dd': function(dt) {
            var d = dt.getDate();
            return d < 10 ? '0' + d : d.toString();
        },
        'd': function(dt) {
            var d = dt.getDate();
            return d.toString();
        },
        'hh': function(dt) {
            var h = dt.getHours();
            return h < 10 ? '0' + h : h.toString();
        },
        'h': function(dt) {
            var h = dt.getHours();
            return h.toString();
        },
        'mm': function(dt) {
            var m = dt.getMinutes();
            return m < 10 ? '0' + m : m.toString();
        },
        'm': function(dt) {
            var m = dt.getMinutes();
            return m.toString();
        },
        'ss': function(dt) {
            var s = dt.getSeconds();
            return s < 10 ? '0' + s : s.toString();
        },
        's': function(dt) {
            var s = dt.getSeconds();
            return s.toString();
        },
        'a': function(dt) {
            var h = dt.getHours();
            return h < 12 ? 'AM' : 'PM';
        }
    };
    var token = /([a-zA-Z]+)/;
    Number.prototype.toDateTime = function(format) {
        var fmt = format || 'yyyy-MM-dd hh:mm:ss'
        var dt = new Date(this * 1000);
        var arr = fmt.split(token);
        for (var i=0; i<arr.length; i++) {
            var s = arr[i];
            if (s && s in replaces) {
                arr[i] = replaces[s](dt);
            }
        }
        return arr.join('');
    };
    Number.prototype.toFileSize = function() {
        var i = Math.floor( Math.log(this) / Math.log(1024) );
        return ( this / Math.pow(1024, i) ).toFixed(2) * 1 + ' ' + ['B', 'KB', 'MB', 'GB', 'TB'][i];
    };
}

function encodeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

// parse query string as object:

function parseQueryString() {
    var
        q = location.search,
        r = {},
        i, pos, s, qs;
    if (q && q.charAt(0)==='?') {
        qs = q.substring(1).split('&');
        for (i=0; i<qs.length; i++) {
            s = qs[i];
            pos = s.indexOf('=');
            if (pos <= 0) {
                continue;
            }
            r[s.substring(0, pos)] = decodeURIComponent(s.substring(pos+1)).replace(/\+/g, ' ');
        }
    }
    return r;
}

function gotoPage(i) {
    var r = parseQueryString();
    r.page = i;
    location.assign('?' + $.param(r));
}

function paramsToObject(entries) {
  let result = {}
  for(let entry of entries) { // each 'entry' is a [key, value] tupple
    const [key, value] = entry;
    result[key] = value;
  }
  return result;
}

function refresh() {
    var
        t = new Date().getTime(),
        url = location.pathname;
    if (location.search) {
        url = url + location.search + '&t=' + t;
    }
    else {
        url = url + '?t=' + t;
    }
    location.assign(url);
}

function refresh_param(obj) {
    var url = location.pathname;
    if (location.search) {
        var origin_param = location.search.substring(1);
        var origin_param_obj = paramsToObject(new URLSearchParams(origin_param).entries());
        obj = Object.assign(origin_param_obj, obj);
    }
    url = url + '?' + new URLSearchParams(obj).toString();
    location.assign(url);
}

function redirect_param(url, obj)
{
    if (location.search) {
        var origin_param = location.search.substring(1);
        var origin_param_obj = paramsToObject(new URLSearchParams(origin_param).entries());
        obj = Object.assign(origin_param_obj, obj);
    }
    url = url + '?' + new URLSearchParams(obj).toString();
    location.assign(url);
}

function toSmartDate(timestamp) {
    if (typeof(timestamp)==='string') {
        timestamp = parseInt(timestamp);
    }
    if (isNaN(timestamp)) {
        return '';
    }

    var
        today = new Date(g_time),
        now = today.getTime(),
        s = '1分钟前',
        t = now - timestamp;
    if (t > 604800000) {
        // 1 week ago:
        var that = new Date(timestamp);
        var
            y = that.getFullYear(),
            m = that.getMonth() + 1,
            d = that.getDate(),
            hh = that.getHours(),
            mm = that.getMinutes();
        s = y===today.getFullYear() ? '' : y + '年';
        s = s + m + '月' + d + '日' + hh + ':' + (mm < 10 ? '0' : '') + mm;
    }
    else if (t >= 86400000) {
        // 1-6 days ago:
        s = Math.floor(t / 86400000) + '天前';
    }
    else if (t >= 3600000) {
        // 1-23 hours ago:
        s = Math.floor(t / 3600000) + '小时前';
    }
    else if (t >= 60000) {
        s = Math.floor(t / 60000) + '分钟前';
    }
    return s;
}



$(function() {
    $('.x-smartdate').each(function() {
        $(this).removeClass('x-smartdate').text(toSmartDate($(this).attr('date')));
    });
});

// JS Template:

function Template(tpl) {
    var
        fn,
        match,
        code = ['var r=[];\nvar _html = function (str) { return str.replace(/&/g, \'&amp;\').replace(/"/g, \'&quot;\').replace(/\'/g, \'&#39;\').replace(/</g, \'&lt;\').replace(/>/g, \'&gt;\'); };'],
        re = /\{\s*([a-zA-Z\.\_0-9()]+)(\s*\|\s*safe)?\s*\}/m,
        addLine = function (text) {
            code.push('r.push(\'' + text.replace(/\'/g, '\\\'').replace(/\n/g, '\\n').replace(/\r/g, '\\r') + '\');');
        };
    while (match = re.exec(tpl)) {
        if (match.index > 0) {
            addLine(tpl.slice(0, match.index));
        }
        if (match[2]) {
            code.push('r.push(String(this.' + match[1] + '));');
        }
        else {
            code.push('r.push(_html(String(this.' + match[1] + ')));');
        }
        tpl = tpl.substring(match.index + match[0].length);
    }
    addLine(tpl);
    code.push('return r.join(\'\');');
    fn = new Function(code.join('\n'));
    this.render = function (model) {
        return fn.apply(model);
    };
}

// extends jQuery.form:

$(function () {
    console.log('Extends $form...');
    $.fn.extend({
        showFormError: function (err) {
            return this.each(function () {
                var
                    $form = $(this),
                    $alert = $form && $form.find('.ui.error.message ul li'),
                    fieldName = err && err.data;
                if (! $form.is('form')) {
                    console.error('Cannot call showFormError() on non-form object.');
                    return;
                }
                $form.find('input').closest('.field').removeClass('error');
                $form.find('select').closest('.field').removeClass('error');
                $form.find('textarea').closest('.field').removeClass('error');
                if ($alert.length === 0) {
                    console.warn('Cannot find .ui.error.message element.');
                    return;
                }
                if (err) {
                    $alert.text(err.message ? err.message : (err.error ? err.error : err));///.removeClass('uk-hidden').show();
                    //if (($alert.offset().top - 60) < $(window).scrollTop()) {
                    //    $('html,body').animate({ scrollTop: $alert.offset().top - 60 });
                    //}
                    if (fieldName) {
                        $form.find('[name=' + fieldName + ']').closest('.field').addClass('error');
                    }

                    $form.removeClass('success').addClass('error');
                }
                else {
                    //$alert.addClass('uk-hidden').hide();
                    $form.removeClass('error').addClass('success');
                }
            });
        },
        showFormLoading: function (isLoading) {
            return this.each(function () {
                var
                    $form = $(this);
                    //$submit = $form && $form.find('button[type=submit]'),
                    //$buttons = $form && $form.find('button');
                    //$i = $submit && $submit.find('i'),
                    //iconClass = $i && $i.attr('class');
                if (! $form.is('form')) {
                    console.error('Cannot call showFormLoading() on non-form object.');
                    return;
                }
                /*if (!iconClass || iconClass.indexOf('uk-icon') < 0) {
                    console.warn('Icon <i class="uk-icon-*>" not found.');
                    return;
                }*/
                if (isLoading) {
                    //$buttons.attr('disabled', 'disabled');
                    //$i && $i.addClass('uk-icon-spinner').addClass('uk-icon-spin');
                    $form.addClass('loading');
                }
                else {
                    //$buttons.removeAttr('disabled');
                    //$i && $i.removeClass('uk-icon-spinner').removeClass('uk-icon-spin');
                    $form.removeClass('loading');
                }
            });
        },
        postJSON: function (url, data, callback) {
            if (arguments.length===2) {
                callback = data;
                data = {};
            }
            return this.each(function () {
                var $form = $(this);
                $form.showFormError();
                $form.showFormLoading(true);
                _httpJSON('POST', url, data, function (err, r) {
                    if (err) {
                        $form.showFormError(err);
                        $form.showFormLoading(false);
                    }
                    callback && callback(err, r);
                });
            });
        }
    });
});

// ajax submit form:

function _httpJSON(method, url, data, callback) {
    var opt = {
        type: method,
        dataType: 'json'
    };
    if (method==='GET') {
        opt.url = url + '?' + data;
    }
    if (method==='POST') {
        opt.url = url;
        opt.data = JSON.stringify(data || {});
        opt.contentType = 'application/json';
    }
    $.ajax(opt).done(function (r) {
        if (r && r.error) {
            return callback(r);
        }
        return callback(null, r);
    }).fail(function (jqXHR, textStatus) {
        return callback({'error': 'http_bad_response', 'data': '' + jqXHR.status, 'message': '网络好像出问题了 (HTTP ' + jqXHR.status + ')'});
    });
}

function getJSON(url, data, callback) {
    if (arguments.length===2) {
        callback = data;
        data = {};
    }
    if (typeof (data)==='object') {
        var arr = [];
        $.each(data, function (k, v) {
            arr.push(k + '=' + encodeURIComponent(v));
        });
        data = arr.join('&');
    }
    _httpJSON('GET', url, data, callback);
}

function postJSON(url, data, callback) {
    if (arguments.length===2) {
        callback = data;
        data = {};
    }
    _httpJSON('POST', url, data, callback);
}

// extends Vue
function register_paging_components(app)
{
    app.component('vc-pagination', {
        props: ['p'],
        template: '<nav aria-label="Page navigation">  <ul class="pagination">\
                <li v-if="p.has_prev" class="page-item"><a class="page-link" @click.prevent="gotoPage(p.page_index - 1)"  href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li> \
                <li v-else class="page-item disabled"><a class="page-link" href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li> \
                \
                <template v-for="pn in p.prefix">\
                    <li v-if="p.page_index == pn" class="page-item disabled"><a class="page-link" href="#" v-text="pn"></a></li> \
                    <li v-else class="page-item"><a class="page-link"  @click.prevent="gotoPage(pn)" href="#" v-text="pn"></a></li> \
                </template>\
                \
                <a v-if="p.page_list[0] > 4" class="disabled item">...</a> \
                \
                <template v-for="pn in p.page_list">\
                    <li v-if="pn == p.page_index" class="page-item disabled"><a class="page-link" href="#" v-text="pn"></a></li> \
                    <li v-else class="page-item"><a class="page-link"  @click.prevent="gotoPage(pn)" href="#" v-text="pn"></a></li> \
                </template>\
                \
                <a v-if="p.page_list[p.page_show-1] < (p.page_count-3)" class="disabled item">...</a> \
                \
                <template v-for="pn in p.suffix">\
                    <li v-if="(p.page_index == pn) && (pn != 1)" class="page-item disabled"><a class="page-link" href="#" v-text="pn"></a></li> \
                    <li v-if="(p.page_index != pn) && (pn != 1) && (p.item_count != 0)" class="page-item"><a class="page-link"  @click.prevent="gotoPage(pn)" href="#" v-text="pn"></a></li> \
                </template>\
                \
                <li v-if="p.has_next" class="page-item"><a class="page-link" @click.prevent="gotoPage(p.page_index+1)" href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li> \
                <li v-else class="page-item disabled"><a class="page-link" href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li> \
                </ul></nav>',
        computed: {
            pl: function() {
                var left = 2;
                var right = this.p.page_count;
                var l = [];
                if (this.p.page_count > this.p.page_show) {
                    left = this.p.page_index - parseInt(this.p.page_show/2);
                    if (left < 2) {
                        left = 2;
                    }
                    right = left + this.p.page_show;
                    if (right > this.p.page_count) {
                        right = this.p.page_count;
                        left = right - this.p.page_show;
                    }
                }
                // 返回的列表不包含首项及末项
                while (left < right) {
                    l.push(left);
                    left++;
                }
                return l;
            }
        }, 
        methods:{
            gotoPage: function(i) {
                var r = parseQueryString();
                r.page = i;
                location.assign('?' + $.param(r));
            }
        }
    });
}

function redirect(url) {
    var
        hash_pos = url.indexOf('#'),
        query_pos = url.indexOf('?'),
        hash = '';
    if (hash_pos >=0 ) {
        hash = url.substring(hash_pos);
        url = url.substring(0, hash_pos);
    }
    url = url + (query_pos >= 0 ? '&' : '?') + 't=' + new Date().getTime() + hash;
    console.log('redirect to: ' + url);
    location.assign(url);
}

// init:

function _bindSubmit($form) {
    $form.submit(function (event) {
        event.preventDefault();
        showFormError($form, null);
        var
            fn_error = $form.attr('fn-error'),
            fn_success = $form.attr('fn-success'),
            fn_data = $form.attr('fn-data'),
            data = fn_data ? window[fn_data]($form) : $form.serialize();
        var
            $submit = $form.find('button[type=submit]'),
            $i = $submit.find('i'),
            iconClass = $i.attr('class');
        if (!iconClass || iconClass.indexOf('uk-icon') < 0) {
            $i = undefined;
        }
        $submit.attr('disabled', 'disabled');
        $i && $i.addClass('uk-icon-spinner').addClass('uk-icon-spin');
        postJSON($form.attr('action-url'), data, function (err, result) {
            $i && $i.removeClass('uk-icon-spinner').removeClass('uk-icon-spin');
            if (err) {
                console.log('postJSON failed: ' + JSON.stringify(err));
                $submit.removeAttr('disabled');
                fn_error ? fn_error() : showFormError($form, err);
            }
            else {
                var r = fn_success ? window[fn_success](result) : false;
                if (r===false) {
                    $submit.removeAttr('disabled');
                }
            }
        });
    });
    $form.find('button[type=submit]').removeAttr('disabled');
}

$(function () {
    $('form').each(function () {
        var $form = $(this);
        if ($form.attr('action-url')) {
            _bindSubmit($form);
        }
    });
});

$(function() {
    if (location.pathname === '/' || location.pathname.indexOf('/blog')===0) {
        $('li[data-url=blogs]').addClass('uk-active');
    }
});

function _display_error($obj, err) {
    if ($obj.is(':visible')) {
        $obj.hide();
    }
    var msg = err.message || String(err);
    var L = ['<div class="ui header">'];
    L.push('<p>Error: ');
    L.push(msg);
    L.push('</p><p>Code: ');
    L.push(err.error || '500');
    L.push('</p></div>');
    $obj.html(L.join('')).slideDown();
}

function error(err) {
    _display_error($('#error'), err);
}

function fatal(err) {
    _display_error($('#loading'), err);
}

/* the textarea can capture the tab key. */
function captureTab(e) {
    if(e.keyCode === 9) { // tab was pressed
        var target = e.target;
        // get caret position/selection
        var start = target.selectionStart;
        var end = target.selectionEnd;

        var value = target.value;

        // set textarea value to: text before caret + tab + text after caret
        target.value = value.substring(0, start)
                    + "\t"
                    + value.substring(end);

        // put caret at right position again (add one for the tab)
        target.selectionStart = target.selectionEnd = start + 1;

        // prevent the focus lose
        e.preventDefault();
    }
}

$(function(){
    document.querySelectorAll("textarea").forEach(function(textarea){
        textarea.addEventListener('keydown',captureTab, false);
    });
});


// 导航栏菜单项自动设置选中状态
/*
$(function() {
    var navItem = $('#main-menu a');
    var i = 0;
    // i从2开始，跳过第一个href＝"/"导航菜单项
    for (i = 2; i < navItem.length; i++) {
        var href = $(navItem[i]).attr('href');
        href = href.lastIndexOf('/') <=0 ? href : href.slice(0, href.lastIndexOf('/'));
        if (location.pathname.indexOf(href) == 0) {
            $(navItem[i]).addClass('active');
            break;
        }
    }
    if (i == navItem.length) {
        $(navItem[1]).addClass('active');
    }
});*/


function getQueryString(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.href) || [, ""])[1].replace(/\+/g, '%20')) || null
}