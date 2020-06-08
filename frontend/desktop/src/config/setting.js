/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import bus from '@/utils/bus.js'
import store from '@/store/index.js'
import i18n from '@/config/i18n/index.js'

/**
 * 兼容之前版本的标准插件配置项里的异步请求
 * @param {String} site_url
 * @param {Object} project
 */
export function setConfigContext (site_url, project) {
    $.context = {
        project: project || undefined,
        biz_cc_id: project ? (project.from_cmdb ? project.bk_biz_id : undefined) : undefined,
        site_url: site_url,
        component: site_url + 'api/v3/component/',
        variable: site_url + 'api/v3/variable/',
        template: site_url + 'api/v3/template/',
        instance: site_url + 'api/v3/taskflow/',
        get (attr) { // 获取 $.context 对象上属性
            return $.context[attr]
        },
        getBkBizId () { // 项目来自 cmdb，则获取对应的业务 id
            if ($.context.project) {
                return $.context.project.from_cmdb ? $.context.project.bk_biz_id : ''
            }
            return ''
        },
        getProjectId () { // 获取项目 id
            if ($.context.project) {
                return $.context.project.id
            }
            return ''
        },
        canSelectBiz () { // 是否可以选择业务
            if ($.context.project) {
                return !$.context.project.from_cmdb
            }
            return true
        },
        getConstants () { // 获取流程模板下的全局变量
            return store.state.template.constants
        }
    }
}

/**
 * ajax全局设置
 */
// 在这里对ajax请求做一些统一公用处理
export function setJqueryAjaxConfig () {
    $(document).ajaxError(function (event, xhr, setting) {
        const code = xhr.status
        switch (code) {
            case 400:
                const message = xhr.responseText
                const info = {
                    theme: 'error',
                    message
                }
                bus.$emit('showMessage', info)
                break
            case 401:
                const { has_plain, login_url, width, height } = xhr.responseJSON
                const method = setting.type
                bus.$emit('showLoginModal', { has_plain, login_url, width, height, method })
                break
            case 402:
                // 功能开关
                const src = xhr.responseText
                const ajaxContent = '<iframe name="403_iframe" frameborder="0" src="' + src + '" style="width:570px;height:400px;"></iframe>'
                bus.$emit('showErrorModal', 'default', ajaxContent, i18n.t('提示'))
                break
            case 403:
                bus.$emit('showErrorModal', '403')
                break
            case 405:
                bus.$emit('showErrorModal', '405', xhr.responseText)
                break
            case 406:
                bus.$emit('showErrorModal', '406')
                break
            case 499:
                bus.$emit('showPermissionModal', xhr.responseJSON.permission)
                break
            case 500:
                bus.$emit('showErrorModal', '500', xhr.responseText)
                break
        }
    })
}
