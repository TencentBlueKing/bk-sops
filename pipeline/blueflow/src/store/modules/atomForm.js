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
import { debug } from 'util'

const VAR_TYPE = {
    'var_ip_picker': 'variable',
    'password': 'variable',
    'select': 'variable'
}

const META_FORM_TYPE = {
    'select': 'select_meta'
}

const atomForm = {
    namespaced: true,
    state: {
        fetching: false,
        form: {},
        config: {},
        output: {}
    },
    mutations: {
        setFetching (state, status) {
            state.fetching = status
        },
        setAtomForm (state, payload) {
            let atomType = payload.isMeta ? META_FORM_TYPE[payload.atomType] : payload.atomType
            Vue.set(state.form, atomType, payload.data)
        },
        setAtomConfig (state, payload) {
            Vue.set(state.config, payload.atomType, payload.configData)
        },
        setAtomOutput (state, payload) {
            Vue.set(state.output, payload.atomType, payload.outputData)
        },
        clearAtomForm (state, payload) {
            $.atoms = {}
            state.form = {}
            state.config = {}
            state.output = {}
        }
    },
    actions: {
        loadAtomConfig ({commit, state}, payload) {
            const { atomType, isMeta } = payload
            const atomClassify = VAR_TYPE[atomType] || 'component'
            return api.$getAtomForm(atomType, atomClassify, isMeta || 0).then(
                response => response.data
            ).catch(e => {
                Promise.reject(e)
            })
        },
        loadSubflowConfig ({commit}, payload) {
            const { templateId, version, common } = payload
            return api.getFormByTemplateId(templateId, version, common).then(
                response => response.data
            )
        }
    }
}

export default atomForm