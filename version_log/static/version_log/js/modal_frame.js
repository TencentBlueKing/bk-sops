/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/

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
                title: gettext('版本日志'),
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