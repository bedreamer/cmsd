// 主定时器周期
var period_in_ms = 500;
// 定时器句柄
var handle = null;
// 全局刷新定时器
var global_period = 10 * 1000; // 10 s
var global_counter = 0;

// all object in this list
var api_objects_list = [];

// 所有已经发起请求的对象在这个列表中
var api_object_pendding = [];

var global_host = '192.168.2.106:8083';
var global_root = '/v1.0/realtime';

// 将一个api对象附加到下一次请求队列中
function api_append(api) {
    api_objects_list.push(api);
}

// API访问路径
function ApiObject(dom, api, format) {
    this.dom = dom;
    this.api = api;
    this.path = null;
    this.format = format;
    this.type = null;
}
ApiObject.prototype.apipath = function (host, root) {
    if ( this.path ) {
        return this.path;
    }

    var api_re = /api:\/\//;
    var collector_re = /collector:\/\//;
    if ( this.api.match(api_re) ) {
        this.type = 'api';
        head = "http://" + host + root;
        this.path = this.api.replace("api://", head);
        return this.path;
    } else if ( this.api.match(collector_re) ) {
        this.type = 'collector';
        this.path = this.api.slice("collector://".length, this.api.length);
        return this.path;
    }
};
ApiObject.prototype.update = function (data) {
    if ( data.status === 'ok') {
        if ( this.type === 'api' ) {
            var x = this.parser_format(data.data);
            $(this.dom).html(x);
        } else {
            //console.log(data.data);
        }
    } else {
       $(this.dom).html("!");
    }
};
ApiObject.prototype.parser_format = function(data) {
    if ( this.k === null ) {
        return data;
    }
    if ( this.k === undefined ) {
        if ( this.format.length === 0 ) {
            this.k = null;
            return data;
        }

        var items = {};
        var arr = this.format.split(';');
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].match(/.+=.+/)) {
                var item = arr[i].split('=');
                items[item[0]] = Number(item[1]);
            }
        }

        this.k = items.k ? items.k : 1;
        this.b = items.b ? items.b : 0;
        this.mask = items.mask ? items.mask : 0x7fffffff;
        this.dot = items.dot ? items.dot : 0;
    }

    if ( typeof data !== 'number') {
        return data;
    }

    var v = (data & this.mask) * this.k + this.b;
    return v.toFixed(this.dot);
};


// ajax 请求完成回调函数, 将api对象从pendding 列表中移除
function ajax_get_complete(respons, status) {
    var idx = api_object_pendding.indexOf(this.api);
    if ( idx >= 0 ) {
        api_object_pendding.splice(idx, 1);
    }
    if ( api_object_pendding.length === 0 ) {
        console.log("query done.");
    }
}

// ajax 请求成功
function ajax_get_success(data) {
    this.api.update(data);
}

// 新建一个API请求对象
function ApiAjaxOptions(url, api) {
    this.api = api;
    this.url = url;
}

function main_loop() {
    // 1. 当api_object_pendding 为空时才能发起下一次大循环
    if ( api_object_pendding.length > 0 || api_objects_list.length === 0 ) {
        return;
    }

    // 2. 大循环计时器
    if ( global_counter > 0 ) {
        global_counter = global_counter - period_in_ms;
        return;
    }

    // 3. 一次性将所有object对象添加到查询请求队列中
    for ( var i = 0; i < api_objects_list.length; i ++ ) {
        var object = api_objects_list[i];
        api_object_pendding.push(object);
    }

    global_counter = global_period;
    // 4. 依次发起查询请求
    for ( var i = 0; i < api_object_pendding.length; i ++ ) {
        var object = api_object_pendding[i];
        $.ajax({
            type: "GET",
            url: object.apipath(global_host, global_root),
            api: object,
            complete: ajax_get_complete,
            success: ajax_get_success,
        });
    }
}

// 开始数据循环查询
function api_begin_loop() {
    handle = setInterval(main_loop, period_in_ms);
}
