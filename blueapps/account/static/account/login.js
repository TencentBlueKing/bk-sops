/**
 * 登录相关 JS，其中 remote_static_url & static_url 来源于全局变量
 */ 

document.write(" <script lanague=\"javascript\" src=\""+remote_static_url+"artdialog/jquery.artDialog.js?skin=simple\"> <\/script>");

/**
 * 对 AJAX 请求做一些统一公共处理，目前主要是对登录页面做处理
 */
$.ajaxSetup({
    statusCode: {
        401: function(xhr) {
            var response = JSON.parse(xhr.responseText);
            // 确认当前版本是否支持 Iframe 登录方式
            if (!response.has_plain) {
                window.location.reload();
            }

            try{
                window.top.BLUEKING.corefunc.open_login_dialog(response['login_url']);
            }catch(err){
                open_login_dialog(
                    response['login_url'], response['width'], response['height']);
            }
        }
    }
});

/**
 * 打开登录窗口
 */
function open_login_dialog(src, width, height){
    var login_html = '<div class="mod_login" id="loginbox" style="padding: 0px 0px; visibility: visible;" align="center">' +
                        '<iframe name="login_frame" id="login_frame"  width="100%" height="100%" frameborder="0" allowtransparency="yes"  src="'+src+
                        '" style="width:'+width+'px;height:'+height+'px;"></iframe>' +
                     '</div>';
    art.dialog({
        id:"401_dialog",
        fixed: true,
        lock: true,
        padding: "0px 0px",
        content: login_html
    });
}

/**
 * 关闭登录框
 */
function close_login_dialog(){
    art.dialog({id: '401_dialog'}).close();

    try {
        window.close_login_dialog_after();
    } catch(err){}
}


