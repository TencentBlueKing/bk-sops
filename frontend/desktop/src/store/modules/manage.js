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
import store from '@/store/index.js'

const manage = {
    namespaced: true,
    actions: {
        /**
         * 加载插件包源配置
         * @param {Object} fields 包源查询字段
         */
        loadPackageSource () {
            return axios.get('api/v3/package_source/').then(response => response.data)
        },
        /**
         * 新增插件包源配置
         * @param {Object} data 插件包源配置
         */
        createPackageSource ({ commit }, data) {
            return axios.post('api/v3/package_source/', data).then(response => response.data)
        },
        /**
         * 删除所有插件包源
         */
        deletePackageSource ({ commit }, data) {
            return axios.delete('api/v3/package_source/', data).then(response => response.data)
        },
        /**
         * 更新插件包源配置
         * @param {Object} data 插件包源配置
         */
        updatePackageSource ({ commit }, data) {
            return axios.post('api/v3/package_source/', data, {
                headers: {
                    'content-type': 'application/json',
                    'X-HTTP-Method-Override': 'PATCH'
                }
            }).then(response => response.data)
        },
        /**
         * 加载远程包源同步任务列表
         */
        loadSyncTask ({ commit }, data) {
            const { limit, offset } = data
            return axios.get('api/v3/sync_task/', {
                params: { limit, offset }
            }).then(response => response.data)
        },
        /**
         * 创建远程包源同步
         */
        createSyncTask () {
            const creator = store.state.username
            const create_method = 'manual'
            return axios.post('api/v3/sync_task/', { creator, create_method }).then(response => response.data)
        }
    }
}

export default manage
