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
import api from '@/api/index.js'

const META_FORM_TYPE = {
    'select': 'select_meta'
}

const atomForm = {
    namespaced: true,
    state: {
        fetching: false,
        SingleAtomVersionMap: {},
        form: {},
        config: {
        },
        output: {}
    },
    getters: {
        SingleAtomVersionMap (state) {
            return state.SingleAtomVersionMap
        }
    },
    mutations: {
        setFetching (state, status) {
            state.fetching = status
        },
        setAtomForm (state, payload) {
            const atomType = payload.isMeta ? META_FORM_TYPE[payload.atomType] : payload.atomType
            const action = {}
            action[payload.version] = payload.data
            if (state.form[atomType]) {
                Vue.set(state.form, atomType, {
                    ...state.form[atomType],
                    ...action
                })
            } else {
                Vue.set(state.form, atomType, action)
            }
        },
        setAtomConfig (state, payload) {
            const action = {}
            action[payload.version] = payload.configData
            if (state.config[payload.atomType]) {
                Vue.set(state.config, payload.atomType, {
                    ...state.config[payload.atomType],
                    ...action
                })
            } else {
                Vue.set(state.config, payload.atomType, action)
            }
        },
        setAtomOutput (state, payload) {
            const action = {}
            action[payload.version] = payload.outputData
            if (state.output[payload.atomType]) {
                Vue.set(state.output, payload.atomType, {
                    ...state.output[payload.atomType],
                    ...action
                })
            } else {
                Vue.set(state.output, payload.atomType, action)
            }
        },
        setVersionMap (state, payload) {
            state.SingleAtomVersionMap = payload
        },
        clearAtomForm (state, payload) {
            $.atoms = {}
            state.form = {}
            state.config = {}
            state.output = {}
        }
    },
    actions: {
        /**
         * 加载标准插件配置项
         * @param {String} payload.atomType 节点类型
         * @param {String} payload.setName 自定义请求类型
         */
        async loadAtomConfig ({ commit, state }, payload) {
            const { atomType, classify, isMeta, saveName } = payload
            const atomClassify = classify || 'component'
            const setTypeName = saveName || atomType
            let version = payload.version
            version = atomClassify === 'variable' ? 'legacy' : version

            await api.getAtomFormURL(atomType, atomClassify, version, isMeta).then(async response => {
                const { output: outputData, form: formResource, form_is_embedded: embedded } = response.data

                commit('setAtomForm', { atomType: setTypeName, data: response.data, isMeta, version })
                commit('setAtomOutput', { atomType: setTypeName, outputData, version })

                // 标准插件配置项内嵌到 form 字段
                if (embedded) {
                    /*eslint-disable */
                    eval(formResource)
                    /*eslint-disable */
                    commit('setAtomConfig', { atomType: setTypeName, configData: $.atoms[setTypeName], version })
                    return Promise.resolve({ data: $.atoms[setTypeName] })
                }

                return await new Promise ((resolve, reject) => {
                    $.getScript(formResource, function(response) {
                        commit('setAtomConfig', {atomType: setTypeName, configData: $.atoms[setTypeName], version })
                        resolve(response)
                    })
                })
            })
        },
        loadSubflowConfig ({ commit }, payload) {
            const { templateId, version, common } = payload
            return api.getFormByTemplateId(templateId, version, common).then(
                response => response.data
            )
        }
    }
}

export default atomForm
