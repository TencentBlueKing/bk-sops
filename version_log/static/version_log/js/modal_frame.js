
function show_modal() {
    load_modal_frame(window.site_url+ window.version_log_url+'block/');
}

function load_modal_frame(url) {
    $.ajax({
        url: url,
        type: "GET",
        dataType: "html",
        success: function(data) {
            var d = dialog({
                height: 600,
                width: 1105,
                title: '版本日志',
                content: data,
            });
            d.showModal();
        }
    })
}

// 获取指定的Cookie
function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
}

// 如果存在Cookie SHOW_VERSION_LOG值为True，则弹出版本日志弹窗
if (getCookie("SHOW_VERSION_LOG") === "True") {
    $(document).ready(function () {
        show_modal()
        // 清除Cookie避免重复弹窗
        document.cookie = "SHOW_VERSION_LOG=; path=/; expire=Thu, 01 Jan 1970 00:00:01 GMT;"
    })
}