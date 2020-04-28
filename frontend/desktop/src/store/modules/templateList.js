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
import store from '@/store/index.js'
import axios from 'axios'
import { fileDownload } from '@/api/fileDownload.js'

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
            const { project_id } = store.state.project
            let url = ''
            if (data) {
                const { common } = data
                if (common) {
                    url = 'api/v3/common_template/'
                } else {
                    url = 'api/v3/template/'
                }
            } else {
                url = 'api/v3/template/'
            }
            const querystring = Object.assign({}, { 'project__id': project_id }, data)

            return axios.get(url, {
                params: querystring
            }).then(response => response.data)
        },
        deleteTemplate ({ commit }, data) {
            const { templateId, common } = data
            let url = ''
            if (common) {
                url = 'api/v3/common_template/'
            } else {
                url = 'api/v3/template/'
            }

            return axios.delete(`${url}${templateId}/`).then(response => response.data.objects)
        },
        /**
         * 检测上传模板合法性
         * @param {Object} data formData数据
         */
        templateUploadCheck ({ commit }, data) {
            const { project_id } = store.state.project
            let url = ''
            const { common, formData } = data

            if (common) {
                url = 'common_template/api/import_check/'
            } else {
                url = `template/api/import_check/${project_id}/`
            }

            return axios.post(url, formData, {
                headers: {
                    'content-type': 'application/form-data'
                }
            }).then(response => response.data)
        },
        /**
         * 导入模板
         * @param {Object} data {common是否是公共流程,formData数据}
         */
        templateImport ({ commit }, data) {
            const { formData, common } = data
            const { project_id } = store.state.project
            let url = ''
            if (common) {
                url = 'common_template/api/import/'
            } else {
                url = `template/api/import/${project_id}/`
            }
            return axios.post(url, formData, {
                headers: { 'content-type': 'application/form-data' }
            }).then(response => response.data)
        },
        /**
         * 导出模板
         * @param {String} data 模板列表数组字符串
         */
        templateExport ({ commit }, data) {
            const { common, list } = data
            const { project_id } = store.state.project
            let url = ''
            if (common) {
                url = 'common_template/api/export/'
            } else {
                url = `template/api/export/${project_id}/`
            }

            return axios.post(url, {
                template_id_list: list
            }, {
                headers: {
                    responseType: 'arraybuffer'
                }
            }).then(res => {
                if (res.headers['content-type'].indexOf('json') === -1) { // 处理arraybuffer数据
                    const { site_url } = store.state
                    const { project_id } = store.state.project
                    let filename = `${site_url}_${project_id}.bat`
                    const disposition = res.headers['content-disposition'].split(',')
                    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
                    const matches = filenameRegex.exec(disposition)
                    if (matches != null && matches[1]) {
                        filename = matches[1].replace(/['"]/g, '')
                    }
                    fileDownload(res.data, filename)
                    return { result: true }
                } else { // 处理json格式数据
                    const text = Buffer.from(res.data).toString('utf8')
                    return JSON.parse(text)
                }
            })
        },
        /**
         * 获取项目下的子流程有更新的模板
         * @param {*} data 项目参数
         */
        getExpiredSubProcess ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.get(`template/api/get_templates_with_expired_subprocess/${project_id}/`).then(response => response.data)
        }
    }
}

export default templateList
