/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
/**
 * 登录相关 JS，其中 remote_static_url & static_url 来源于全局变量
 */

/**
 * 对 AJAX 请求做一些统一公共处理，目前主要是对登录页面做处理
 */
$.ajaxSetup({
  statusCode: {
    401: function (xhr) {
      const response = JSON.parse(xhr.responseText);
      // 确认当前版本是否支持 Iframe 登录方式
      if (!response.has_plain) {
        window.location.reload();
      }

      openLoginWindow(response.login_url, response.width, response.height);
    },
  },
});

// 绑定跨域通信事件
function messageHandler(message) {
  const data = message.data; // message.data为另一个页面传递的数据
  if (data && data === 'login') {
    window.loginWindow.close(); // 关闭弹出的窗口
    window.loginWindow = null; // 释放弹出窗口的内存引用，刷新页面可忽略此步骤
  }
}

window.addEventListener('message', messageHandler, false);

// 检测到未登录时，弹出窗口
function openLoginWindow(src, width, height) {
  const { availHeight, availWidth } = window.screen;
  const left = (availWidth - width) / 2;
  const top = (availHeight - height) / 2;
  window.loginWindow = window.open(src, '_blank', `
        width=${width},
        height=${height},
        left=${left},
        top=${top},`);
}
