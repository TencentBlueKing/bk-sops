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
import store from '@/store/index.js'

/**
 * 兼容之前版本的标准插件配置项里的异步请求
 * @param {String} site_url
 * @param {Object} project
 */
export function setAtomConfigApiUrls (site_url, project) {
    $.context = {
        project,
        biz_binding: project.from_cmdb,
        bk_biz_id: project.bk_biz_id,
        biz_cc_id: project.bk_biz_id,
        site_url: site_url,
        project_id: project.id,
        component: site_url + 'api/v3/component/',
        variable: site_url + 'api/v3/variable/',
        template: site_url + 'api/v3/template/',
        instance: site_url + 'api/v3/taskflow/',
        getConstants () {
            return store.state.template.constants
        }
    }
}

/**
 * ajax全局设置
 */
// 在这里对ajax请求做一些统一公用处理
export function setJqueryAjaxConfig () {
    $.ajaxSetup({
        // timeout: 8000,
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
                const src = xhr.responseText
                const ajaxContent = '<iframe name="403_iframe" frameborder="0" src="' + src + '" style="width:570px;height:400px;"></iframe>'
                bus.$emit('showErrorModal', 'default', ajaxContent, gettext('提示'))
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
            499: function (xhr) {
                const resData = JSON.parse(xhr.responseText)
                const permission = resData.permission
                bus.$emit('showPermissionModal', permission)
            },
            500: function (xhr, textStatus) {
                bus.$emit('showErrorModal', '500', xhr.responseText)
            }
        }
    })
}
