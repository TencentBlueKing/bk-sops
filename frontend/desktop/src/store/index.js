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
import Vue from 'vue'
import Vuex from 'vuex'
import modules from './modules/index.js'
import axios from 'axios'

Vue.use(Vuex)

function getAppLang () {
    return getCookie('blueking_language') === 'en' ? 'en' : 'zh-cn'
}

const store = new Vuex.Store({
    strict: process.env.NODE_ENV !== 'production',
    state: {
        username: window.USERNAME,
        footer: '',
        hasAdminPerm: null, // 是否有管理员查看权限
        hasStatisticsPerm: null, // 是否有运营数据查看权限
        hideHeader: window.HIDE_HEADER === 1,
        site_url: window.SITE_URL,
        app_id: window.APP_ID, // 轻应用 id
        view_mode: window.VIEW_MODE,
        lang: getAppLang(),
        notFoundPage: false,
        categorys: [],
        components: [],
        isSuperUser: window.IS_SUPERUSER === 1,
        v1_import_flag: window.IMPORT_V1_FLAG,
        rsa_pub_key: window.RSA_PUB_KEY,
        permissionMeta: {
            system: [],
            resources: [],
            actions: []
        }
    },
    mutations: {
        setAppId (state, id) {
            state.app_id = id
        },
        setPageFooter (state, content) {
            state.footer = content
        },
        setAdminPerm (state, perm) {
            state.hasAdminPerm = perm
        },
        setStatisticsPerm (state, perm) {
            state.hasStatisticsPerm = perm
        },
        setViewMode (state, mode) {
            state.view_mode = mode
        },
        setNotFoundPage (state, val) {
            state.notFoundPage = val
        },
        setCategorys (state, data) {
            state.categorys = data
        },
        setSingleAtomList (state, data) {
            state.components = data
        },
        setPermissionMeta (state, data) {
            state.permissionMeta = data
        }
    },
    actions: {
        // 获取页面动态 footer 内容
        getFooterContent () {
            return axios.get('core/footer/').then(response => response.data)
        },
        // 获取项目版本更新日志列表
        getVersionList () {
            return axios.get('version_log/version_logs_list/').then(response => response.data)
        },
        // 版本日志详情
        getVersionDetail ({ commit }, data) {
            return axios.get('version_log/version_log_detail/', {
                params: {
                    log_version: data.version
                }
            }).then(response => response.data)
        },
        getCategorys ({ commit }) {
            axios.get('analysis/get_task_category/').then(response => {
                commit('setCategorys', response.data.data)
            })
        },
        // 获取收藏列表
        loadCollectList ({ commit }, data) {
            return axios.get('api/v3/collection/', {
                params: {
                    limit: 0
                }
            }).then(response => response.data)
        },
        // 收藏模板，批量操作
        addToCollectList ({ commit }, list) {
            return axios.put('api/v3/collection/', {
                objects: list
            }).then(response => response.data)
        },
        // 删除收藏模板，单个删除
        deleteCollect ({ commit }, id) {
            return axios.delete(`api/v3/collection/${id}/`).then(response => response.data)
        },
        // ip 选择器接口 start --->
        // 查询业务在 CMDB 的主机
        getHostInCC ({ commmit }, data) {
            const { url, fields, topo } = data
            return axios.get(url, {
                params: {
                    fields: JSON.stringify(fields),
                    topo: JSON.stringify(topo)
                },
                baseURL: '/'
            }).then(response => response.data)
        },
        // 查询业务在 CMDB 的拓扑树
        getTopoTreeInCC ({ commmit }, data) {
            return axios.get(data.url, { baseURL: '/' }).then(response => response.data)
        },
        // 查询业务在 CMDB 的拓扑模型
        getTopoModelInCC ({ commit }, data) {
            return axios.get(data.url, { baseURL: '/' }).then(response => response.data)
        },
        // <--- ip 选择器接口 end
        // 开区资源选择器接口 start --->
        getCCSearchTopoSet ({ commit }, data) {
            return axios.get(data.url, { baseURL: '/' }).then(response => response.data)
        },
        getCCSearchTopoResource ({ commit }, data) {
            return axios.get(data.url, { baseURL: '/' }).then(response => response.data)
        },
        getCCSearchModule ({ commit }, data) {
            return axios.get(data.url, {
                params: {
                    bk_set_id: data.bk_set_id
                },
                baseURL: '/'
            }).then(response => response.data)
        },
        getCCSearchObjAttrHost ({ commit }, data) {
            return axios.get(data.url, { baseURL: '/' }).then(response => response.data)
        },
        getCCSearchColAttrSet ({ commit }, data) {
            return axios.get(data.url, { baseURL: '/' }).then(response => response.data)
        },
        // <--- 开区资源选择器接口 end
        /**
         * 获取权限相关元数据
         */
        getPermissionMeta ({ commit }) {
            return axios.get('iam/api/meta/').then(response => {
                commit('setPermissionMeta', response.data.data)
                return response.data
            })
        },
        /**
         * 查询用户是否有某项权限
         */
        queryUserPermission ({ commit }, data) {
            return axios.post('iam/api/is_allow/', data).then(response => response.data)
        },
        /**
         * 获取权限中心跳转链接
         */
        getIamUrl ({ commit }, data) {
            return axios.post('iam/api/apply_perms_url/', data).then(response => response.data)
        }
    },
    modules
})

export default store
