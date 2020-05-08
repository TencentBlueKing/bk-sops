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
import api from '@/api/index.js'

const META_FORM_TYPE = {
    'select': 'select_meta'
}

const atomForm = {
    namespaced: true,
    state: {
        form: {},
        config: {},
        output: {}
    },
    mutations: {
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
        clearAtomForm (state, payload) {
            $.atoms = {}
            state.form = {}
            state.config = {}
            state.output = {}
        }
    },
    actions: {
        /**
         * 加载全量标准插件
         */
        loadSingleAtomList ({ commit }) {
            return api.getSingleAtomList().then(response => response.data.objects)
        },
        /**
         * 加载全量子流程
         */
        loadSubflowList ({ commit }, data) {
            return api.getSubAtomList(data).then(response => response.data)
        },
        /**
         * 加载标准插件统计数据
         */
        queryAtomData ({ commit }, data) {
            return api.queryAtom(data).then(response => response.data)
        },
        /**
         * 加载标准插件配置项
         * @param {String} payload.atomType 节点类型
         * @param {String} payload.setName 自定义请求类型
         */
        async loadAtomConfig ({ commit, state }, payload) {
            const { name, atom, classify, isMeta, version } = payload
            const atomClassify = classify || 'component'
            const atomFile = name || atom
            const atomVersion = atomClassify === 'variable' ? 'legacy' : version

            await api.getAtomFormURL(atomFile, atomClassify, atomVersion, isMeta).then(async response => {
                const { output: outputData, form: formResource, form_is_embedded: embedded } = response.data

                commit('setAtomForm', { atomType: atom, data: response.data, isMeta, version: atomVersion })
                commit('setAtomOutput', { atomType: atom, outputData, version: atomVersion })

                // 标准插件配置项内嵌到 form 字段
                if (embedded) {
                    /*eslint-disable */
                    eval(formResource)
                    /*eslint-disable */
                    commit('setAtomConfig', { atomType: atom, configData: $.atoms[atom], version: atomVersion })
                    return Promise.resolve({ data: $.atoms[atom] })
                }

                return await new Promise ((resolve, reject) => {
                    $.getScript(formResource, function(response) {
                        commit('setAtomConfig', {atomType: atom, configData: $.atoms[atom], version: atomVersion })
                        resolve(response)
                    })
                })
            })
        },
        /**
         * 加载子流程参数详情
         * @param {String} payload.templateId 模板id
         * @param {String} payload.version 模板版本
         * @param {String} payload.common 是否为公共流程
         */
        loadSubflowConfig ({ commit }, payload) {
            const { templateId, version, common } = payload
            return api.getFormByTemplateId(templateId, version, common).then(
                response => response.data
            )
        }
    }
}

export default atomForm