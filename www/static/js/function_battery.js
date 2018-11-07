$(document).ready(function () {
    var manager = new RestfulAPiManager('192.168.2.106:8083', '/v1.0/realtime', 'ui');
    var access = $(".item-body");
    for ( var i = 0; i < access.length; i ++ ) {
        var path = $(access[i]).attr("datapath");
        manager.register(path, access[i], function (data, dom) {
            $(dom).html(data.data);
        }, function(dom){
            $(dom).html("Lost");
        });
    }
    function convert_value(value, converter) {
        var val = Number(Number(value) / converter.k + converter.b).toFixed(converter.dot);
        return val;
    }
    function parser_convert(convert) {
        var d = convert.split('&');
        var cfg = {};
        cfg.k = 1;
        cfg.b = 0;
        cfg.dot = 1;
        for ( var i = 0; i < d.length; i ++ ) {
            var x = d[i].split('=');
            cfg[x[0]] = Number(x[1]);
        }
        return cfg;
    }

    var last = $('.voltage').attr("arraypath");

    function display_voltage(data, userparam) {
        var body = $(".battery-body");
        var convert = parser_convert($('.voltage').attr("convert"));
        for ( var i = 0; i < body.length; i ++ ) {
            $('#id_battery_' + (i + 1)).html(convert_value(data.data[i], convert));
        }
    }

    function display_temperature(data, userparam) {
        var body = $(".battery-body");
        var convert = parser_convert($('.temperature').attr("convert"));
        for ( var i = 0; i < body.length; i ++ ) {
            $(body[i]).html(convert_value(data.data[i], convert));
        }
    }
    function display_singlesoc(data, userparam) {
        var body = $(".battery-body");
        var convert = parser_convert($('.singlesoc').attr("convert"));
        for ( var i = 0; i < body.length; i ++ ) {
            $(body[i]).html(convert_value(data.data[i], convert));
        }
    }
    function display_singlesoh(data, userparam) {
        var body = $(".battery-body");
        var convert = parser_convert($('.singlesoh').attr("convert"));
        for ( var i = 0; i < body.length; i ++ ) {
            $(body[i]).html(convert_value(data.data[i], convert));
        }
    }

    // 初始页面显示单体电压
    manager.register($('.voltage').attr("arraypath"), null, display_voltage, function(dom) {
        $(dom).html("Lost");
    });

    $(".voltage").click(function () {
        if ( last === $('.voltage').attr("arraypath") ) {
            return;
        }
        manager.unregister(last);
        last = $('.voltage').attr("arraypath");
        manager.register(last, null, display_voltage, function(dom){
            $(dom).html("Lost");
        });
    });
    $(".temperature").click(function () {
        if ( last === $('.temperature').attr("arraypath") ) {
            return;
        }
        manager.unregister(last);
        last = $('.temperature').attr("arraypath");
        manager.register(last, null, display_temperature, function(dom){
            $(dom).html("Lost");
        });
    });
    $(".singlesoc").click(function () {
        if ( last === $('.singlesoc').attr("arraypath") ) {
            return;
        }
        manager.unregister(last);
        last = $('.singlesoc').attr("arraypath");
        manager.register(last, null, display_singlesoc, function(dom){
            $(dom).html("Lost");
        });
    });
    $(".singlesoh").click(function () {
        if ( last === $('.singlesoh').attr("arraypath") ) {
            return;
        }
        manager.unregister(last);
        last = $('.singlesoh').attr("arraypath");
        manager.register(last, null, display_singlesoh, function(dom){
            $(dom).html("Lost");
        });
    });

    setInterval(function () {
        manager.check_poll();
    }, 50);

    var lineChartData = {
        labels: [],
        datasets: [{
            label: '电压(V)',
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgb(255, 99, 132)',
            fill: false,
            data: [ ],
            yAxisID: 'y-axis-1',
        }, {
            label: '电流(A)',
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgb(54, 162, 235)',
            fill: false,
            data: [ ],
            yAxisID: 'y-axis-2'
        }]
    };

    var cavas = $(".grid-body")[0];
    var ctx = cavas.getContext('2d');
    //Chart.defaults.global.animation.duration = 0;
    var myLine = Chart.Line(ctx, {
        data: lineChartData,
        options: {
            responsive: false,
            hoverMode: 'index',
            stacked: false,
            title: {
                display: false,
                text: 'Chart.js Line Chart - Multi Axis'
            },
            scales: {
                yAxes: [{
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'y-axis-1',
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'right',
                    id: 'y-axis-2',

                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }],
            }
        }
    });

    function time_axis(count) {
        var axis = ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30",
                    "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
                    "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",
        ].reverse();
        function Tag(idx, tag) {
            this.idx = idx;
            this.tag = tag;
            this.next = null;
        }
        var taghead = new Tag(47, "23:30");
        var tag = taghead;
        for ( var i = 1; i < axis.length; i ++ ) {
            tag.next = new Tag(47 - i, axis[i]);
            tag = tag.next;
        }
        tag.next = taghead;

        var now = new Date();
        var hour = now.getHours();
        var min = now.getMinutes();

        var idx = hour * 2 + (min >= 30 ? 1 : 0);

        var limit = 0;
        while ( tag.idx !== idx && limit <= 48) {
            tag = tag.next;
            limit += 1;
        }
        var output = [];
        while ( count > 0 ) {
            count -= 1;
            output.push(tag.tag);
            tag = tag.next;
        }

        return output.reverse();
    }

    function get_time_tags(count) {

    }

    function random(min, max){
        return Math.floor(min+Math.random()*(max-min));
    }

    function update() {
        myLine.data.labels = time_axis(16);
        while ( myLine.data.datasets[0].data.length < 16 ) {
            myLine.data.datasets[0].data.push(random(0, 750));
        }
        myLine.data.datasets[0].data.push(random(0, 750));
        myLine.data.datasets[0].data.shift();

        while ( myLine.data.datasets[1].data.length < 16 ) {
            myLine.data.datasets[1].data.push(random(-200, 200));
        }
        myLine.data.datasets[1].data.push(random(-200, 200));
        myLine.data.datasets[1].data.shift();
        myLine.clear();
        myLine.update();
    }
    var min = 0;
    function mincall() {
        min += 1;
        update();
    }
    update();
    setInterval(mincall, 60000);
});
