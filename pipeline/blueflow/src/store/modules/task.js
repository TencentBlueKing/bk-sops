/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import api from '@/api/index.js'

const task = {
    namespaced: true,
    state: {
        taskScheme: []
    },
    mutations: {
        setTaskScheme (state, data) {
            state.taskScheme = data
        }
    },
    actions: {
        loadTaskScheme ({commit}, payload) {
            const { cc_id, template_id} = payload
            return api.getTaskScheme({cc_id, template_id}).then(response => response.data.objects)
        },
        createTaskScheme ({commit}, payload) {
            return api.createTaskScheme(payload).then(response => response.data)
        },
        deleteTaskScheme ({commit}, schemeId) {
            return api.deleteTaskScheme(schemeId).then(response => response.data)
        },
        getSchemeDetail ({commit}, schemeId) {
            return api.getSchemeDetail(schemeId).then(response => response.data)
        },
        loadPreviewNodeData ({commit}, payload) {
            return api.getPreviewNodeData(payload).then(response => response.data)
        },
        createTask ({commit}, data) {
            return api.createTask(data).then(response => response.data)
        },
        getTaskInstanceData ({commit}, instance_id) {
            return api.getTaskInstanceData(instance_id).then(response => response.data)
        },
        claimFuncTask ({commit}, data) {
            return api.claimFuncTask(data).then(response => response.data)
        },
        getInstanceStatus ({commit}, data) {
            return api.getInstanceStatus(data).then(response => response.data)
        },
        instanceStart ({commit}, instance_id) {
            return api.instanceStart(instance_id).then(response => response.data)
        },
        instancePause ({commit}, instance_id) {
            return api.instancePause(instance_id).then(response => response.data)
        },
        subInstancePause ({commit}, data) {
            return api.subInstancePause(data).then(response => response.data)
        },
        instanceResume ({commit}, instance_id) {
            return api.instanceResume(instance_id).then(response => response.data)
        },
        subInstanceResume ({commit}, data) {
            return api.subInstanceResume(data).then(response => response.data)
        },
        instanceRevoke ({commit}, instance_id) {
            return api.instanceRevoke(instance_id).then(response => response.data)
        },
        instanceModifyParams ({commit}, data) {
            return api.instanceModifyParams(data).then(response => response.data)
        },
        getNodeActDetail ({commit}, data) {
            return api.getNodeActDetail(data).then(response => response.data)
        },
        getNodeActInfo ({commit}, data) {
            return api.getNodeActInfo(data).then(response => response.data)
        },
        instanceRetry ({commit}, data) {
            return api.instanceRetry(data).then(response => response.data)
        },
        setSleepNode ({commit}, data) {
            return api.setSleepNode(data).then(response => response.data)
        },
        instanceNodeSkip ({commit}, data) {
            return api.instanceNodeSkip(data).then(response => response.data)
        },
        skipExclusiveGateway ({commit}, data) {
            return api.instanceBranchSkip(data).then(response => response.data)
        },
        pauseNodeResume ({commit}, data) {
            return api.pauseNodeResume(data).then(response => response.data)
        },
        loadAppmakerSummary () {
            return api.loadAppmakerSummary().then(response => response.data)
        },
        loadTaskCount ({commit}, params) {
            return api.loadTaskCount(params).then(response => response.data)
        },
        queryInstanceData ({commit}, data) {
            return api.queryInstance(data).then(response => response.data)
        },
        loadCreateMethod ({commit}) {
            return api.loadCreateMethod().then(response => response.data)
        },
        getJobInstanceLog ({commit}, data) {
            return api.getJobInstanceLog(data).then(response => response.data)
        }
    }
}

export default task
