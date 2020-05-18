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
import api from '@/api'

Vue.use(Vuex)

function getAppLang () {
    return getCookie('blueking_language') || 'zh-cn'
}

const store = new Vuex.Store({
    strict: process.env.NODE_ENV !== 'production',
    state: {
        username: window.USERNAME,
        userRights: {
            function: false,
            audit: false
        },
        footer: '',
        hasAdminPerm: false, // 是否有管理员权限
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
        rsa_pub_key: window.RSA_PUB_KEY
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
        setUserRights (state, data) {
            const { type, val } = data
            state.userRights[type] = val
        }
    },
    actions: {
        getFooterContent () {
            return api.getFooterContent().then(response => response.data)
        },
        getVersionList () {
            return api.getVersionList().then(response => response.data)
        },
        getVersionDetail ({ commit }, data) {
            return api.getVersionDetail(data).then(response => response.data)
        },
        getCategorys ({ commit }) {
            api.getCategorys().then(response => {
                commit('setCategorys', response.data.data)
            })
        },
        getSingleAtomList ({ commit }) {
            api.getSingleAtomList().then(response => {
                commit('setSingleAtomList', response.data.objects)
            })
        },
        // ip 选择器接口 start --->
        getHostInCC ({ commmit }, data) {
            return api.loadHostInCC(data).then(response => response.data)
        },
        getTopoTreeInCC ({ commmit }, data) {
            return api.loadTopoTreeInCC(data).then(response => response.data)
        },
        getTopoModelInCC ({ commit }, data) {
            return api.loadTopoModelInCC(data).then(response => response.data)
        },
        // <--- ip 选择器接口 end
        // 开区资源选择器接口 start --->
        getCCSearchTopoSet ({ commit }, data) {
            return api.getCCSearchTopoSet(data).then(response => response.data)
        },
        getCCSearchTopoResource ({ commit }, data) {
            return api.getCCSearchTopoResource(data).then(response => response.data)
        },
        getCCSearchModule ({ commit }, data) {
            return api.getCCSearchModule(data).then(response => response.data)
        },
        getCCSearchObjAttrHost ({ commit }, data) {
            return api.getCCSearchObjAttrHost(data).then(response => response.data)
        },
        getCCSearchColAttrSet ({ commit }, data) {
            return api.getCCSearchColAttrSet(data).then(response => response.data)
        },
        // <--- 开区资源选择器接口 end
        getPermissionUrl ({ commit }, data) {
            return api.getPermissionUrl(data).then(response => response.data)
        },
        queryUserPermission ({ commit }, data) {
            return api.queryUserPermission(data).then(response => response.data)
        }
    },
    getters: {},
    modules
})

export default store
