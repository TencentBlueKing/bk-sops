/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import Vue from 'vue'
import Vuex from 'vuex'

import component from './modules/component'
import business from './modules/business'
import template from './modules/template'
import taskList from './modules/taskList'
import task from './modules/task'
import http from '@/api'
import { unifyObjectStyle } from '@/common/util'

Vue.use(Vuex)

const store = new Vuex.Store({
    // 模块
    modules: {
        component,
        business,
        task,
        taskList,
        template
    },
    // 公共 store
    state: {
        loading: false, // 页面加载中
        mainContentLoading: false,
        lang: 'zh-cn',
        bizId: 0, // 业务ID
        templateId: '', // 模板ID
        taskId: '', // 任务ID
        node: {}, // 当前节点数据
        title: '业务选择',
        template: {},
        collectedTemplateList: [],
        task: {},
        taskState: '',
        excludeTaskNodes: [], // 被排除的节点
        isActionSheetShow: true,
        setPreviewCanvasData: {}, // 预览数据
        pipelineTree: {},
        defaultSchemaIndex: 0, // 默认选中的方案
        rsa_pub_key: global.RSA_PUB_KEY || '',
        // 系统当前登录用户
        user: {}
    },
    // 公共 getters
    getters: {
        mainContentLoading: state => state.mainContentLoading,
        user: state => state.user
    },
    // 公共 mutations
    mutations: {
        setBizId (state, id) {
            state.bizId = id
        },

        setTemplateId (state, id) {
            state.templateId = id
        },

        setTaskId (state, id) {
            state.taskId = id
        },

        setMainContentLoading (state, loading) {
            state.mainContentLoading = loading
        },

        updateUser (state, user) {
            state.user = Object.assign({}, user)
        },
        setTitle (state, title) {
            state.title = title
        },
        setActionSheetShow (state, isActionSheetShow) {
            state.isActionSheetShow = isActionSheetShow
        },
        setTask (state, task) {
            state.task = task
        },
        setTaskState (state, taskState) {
            state.taskState = taskState
        },
        setTemplate (state, template) {
            state.template = template
        },
        setExcludeTaskNodes (state, taskNodes) {
            state.excludeTaskNodes = taskNodes
        },
        setPreviewCanvasData (state, data) {
            state.previewCanvasData = data
        },
        setLoading (state, loading) {
            state.loading = loading
        },
        setCollectedTemplateList (state, collectedTemplateList) {
            state.collectedTemplateList = collectedTemplateList
        },
        setPipelineTree (state, pipelineTree) {
            state.pipelineTree = pipelineTree
        },
        setDefaultSchemaIndex (state, defaultSchemaIndex) {
            state.defaultSchemaIndex = defaultSchemaIndex
        },
        setNode (state, node) {
            state.node = node
        }
    },
    actions: {
        /**
         * 获取用户信息
         *
         * @param {Function} commit store commit mutation handler
         * @param {Object} state store state
         * @param {Function} dispatch store dispatch action handler
         *
         * @return {Promise} promise 对象
         */
        userInfo ({ commit, state, dispatch }, config) {
            // return http.get(`/app/index?invoke=userInfo`, config).then(response => {
            return http.get(`${AJAX_URL_PREFIX}/api/user/`, config).then(response => {
                const userData = response.data || {}
                commit('updateUser', userData)
                return userData
            })
        }
    }
})

/**
 * hack vuex dispatch, add third parameter `config` to the dispatch method
 *
 * @param {Object|string} _type vuex type
 * @param {Object} _payload vuex payload
 * @param {Object} config config 参数，主要指 http 的参数，详见 src/api/index initConfig
 *
 * @return {Promise} 执行请求的 promise
 */
store.dispatch = function (_type, _payload, config = {}) {
    const { type, payload } = unifyObjectStyle(_type, _payload)

    const action = { type, payload, config }
    const entry = store._actions[type]
    if (!entry) {
        if (NODE_ENV !== 'production') {
            console.error(`[vuex] unknown action type: ${type}`)
        }
        return
    }

    store._actionSubscribers.forEach(sub => {
        return sub(action, store.state)
    })

    return entry.length > 1
        ? Promise.all(entry.map(handler => handler(payload, config)))
        : entry[0](payload, config)
}

export default store
