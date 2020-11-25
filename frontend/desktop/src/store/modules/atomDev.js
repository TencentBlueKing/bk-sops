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

const atomDev = {
    namespaced: true,
    actions: {
        // 加载 api 接口分组列表
        loadApiList ({ commit }) {
            return axios.get('develop/api/esb_get_systems/').then(response => response.data)
        },
        // 加载分组下的所有 api 配置参数
        loadApiComponent ({ commit }, data) {
            const { name } = data
            return axios.get('develop/api/esb_get_components/', {
                params: {
                    system_names: JSON.stringify(name)
                }
            }).then(response => response.data)
        },
        // 加载 api 代码内容
        loadApiPluginCode ({ commit }, data) {
            const { system, component } = data
            return axios.get('develop/api/get_plugin_initial_code/', {
                params: {
                    esb_system: system,
                    esb_component: component
                }
            }).then(response => response.data)
        }
    }
}

export default atomDev
