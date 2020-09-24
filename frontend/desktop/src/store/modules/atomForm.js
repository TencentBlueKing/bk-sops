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
import axios from 'axios'
import store from '@/store/index.js'

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
        loadSingleAtomList ({ commit }, params) {
            return axios.get('api/v3/component/', { params }).then(response => response.data.objects)
        },
        /**
         * 加载全量子流程
         */
        loadSubflowList ({ commit }, data) {
            let url = ''
            const params = {}
            const { project_id, common } = data
            if (common) {
                url = 'api/v3/common_template/'
            } else {
                url = 'api/v3/template/'
                params['project__id'] = project_id
            }
            return axios.get(url, { params }).then(response => response.data)
        },
        /**
         * 加载标准插件配置项
         * @param {String} payload.atomType 节点类型
         * @param {String} payload.setName 自定义请求类型
         */
        async loadAtomConfig ({ commit, state }, payload) {
            const { name, atom, classify = 'component', isMeta, version = 'legacy', project_id } = payload
            const atomClassify = classify
            const atomFile = name || atom
            const atomVersion = atomClassify === 'component' ? version : 'legacy'
            const params = { project_id } // 业务下需要带 project_id，公共流程、插件开发等不需要传
            const url = atomClassify === 'component' ? `api/v3/component/${atomFile}/` : `api/v3/variable/${atomFile}/`

            // 变量暂时没有版本系统
            if (atomClassify === 'component') {
                params.version = atomVersion
            }
            params.meta = isMeta ? 1 : undefined

            await axios.get(url, { params }).then(async response => {
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
            const { project_id } = store.state.project
            const { templateId, version, common } = payload
            let url = ''
            if (common) {
                url = 'common_template/api/form/'
            } else {
                url = `template/api/form/${project_id}/`
            }

            return axios.get(url, {
                params: {
                    template_id: templateId,
                    version
                }
            }).then(response => response.data)
        }
    }
}

export default atomForm