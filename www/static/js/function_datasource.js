
// 数据采集器
function DataSourceCollector(path, format, dom) {
    this.path = path;
    this.format = format;
    this.dom = dom;
}

// 数据中心
function DataSourcerestFullAPI(path, format, dom) {
    this.path = path;
    this.format = format;
    this.dom = dom;
}

// 通过参数初始化一个数据源
function DataSource(datasource, format, dom) {
    var collector_re = /collector:\/\//;
    var restfull_re = /api:\/\//;

    if ( datasource.match(collector_re) ) {
        var path = datasource.slice("collector://".length, datasource.length);
        return new DataSourceCollector(path, format, dom);
    }
    else if ( datasource.match(restfull_re) ) {
        var path = datasource.slice("api://".length, datasource.length);
        return new DataSourcerestFullAPI(path, format, dom);
    }
    else {
        console.error("invalid data source", datasource);
    }

    return null;
}


// 数据源管理器
function DataSourceManager() {
    this.sources = new Array();
    this.pendding = new Array();
}
DataSourceManager.prototype.append = function (datasource) {
    this.sources.push(datasource);
};
DataSourceManager.prototype.remove = function (datasource) {
    var idx = this.sources.indexOf(datasource);
    if ( idx >= 0 ) {
        this.sources.splice(idx, 1);
    }
};
DataSourceManager.prototype.main = function () {
};
