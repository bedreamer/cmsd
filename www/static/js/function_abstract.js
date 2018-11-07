// 处理页面上的遥测数据显示

$(document).ready(function () {
    var abstract_object_list = $(".title-arear-item .value");
    for ( var i = 0; i < abstract_object_list.length; i ++ ) {
        var obj = abstract_object_list[i];
        var abstract = new ApiObject(obj, $(obj).attr('datasource'), $(obj).attr("format"));
        api_append(abstract)
    }
});

