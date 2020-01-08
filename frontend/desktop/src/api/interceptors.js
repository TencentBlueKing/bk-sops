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
        const response = error.response
        console.log(response)

        switch (response.status) {
            case 400:
                const info = {
                    message: response.data.error || response.data.msg.error,
                    theme: 'error'
                }
                bus.$emit('showMessage', info)
                break
            case 401:
            case 403:
            case 405:
            case 406:
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
