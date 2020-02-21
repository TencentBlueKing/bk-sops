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
/**
 * 异步获取插件配置列表
 * @param {String} atomUrl 配置文件 js 地址
 * @param {Boolean} isEmbedded 是为否嵌入式
 * @param {String} atomType 插件类型
 * @param {Boolean} atomType 是否输出类型
 */
const asyncGetAtomConfig = async function (atomUrl, isEmbedded, atomType, isOutput = false) {
    // 输入表单挂载名为 code
    // 输出表单挂载名为 code_output
    const type = isOutput ? atomType + '_output' : atomType
    if (!atomUrl) {
        return []
    }
    if (isEmbedded) {
        eval(atomUrl)
        return $.atoms[type]
    } else {
        const list = await new Promise((resolve, reject) => {
            $.getScript(atomUrl, function (response) {
                resolve($.atoms[type])
            })
        })
        return list
    }
}
const atomForm = {
    namespaced: true,
    state: {
        fetching: false,
        SingleAtomVersionMap: {},
        form: {}, // 插件所有信息(描述，输入，输出等)
        config: {}, // 输入-表单配置项
        output: {}, // 输出-表单初始值 data
        outputConfig: {} // 输出-表单配置项
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
        // 设置插件信息
        setAtomForm (state, payload) {
            const { isMeta, atomType, version, data } = payload
            const type = isMeta ? META_FORM_TYPE[atomType] : atomType
            if (state.form[type]) {
                Vue.set(state.form[type], version, data)
            } else {
                Vue.set(state.form, type, { [version]: data })
            }
        },
        // 设置输入配置
        setInputConfig (state, payload) {
            const { version, configList, atomType } = payload
            if (state.config[atomType]) {
                Vue.set(state.config[atomType], version, configList)
            } else {
                Vue.set(state.config, atomType, { [version]: configList })
            }
        },
        // 设置输出数据
        setAtomOutputData (state, payload) {
            const { version, atomType, outputData } = payload
            if (state.output[atomType]) {
                Vue.set(state.output[atomType], version, outputData)
            } else {
                Vue.set(state.output, atomType, { [version]: outputData })
            }
        },
        setVersionMap (state, payload) {
            state.SingleAtomVersionMap = payload
        },
        // 设置输出配置
        setOutputConfig (state, payload) {
            const { atomType, version, configList } = payload
            if (state.outputConfig[atomType]) {
                Vue.set(state.outputConfig[atomType], version, configList)
            } else {
                Vue.set(state.outputConfig, atomType, { [version]: configList })
            }
        },
        clearAtomForm (state, payload) {
            $.atoms = {}
            state.form = {}
            state.config = {}
            state.output = {}
            state.outputConfig = {}
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
            const type = saveName || atomType
            const version = atomClassify === 'variable' ? 'legacy' : payload.version

            const atomRes = await api.getAtomFormURL(atomType, atomClassify, version, isMeta)
            const {
                output: outputData,
                form: inputForm,
                form_is_embedded: isInputFormEmbedded,
                output_form: outputForm,
                embedded_output_form: isOutputFormEmbedded
            } = atomRes.data
            const result = {
                input: [],
                output: [],
                isRenderOutputForm: !!outputForm
            }
            commit('setAtomForm', { atomType: type, data: atomRes.data, isMeta, version })
            commit('setAtomOutputData', { atomType: type, outputData, version })
            if (outputForm) {
                result.output = await asyncGetAtomConfig(outputForm, isOutputFormEmbedded, type, true)
                commit('setOutputConfig', { atomType: type, version, configList: result.output })
            }
            if (inputForm) {
                result.input = await asyncGetAtomConfig(inputForm, isInputFormEmbedded, type)
                commit('setInputConfig', { atomType: type, version, configList: result.input })
            }
            return result
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
