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
import i18n from '@/config/i18n/index.js'
import axios from 'axios'
import bus from '@/utils/bus.js'
import { checkDataType } from '@/utils/checkDataType'
import { setJqueryAjaxConfig } from '@/config/setting.js'

// jquery ajax error handler
setJqueryAjaxConfig()

axios.interceptors.request.use(function (config) {
    return config
}, function (error) {
    return Promise.reject(error)
})

axios.interceptors.response.use(
    response => {
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

        switch (response.status) {
            case 400:
                const info = {
                    message: response.data.error || response.data.msg.error,
                    lines: 2,
                    theme: 'error'
                }
                bus.$emit('showMessage', info)
                break
            case 401:
                const data = response.data
                if (data.has_plain) {
                    window.top.BLUEKING.corefunc.open_login_dialog(data.login_url, data.width, data.height, response.config.method)
                }
                break
            case 403:
            case 405:
            case 406:
            case 500:
                bus.$emit('showErrorModal', response.status, response.data.responseText)
                break
            case 499:
                const permissions = response.data.permission
                let viewType = ''
                const isViewApply = permissions.some(perm => {
                    if (perm.action_id === 'view') {
                        perm.resources.some(resource => {
                            viewType = 'other'
                            if (resource.find(item => item.resource_type === 'project')) {
                                viewType = 'project'
                                return true
                            }
                        })
                        return true
                    }
                })
                if (isViewApply) {
                    bus.$emit('togglePermissionApplyPage', true, viewType, permissions)
                } else {
                    bus.$emit('showPermissionModal', permissions)
                }
                break
        }
        if (!response.data) {
            const msg = i18n.t('接口数据返回为空')
            console.warn(i18n.t('接口异常，'), i18n.t('HTTP状态码：'), response.status)
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
        if (response.data.message) {
            if (checkDataType(response.data.message) === 'Object') {
                const msg = []
                for (const key in response.data.message) {
                    msg.push(response.data.message[key].join(';'))
                }
                response.data.msg = msg.join(';')
            } else if (checkDataType(response.data.message) === 'Array') {
                response.data.msg = response.data.message.join(';')
            } else {
                response.data.msg = response.data.message
            }
        }
        if (response.data.responseText) {
            response.data.msg = response.data.responseText
        }
        return Promise.reject(response)
    }
)
