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
import api from '@/api/index.js'

const manage = {
    namespaced: true,
    state: {
    },
    mutations: {
    },
    actions: {
        loadPackageSource () {
            return api.loadPackageSource().then(
                response => response.data
            )
        },
        createPackageSource ({ commit }, data) {
            return api.createPackageSource(data).then(
                response => response.data
            )
        },
        deletePackageSource ({ commit }, data) {
            return api.deletePackageSource(data).then(
                response => response.data
            )
        },
        updatePackageSource ({ commit }, data) {
            return api.updatePackageSource(data).then(
                response => response.data
            )
        },
        loadSyncTask ({ commit }, data) {
            return api.loadSyncTask(data).then(
                response => response.data
            )
        },
        createSyncTask () {
            return api.createSyncTask().then(
                response => response.data
            )
        }
    }
}

export default manage
