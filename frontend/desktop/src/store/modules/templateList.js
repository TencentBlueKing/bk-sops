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
import api from '@/api'

const templateList = {
    namespaced: true,
    state: {
        templateListData: [],
        commonTemplateData: []
    },
    mutations: {
        setTemplateListData (state, payload) {
            const { list, isCommon } = payload
            if (isCommon) {
                state.commonTemplateData = list
            } else {
                state.templateListData = list
            }
        }
    },
    actions: {
        loadTemplateList ({ commit }, data) {
            return api.getTemplateList(data).then(response => response.data)
        },
        deleteTemplate ({ commit }, template_id) {
            return api.deleteTemplate(template_id).then(response => response.data.objects)
        },
        getBizPerson () {
            return api.getBizPerson().then(response => response.data)
        },
        getTemplatePersons ({ commit }, data) {
            return api.getTemplatePersons(data).then(response => response.data)
        },
        saveTemplatePersons ({ commit }, data) {
            return api.saveTemplatePersons(data).then(response => response.data)
        },
        templateUploadCheck ({ commit }, data) {
            return api.templateUploadCheck(data).then(response => response.data)
        },
        templateImport ({ commit }, data) {
            return api.templateImport(data).then(response => response.data)
        },
        templateExport ({ commit }, data) {
            return api.templateExport(data).then(response => response.data)
        }
    },
    getters: {}
}

export default templateList
