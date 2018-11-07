// coding: utf8
$(document).ready(function () {
    var host = $.url.get("host", "192.168.2.106");
    var port = $.url.get("port", 8083);
    var datasource = '/v1.0/realtime/系统配置参数';
    console.log(host, port);

    $("#save").click(function () {
        var input = $("input");
        var config = {};
        for (var i = 0; i < input.length; i++) {
            var name = $(input[i]).attr('name');
            var type = $(input[i]).attr('valuetype');
            var value = $(input[i]).val();
            if (name.match(/\S+_\d+/)) {
                var name = name.split('_')[0];
                if (type === 'number') {
                    value = Number(value);
                }

                if (config[name]) {
                    config[name].push(value);
                } else {
                    config[name] = [value];
                }
            } else {
                if (type === 'number') {
                    config[name] = Number(value);
                } else {
                    config[name] = value;
                }
            }
        }

        var options = {
            method: 'POST',
            data: String(JSON.stringify(config)),
            beforeSend: function (xhr) {
                xhr.setRequestHeader("Content-Type", "application/json");
            },
            success: function (data, status, xhr) {
                $(".alert-success").toggle();
            },
            fail: function () {
                $(".alert-danger").toggle();
            }
        }
        var url = 'http://' + host + ':' + port + datasource;
        $.ajax(url, options);
    });

    var link_counter_items = {
        "BMS型号": "BMS设备个数",
        "BCMU设备个数": "BMS设备个数",
        "BMS设备通讯地址": "BMS设备个数",
        "PCS通讯地址": "PCS设备个数",
        "PCS型号": "PCS设备个数",
        "电表地址": "电表个数",
        "逆变器通讯地址": "逆变器个数",
    };
    var hide_items = [
        "配置完成"
    ];

    // 显示全部配置项
    function show_all_configure_items(host, port, source) {
        $.get("http://" + host + ':' + port + source, '', function (data, status, xhr) {
            for ( var itemname in data.data ) {
                var html =
                        '<div class="row">';
                html += '  <div class="col-sm-12 level1">';
                html += '    <div class="row">';
                html += '      <div class="col-sm-8 itemname">';
                html += '      ' + itemname;
                html += '      </div>';

                var value_type = typeof data.data[itemname];
                if ( value_type != 'object' ) {
                    html += '      <div class="col-sm-4 itemvalue">';
                    var payload = data.data[itemname];
                    html += '        <span name="' + itemname + '" class="normaldata">' + payload + '</span>';
                    html += '        <input valuetype="' + value_type + '" style="display: none" name="' + itemname + '" class="input-sm normaldatainput" value="' + payload + '" />';
                } else {
                    html += '      <div class="col-sm-4 itemmenucontrol">';
                    html += '          <a name="' + itemname + '" class="glyphicon glyphicon-menu-down"></a>';
                }

                html += '      </div>';
                html += '    </div>';
                html += '  </div>';
                html += '</div>';

                $("#id_body").append(html);
                if ( typeof data.data[itemname] === 'object' ) {
                    for ( var i = 1; i < data.data[itemname].length + 1; i ++ ) {
                        var html =
                            '<div style="display: none" class="row" name="' + itemname + '">';
                        html += '  <div class="col-sm-1">&nbsp;</div>';
                        html += '  <div class="col-sm-11">';
                        html += '    <div class="row  level2">';
                        html += '      <div class="col-sm-6 itemname">';
                        html += '      #' + i;
                        html += '      </div>';
                        html += '      <div class="col-sm-6 itemvalue">';
                        var payload = data.data[itemname][i-1];
                        var value_type = typeof data.data[itemname][i-1];
                        if ( payload.length == 0 ) {
                            payload = '?';
                        }
                        html += '        <span name="' + itemname + '_' + i + '" class="normaldata">' + payload + '</span>';
                        html += '        <input valuetype="' + value_type + '" style="display: none" name="' + itemname + '_' + i + '" class="input-sm normaldatainput" value="' + payload + '" />';
                        html += '      </div>';
                        html += '    </div>';
                        html += '  </div>';
                        html += '</div>';
                        $("#id_body").append(html);
                    }
                }

                console.log(itemname, typeof data.data[itemname]);
            }
        }).fail(function () {
        });
    }

    // 普通的字符串，数字数据双击后产生编辑框
    $("div").on("click", '.normaldata', function () {
        $(this).toggle();
        var name = $(this).attr('name');
        var input = $("input[name=" + name + "]");
        $(input).val($(this).html());
        $(input).toggle();
        $(input).focus();
        //$(input).parents().scrollIntoView(true);
    });
    // 普通数据编辑完成后处理
    $("div").on("blur", '.normaldatainput', function () {
        $(this).toggle();
        var name = $(this).attr('name');
        var span = $("span[name=" + name + "]");
        if ( $(this).val().length > 0 ) {
            $(span).html($(this).val());
        }
        $(span).toggle();
    });

    // 普通数据编辑完成后处理
    $("div").on("click", '.glyphicon-menu-down', function () {
        var name = $(this).attr('name');
        $(this).removeClass('glyphicon-menu-down');
        $(this).addClass('glyphicon-menu-up');
        var items = $("div[name=" + name + "]");
        var link_name = link_counter_items[name];
        var max_count = 0;
        if ( ! link_name ) {
            max_count = items.length;
        } else {
            max_count = Number($('span[name=' + link_name + ']').html());
        }
        for ( var i = 0; i < max_count && i < items.length; i ++ ) {
            $(items[i]).show();
        }
    });

    // 普通数据编辑完成后处理
    $("div").on("click", '.glyphicon-menu-up', function () {
        var name = $(this).attr('name');
        $("div[name=" + name + "]").hide();
        $(this).removeClass('glyphicon-menu-up');
        $(this).addClass('glyphicon-menu-down');
    });

    show_all_configure_items(host, port, datasource);

    window.onresize = function (e){
        //console.log(e, arguments);
        e.preventDefault();
    }
});
