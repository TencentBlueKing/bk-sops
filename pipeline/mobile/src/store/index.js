import Vue from 'vue'
import Vuex from 'vuex'

import templateList from './modules/templateList'
import template from './modules/template'
import taskList from './modules/taskList'
import task from './modules/task'
import http from '@/api'
import { unifyObjectStyle } from '@/common/util'

Vue.use(Vuex)

const store = new Vuex.Store({
    // 模块
    modules: {
        task,
        taskList,
        templateList,
        template
    },
    // 公共 store
    state: {
        mainContentLoading: false,
        lang: 'zh-cn',
        bizId: 0,
        title: '业务选择',
        isActionSheetShow: true,
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
        /**
         * 更新业务ID
         *
         * @param {Object} state store state
         * @param id
         */
        setBizId (state, id) {
            state.bizId = id
        },

        /**
         * 设置内容区的 loading 是否显示
         *
         * @param {Object} state store state
         * @param {boolean} loading 是否显示 loading
         */
        setMainContentLoading (state, loading) {
            state.mainContentLoading = loading
        },

        /**
         * 更新当前用户 user
         *
         * @param {Object} state store state
         * @param {Object} user user 对象
         */
        updateUser (state, user) {
            state.user = Object.assign({}, user)
        },
        setTitle (state, title) {
            state.title = title
        },
        setActionSheetShow (state, isActionSheetShow) {
            state.isActionSheetShow = isActionSheetShow
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
