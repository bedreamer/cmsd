// 处理页面上的遥测数据显示

function format_to_chartdata(format) {
    var lineChartData = {
        labels: [],
        datasets: [{
            label: '电压(V)',
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgb(255, 99, 132)',
            fill: false,
            data: [],
            yAxisID: 'y-axis-1',
        }, {
            label: '电流(A)',
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgb(54, 162, 235)',
            fill: false,
            data: [],
            yAxisID: 'y-axis-2'
        }]
    };
    return lineChartData;
}

$(document).ready(function () {
    var grid_object_list = $(".frame-grid-1-arear");
    for ( var i = 0; i < grid_object_list.length; i ++ ) {
        var obj = grid_object_list[i];
        var datasource = $(obj).attr('datasource');
        var format = $(obj).attr("format");

        var cav = $(obj).children('canvas');
        if (cav === undefined) {
            console.error("invalid canvas dom.");
            continue;
        }
        var width = Math.round(Number($(obj).css("width").split("px")[0]));
        var height = Math.round(Number($(obj).css("height").split("px")[0]));

        $(cav).css("width", width + "px");
        $(cav).css("height", height + "px");
    }
/*
        var ctx = cav[0].getContext('2d');
        if ( ctx === undefined ) {
            console.error("canvas fail.");
            continue;
        }

        var lineChartData = {
            labels: [],
            datasets: [{
                label: '电压(V)',
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgb(255, 99, 132)',
                fill: false,
                data: [],
                yAxisID: 'y-axis-1',
            }, {
                label: '电流(A)',
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgb(54, 162, 235)',
                fill: false,
                data: [],
                yAxisID: 'y-axis-2'
            }]
        };
        var line = Chart.Line(ctx, {
            data: lineChartData,
            options: {
                responsive: false,
                hoverMode: 'index',
                stacked: false,
                title: {
                    display: false,
                    text: '图表'
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
        line.update();
        */
});

