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
import i18n from '@/config/i18n/index.js'
import bus from '@/utils/bus.js'

/**
 * vue组件接口请求异常处理函数
 * @param {Object} error 错误对象
 * @param {Object} instance
 */
export function errorHandler (error, instance) {
    const data = error.data
    console.error(error)
    if (data && data.code) {
        if (data.code === 499) {
            return
        }
        if (!data.code || data.code === 404) {
            instance.exception = {
                code: '404',
                msg: i18n.t('当前访问的页面不存在')
            }
        } else if (data.code === 403) {
            instance.exception = {
                code: '403',
                msg: i18n.t('sorry，您没有访问权限!')
            }
        } else if (data.code === 405) {
            instance.exception = {
                code: '405',
                msg: i18n.t('Sorry，您的权限不足!')
            }
        } else if (data.code === 406) {
            instance.exception = {
                code: '405',
                msg: i18n.t('Sorry，您的权限不足!')
            }
        } else if (data.code === 500) {
            instance.exception = {
                code: '500',
                msg: i18n.t('系统出现异常, 请记录下错误场景并与开发人员联系, 谢谢!')
            }
        } else if (data.code === 502) {
            instance.exception = {
                code: '502',
                msg: i18n.t('系统出现异常, 请记录下错误场景并与开发人员联系, 谢谢!')
            }
        }
    } else {
        const msg = error.message || error.data.msg
        bus.$emit('showErrMessage', msg)
    }
}
