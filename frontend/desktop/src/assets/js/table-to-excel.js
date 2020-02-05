/**
 * thanks to https://github.com/ecofe/tabletoexcel
 * version 1.0.6
 */


/**
 * @fileOverview 定义table或者array转化成excel表格的公共方法
 */



/**
 * @class TableToExcel 定义 table或者 array转化成 excel表格的公共方法
 */
const TableToExcel = function() {}
/**
 *@lends TableToExcel.prototype
    */
TableToExcel.prototype = {
    /**
     *判断IE和非IE浏览器
        */
    checkIsIE: !!(navigator.userAgent.indexOf('Trident') > -1 && navigator.userAgent.indexOf('Opera') === -1),
    /**
     *判断是否mac系统
        */
    checkIsMac: navigator.userAgent.indexOf("Mac") != -1,
    /**
     *入口
        *@param {String} table 页面内table的id属性值  不传值则从一个二维数组里生成table
        */
    render: function(param, title) {
        if (this.checkIsIE) {
            this.createExcelIE(param, title);
        } else {
            this.createExcel(param, title)
        }
    },
    /**
    *创建表格，render方法传递的参数是数组时调用
    *@param {Array} param 接口传过来的数组
    *数组格式
    *@example
    var obj=[
        ['LastName','Sales','Country','Quarter'],
        ['Smith','16753','UK','Qtr 3'],
        ['Johnson','14808','USA','Qtr 4']
    ];
    */
    createTable: function(param, title) {
        var trLen = param.length;
        var tdLen = param[0].length;
        var trArr = [];
        var style = this.checkIsMac ? "" : 'mso-number-format:"\@"';
        if (title) {
            var hdLen = title.length;
            for (var n = 0; n < hdLen; n++) {
                var border = n % 2 != 0 ? "border-top:1px solid #fff;" : "";
                trArr.push('<tr><td style="background:'+title[n].bg+'; color:'+title[n].color+';" colspan="' + param[0].length + '">' + title[n].text + '</td></tr>');
            }
        }
        for (var i = 0; i < trLen; i++) {
            var tdArr = [];
            for (var o = 0; o < tdLen; o++) {
                var tdHtml = '<td style=' + style + '>' + param[i][o] + '</td>';
                tdArr.push(tdHtml);
            }
            var trHtml = '<tr>' + tdArr.join("") + '</tr>';
            trArr.push(trHtml);
        }
        return trArr.join("");
    },
    /**
     *根据页面内存在的table生成excel   非IE浏览器
        *@param {String} param 页面内table的id属性值
        *or
        *@param {Array} param 接口传过来的二维数组
        */
    createExcel: function(param, title) {
        var self = this;
        var tableHtml = null;
        var func = (function() {
            var uri = 'data:application/vnd.ms-excel;base64,';
            var template = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>{worksheet}</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--><style>td{mso-number-format:"\@";}</style></head><body><table>{table}</table></body></html>';
            var base64 = function(s) {
                return window.btoa(unescape(encodeURIComponent(s)))
            };
            var format = function(s, c) {
                return s.replace(/{(\w+)}/g, function(m, p) {
                    return c[p];
                })
            }
            return function(table, name) {
                if (typeof(param) == "string") {
                    tableHtml = document.getElementById(param).innerHTML;
                } else {
                    tableHtml = self.createTable(param, title);
                }
                var ctx = {
                    worksheet: name || 'Worksheet',
                    table: tableHtml
                }
                var link = document.createElement("a");
                link.href = uri + base64(format(template, ctx));
                link.download = 'download.xls';
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
            }
        })();
        func()
    },
    /**
     *根据页面内存在的table生成excel   IE浏览器
        *@param {String} param 页面内table的id属性值
        *or
        *@param {Array} param 接口传过来的二维数组
        */
    createExcelIE: function(param, title) {
        var tableHtml = null;
        if (typeof(param) == "string") {
            tableHtml = document.getElementById(param).outerHTML;
        } else {
            tableHtml = '<table>' + this.createTable(param, title) + '</table>';
        }

        window.clipboardData.setData("Text", tableHtml);
        var objExcel = new ActiveXObject("Excel.Application");
        objExcel.visible = true;
        var objWorkbook = objExcel.Workbooks.Add;
        var objWorksheet = objWorkbook.Worksheets(1);
        objWorksheet.Paste;
    }
}

export default TableToExcel
