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
import Vue from 'vue'
import Vuex from 'vuex'
import modules from './modules/index.js'
import axios from 'axios'
import i18n from '@/config/i18n/index.js'

Vue.use(Vuex)

const getAppLang = () => {
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
        },
        infoBasicConfig: {
            title: i18n.t('确认离开当前页面吗？'),
            subTitle: i18n.t('离开将会丢失未保存信息，建议保存后离开'),
            okText: i18n.t('留在此页'),
            cancelText: i18n.t('直接离开'),
            maskClose: false,
            closeFn: () => {
                return true
            }
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
        // 查询用户是否查看最新的版本日志
        queryNewVersion () {
            return axios.get('version_log/has_user_read_latest/').then(response => response.data)
        },
        // 获取项目版本更新日志列表
        getVersionList () {
            return axios.get('version_log/version_logs_list/').then(response => response.data)
        },
        // 版本日志详情
        getVersionDetail ({ commit }, data) {
            return axios.get('version_log/markdown_version_log_detail/', {
                params: {
                    log_version: data.version
                }
            }).then(response => response.data)
        },
        getCategorys ({ commit }) {
            axios.get('analysis/get_task_category/').then((response) => {
                commit('setCategorys', response.data.data)
            })
        },
        getNotifyTypes () {
            return axios.get('core/api/get_msg_types/').then(response => response.data)
        },
        getNotifyGroup ({ commit }, params) {
            return axios.get('api/v3/staff_group/', { params }).then(response => response.data)
        },
        // 获取收藏列表
        loadCollectList ({ commit }, data) {
            return axios.get('api/v3/collection/').then(response => response.data)
        },
        // 收藏模板，批量操作
        addToCollectList ({ commit }, list) {
            return axios.post('api/v3/collection/', list).then(response => response.data)
        },
        // 删除收藏模板，单个删除
        deleteCollect ({ commit }, id) {
            return axios.delete(`api/v3/collection/${id}/`).then(response => response.data)
        },
        // ip 选择器接口 start --->
        // 查询业务在 CMDB 的主机
        getHostInCC ({ commmit }, data) {
            const { url, fields, topo, search_host_lock } = data
            return axios.get(url, {
                params: {
                    fields: JSON.stringify(fields),
                    topo: JSON.stringify(topo),
                    search_host_lock
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
        // 查询业务在 CMDB 的动态分组
        getDynamicGroup ({ commit }, data) {
            return axios.get(data.url, { baseURL: '/', start: data.start, limit: 200 }).then(response => response.data)
        },
        // <--- ip 选择器接口 end
        // 开区资源选择器接口 start --->
        getResourceConfig ({ commit }, data) {
            return axios.get(data.url).then(response => response.data)
        },
        saveResourceScheme ({ commit }, params) {
            const { url, data } = params
            return axios.patch(url, data).then(response => response.data)
        },
        createResourceScheme ({ commit }, params) {
            const { url, data } = params
            return axios.post(url, data).then(response => response.data)
        },
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
        getCCHostCount ({ commit }, data) {
            return axios.get(data.url, { baseURL: '/', params: { bk_inst_id: data.ids } }).then(response => response.data)
        },
        // <--- 开区资源选择器接口 end
        /**
         * 获取权限相关元数据
         */
        getPermissionMeta ({ commit }) {
            return axios.get('iam/api/meta/').then((response) => {
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
         * 查询用户是否有公共流程管理页面权限
         */
        queryUserCommonPermission ({ commit }) {
            return axios.get('iam/api/is_allow/common_flow_management/').then(response => response.data)
        },
        /**
         * 获取权限中心跳转链接
         */
        getIamUrl ({ commit }, data) {
            return axios.post('iam/api/apply_perms_url/', data).then(response => response.data)
        },
        /**
         * 项目收藏、取消项目收藏
         */
        projectFavorite ({ commit }, data) {
            return axios.post(`api/v3/user_project/${data.id}/favor/`).then(response => response.data)
        },
        projectuCancelFavorite ({ commit }, data) {
            return axios.delete(`api/v3/user_project/${data.id}/cancel_favor/`).then(response => response.data)
        }
    },
    modules
})

export default store
