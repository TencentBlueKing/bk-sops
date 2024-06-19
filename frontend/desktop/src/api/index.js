/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import axios from 'axios'
import axiosDefaults from 'axios/lib/defaults'
import bus from '@/utils/bus.js'
import { setJqueryAjaxConfig } from '@/config/setting.js'
import { generateTraceId } from '@/utils/uuid.js'
import { showLoginModal } from '@blueking/login-modal'

axiosDefaults.baseURL = window.SITE_URL
axiosDefaults.xsrfCookieName = window.APP_CODE + '_csrftoken'
axiosDefaults.xsrfHeaderName = 'X-CSRFToken'
axiosDefaults.withCredentials = true
axiosDefaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

// jquery ajax error handler
setJqueryAjaxConfig()

axios.interceptors.request.use(
    config => {
        config.headers.common.traceparent = generateTraceId()
        return config
    },
    error => Promise.reject(error)
)

axios.interceptors.response.use(
    response => {
        if (response.data.hasOwnProperty('result')) {
            if (!response.data.result) {
                const info = {
                    message: response.data,
                    traceId: response.headers['sops-trace-id'],
                    errorSource: 'result'
                }
                bus.$emit('showErrMessage', info)
            }
        }
        return response
    },
    error => {
        // 取消接口请求
        if (error.message === 'cancelled') {
            console.warn('cancelled')
            return Promise.reject(error)
        }

        const response = error.response
        console.log(response)
        if (response.data.message) {
            response.data.msg = response.data.message
        }
        if (response.data.responseText) {
            response.data.msg = response.data.responseText
        }
        const applyPermission = response.config.headers['Tpl-Node-Permission-Check']

        switch (response.status) {
            case 400:
                const msg = response.data.error || response.data.msg || response.data.msg.error
                const errorInfo = {
                    traceId: response.headers['sops-trace-id'],
                    message: msg
                }
                bus.$emit('showErrMessage', errorInfo)
                break
            case 401:
                const data = response.data
                if (data.has_plain && !window.loginWindow) {
                    // 当前路由为模板编辑页时，登录前先保存模板数据
                    const { pathname } = window.location
                    const typeList = ['new', 'edit', 'clone']
                    const isMatch = typeList.some(type => {
                        return [`/template/${type}/`, `/common/${type}/`].some(item => pathname.indexOf(item) > -1)
                    })
                    if (isMatch) {
                        bus.$emit('createSnapshot', true) // 创建模板快照
                    }

                    // 退出登录接口不打开登录弹框
                    if (response.config.url !== '/logout') {
                        const successUrl = `${window.location.origin}${window.SITE_URL}static/bk_sops/login_success.html`
                        let [loginUrl] = data.login_url.split('?')
                        loginUrl = `${loginUrl}?c_url=${encodeURIComponent(successUrl)}`
    
                        showLoginModal({ loginUrl })
                    }
                }
                break
            case 499:
                const permissions = response.data.permission
                let isViewApply = false
                let viewType = 'other'
                if (permissions.actions.find(item => item.id === 'project_view')) {
                    viewType = 'project'
                    isViewApply = true
                } else if (applyPermission) {
                    isViewApply = false
                } else {
                    isViewApply = permissions.actions.some(item => {
                        return ['flow_view', 'common_flow_view', 'mini_app_view', 'task_view'].includes(item.id)
                    })
                }
                if (isViewApply) {
                    bus.$emit('togglePermissionApplyPage', true, viewType, permissions)
                } else {
                    bus.$emit('showPermissionModal', permissions)
                }
                break
            case 500:
                bus.$emit('showErrorModal', response.status, response.data.responseText)
                break
        }
        if (!response.data) {
            const msg = gettext('接口数据返回为空')
            console.warn(gettext('接口异常，'), gettext('HTTP状态码：'), response.status)
            console.error(msg)
            response.data = {
                code: response.status,
                msg: msg
            }
        } else {
            const msg = response.data
            response.data = {
                code: response.status,
                msg
            }
        }
        return Promise.reject(response)
    }
)

axios.jsonp = (url, data) => {
    if (!url) {
        throw new Error('url is necessary')
    }
    const callback = 'CALLBACK' + Math.random().toString().substr(9, 18)
    const JSONP = document.createElement('script')
    JSONP.setAttribute('type', 'text/javascript')

    const headEle = document.getElementsByTagName('head')[0]

    let ret = ''
    if (data) {
        if (typeof data === 'string') {
            ret = '&' + data
        } else if (typeof data === 'object') {
            for (const key in data) {
                ret += '&' + key + '=' + encodeURIComponent(data[key])
            }
        }
        ret += '&_time=' + Date.now()
    }
    JSONP.src = `${url}?callback=${callback}${ret}`

    function remove () {
        headEle.removeChild(JSONP)
        delete window[callback]
    }
    return new Promise((resolve, reject) => {
        window[callback] = r => {
            resolve(r)
            remove()
        }
        JSONP.onerror = err => {
            reject(err)
            remove()
        }

        headEle.appendChild(JSONP)
    })
}
