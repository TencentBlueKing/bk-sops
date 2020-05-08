/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
/**
 * 移动端vue组件接口请求异常处理函数
 * @param {Object} error 错误对象
 * @param {Object} instance
 */
export function errorHandler (error, instance) {
    // 请求队列被取消不捕获
    if (error.isCancel) {
        return
    }
    const data = error.data
    console.error(error)
    let msg = ''
    if (data && data.code) {
        if (!data.code || data.code === 404) {
            instance.exception = {
                code: '404',
                msg: window.gettext('当前访问的页面不存在')
            }
        } else if (data.code === 403) {
            instance.exception = {
                code: '403',
                msg: window.gettext('sorry，您没有访问权限!')
            }
        } else if (data.code === 405) {
            instance.exception = {
                code: '405',
                msg: window.gettext('Sorry，您的权限不足!')
            }
        } else if (data.code === 406) {
            instance.exception = {
                code: '405',
                msg: window.gettext('Sorry，您的权限不足!')
            }
        } else if (data.code === 500) {
            instance.exception = {
                code: '500',
                msg: window.gettext('系统出现异常, 请记录下错误场景并与开发人员联系, 谢谢!')
            }
        } else if (data.code === 502) {
            instance.exception = {
                code: '502',
                msg: window.gettext('系统出现异常, 请记录下错误场景并与开发人员联系, 谢谢!')
            }
        }
        msg = instance.exception.msg
    } else {
        msg = error.message || error.data.msg
    }
    global.bus.$emit('notify', { message: msg, result: false })
}
