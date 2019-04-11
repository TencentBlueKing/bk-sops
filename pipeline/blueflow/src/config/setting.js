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
import bus from '@/utils/bus.js'

/**
 * 兼容之前版本的标准插件配置项里的异步请求
 * @param {String} site_url
 * @param {String} BIZ_CC_ID
 */
export function setAtomConfigApiUrls (SITE_URL, BIZ_CC_ID) {
    $.context = {
        site_url: SITE_URL,
        biz_cc_id: BIZ_CC_ID,
        homelist: SITE_URL + 'template/home/' + BIZ_CC_ID + '/',
        component: SITE_URL + 'api/v3/component/',
        variable: SITE_URL + 'api/v3/variable/',
        template: SITE_URL + 'api/v3/template/',
        subform: SITE_URL + 'template/api/form/' + BIZ_CC_ID + '/',
        instance: SITE_URL + 'api/v3/taskflow/'
    }
}

/**
 * ajax全局设置
 */
// 在这里对ajax请求做一些统一公用处理
export function setJqueryAjaxConfig () {
    $.ajaxSetup({
        //	timeout: 8000,
        statusCode: {
            // tastypie args error
            400: function (xhr) {
                const message = xhr.responseText
                const info = {
                    theme: 'error',
                    message
                }
                bus.$emit('showMessage', info)
            },
            401: function (xhr) {
                const src = xhr.responseText
                bus.$emit('showLoginModal', src)
            },
            402: function (xhr) {
                // 功能开关
                var _src = xhr.responseText
                var ajax_content = '<iframe name="403_iframe" frameborder="0" src="' + _src + '" style="width:570px;height:400px;"></iframe>'
                art.dialog({
                    title: gettext("提示"),
                    lock: true,
                    content: ajax_content
                })
                return
            },
            403: function (xhr) {
                bus.$emit('showErrorModal', '403')
            },
            405: function (xhr) {
                bus.$emit('showErrorModal', '405', xhr.responseText)
            },
            406: function (xhr) {
                bus.$emit('showErrorModal', '406')
            },
            500: function (xhr, textStatus) {
                bus.$emit('showErrorModal', '500', xhr.responseText)
            }
        }
    })
}

