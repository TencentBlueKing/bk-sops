/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import http from '@/api'

export default {
    namespaced: true,
    actions: {
        getAtomConfig ({ state }, { atomCode, version }) {
            return http.get(`api/v3/weixin_component/${atomCode}/`, { params: { version } }).then((response) => {
                response = response.data
                if (response.form_is_embedded) {
                    /* eslint-disable-next-line */
                    eval(response.form)
                    return $.atoms[atomCode]
                }

                const form = response.form.replace(/^http(s)?:\/\/(.*?)\//, '/').replace('/static/', '/static/weixin/')
                return global.$.getScript(form).then(() => $.atoms[atomCode])
            })
        },

        getVariableConfig ({ state }, { customType, configKey, version }) {
            return http.get(`api/v3/weixin_variable/${customType}/`, { params: { version } }).then((response) => {
                response = response.data
                if (response.form_is_embedded) {
                    /* eslint-disable-next-line */
                    eval(response.form)
                    return $.atoms[configKey]
                }

                const form = response.form.replace(/^http(s)?:\/\/(.*?)\//, '/').replace('/static/', '/static/weixin/')
                return global.$.getScript(form).then(() => $.atoms[configKey])
            })
        }
    }
}
