// 处理页面上的遥测数据显示

$(document).ready(function () {
    var yaoce_object_list = $(".yaoce-arear-item .unit .value");
    for ( var i = 0; i < yaoce_object_list.length; i ++ ) {
        var obj = yaoce_object_list[i];
        var yaoce = new ApiObject(obj, $(obj).attr('datasource'), $(obj).attr("format"));
        api_append(yaoce)
    }
});

