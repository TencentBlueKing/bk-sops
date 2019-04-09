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
import Vue from 'vue'
import Vuex from 'vuex'
import modules from './modules/index.js'
import api from "@/api"

Vue.use(Vuex)

function getAppLang () {
    return getCookie('blueking_language')
}

// 用户类型
function getUserType () {
    let userType = ''
    if (window.IS_FUNCTOR === 1) {
        userType = 'functor'
    } else if (window.IS_AUDITOR === 1) {
        userType = 'auditor'
    } else {
        userType = 'maintainer'
    }
    return userType
}

const store = new Vuex.Store({
    strict: process.env.NODE_ENV !== 'production',
    state: {
        username: window.USERNAME,
        userType: getUserType(),
        hideHeader: window.HIDE_HEADER === 1,
        site_url: window.SITE_URL,
        app_id: window.APP_ID, // 轻应用 id
        view_mode: window.VIEW_MODE,
        cc_id: window.BIZ_CC_ID,
        lang: getAppLang(),
        bizList: [],
        templateId: '', // 轻应用页面全局 template_id
        notFoundPage: false,
        categorys: [],
        components: [],
        isSuperUser: window.IS_SUPERUSER === 1,
        v1_import_flag: window.IMPORT_V1_FLAG,
        rsa_pub_key: window.RSA_PUB_KEY,
        businessTimezone: window.BUSINESS_TIMEZONE
    },
    mutations: {
        setAppId (state, id) {
            state.app_id = id
        },
        setViewMode (state, mode) {
            state.view_mode = mode
        },
        setBizId (state, id) {
            state.cc_id = id
        },
        setBizList (state, data) {
            state.bizList = data
        },
        setTemplateId (state, id) {
            state.templateId = id
        },
        setNotFoundPage (state, val) {
            state.notFoundPage = val
        },
        setCategorys (state,data) {
            state.categorys = data
        },
        setSingleAtomList (state,data) {
            state.components = data
        },
        setBusinessTimezone (state, data) {
            state.businessTimezone = data
        }
    },
    actions: {
        getBizList ({commit}) {
            api.getBizList().then(response => {
                commit('setBizList', response.data.objects)
            })
        },
        changeDefaultBiz ({commit}, ccId) {
            return api.changeDefaultBiz(ccId).then(response => response.data)
        },
        getCategorys ({commit}) {
            api.getCategorys().then(response => {
                commit('setCategorys', response.data.data)
            })
        },
        getSingleAtomList ({commit}) {
            api.getSingleAtomList().then(response => {
                commit('setSingleAtomList', response.data.objects)
            })
        },
        getBusinessTimezone ({commit}) {
            api.getBusinessTimezone().then(response => {
                const data = response.data
                if (data.time_zone === undefined) {
                    commit('setBusinessTimezone', undefined)
                } else {
                    commit('setBusinessTimezone', data.time_zone)
                }
                
            })
        },
        getHostInCC ({commmit}, fields) {
            return api.loadHostInCC(fields).then(response => response.data)
        },
        getTopoTreeInCC ({commmit}) {
            return api.loadTopoTreeInCC().then(response => response.data)
        },
        getTopoModelInCC ({commit}) {
            return api.loadTopoModelInCC().then(response => response.data)
        }
    },
    getters: {},
    modules
})

export default store
