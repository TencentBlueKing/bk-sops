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
import store from '@/store/index.js'
import axios from 'axios'
import { fileDownload } from '@/api/fileDownload.js'

const templateList = {
    namespaced: true,
    actions: {
        loadTemplateList ({ commit }, data) {
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
            url = data.new ? url + 'list_with_top_collection/' : url
            const config = {}
            if (data.cancelToken) {
                config.cancelToken = data.cancelToken
                delete data.cancelToken
            }
            delete data.new
            return axios.get(url, {
                params: data,
                ...config
            }).then(response => {
                if (!('limit' in data)) {
                    return { results: response.data.data }
                } else {
                    return response.data.data
                }
            })
        },
        deleteTemplate ({ commit }, data) {
            const { templateId, common } = data
            let url = ''
            if (common) {
                url = 'api/v3/common_template/'
            } else {
                url = 'api/v3/template/'
            }

            return axios.delete(`${url}${templateId}/`).then(response => response.data)
        },
        // 我收藏的流程模板
        loadCollectTemplateList ({ commit }, data) {
            return axios.get('api/v3/collection_template/', {
                params: data
            }).then(response => response.data)
        },
        // 批量取消收藏流程模板
        batchCancelCollectTpl ({ commit }, data) {
            const { projectId, cancelList } = data
            return axios.post('collection/api/batch_cancel_collection/', {
                project_id: projectId,
                batch_cancel_collection_ids: cancelList }).then(response => response.data)
        },
        // 批量删除流程模板
        batchDeleteTpl ({ commit }, data) {
            const { ids, projectId, common } = data
            const url = common ? 'api/v4/common_template/batch_delete/' : `api/v4/project_template/${projectId}/batch_delete/`

            return axios.post(url, { template_ids: ids }).then(response => response.data)
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
         * yaml类型文件导入检查
         */
        yamlTplImportCheck ({ commit }, data) {
            return axios.post('template/api/upload_yaml_templates/', data, {
                headers: {
                    'content-type': 'application/form-data'
                }
            }).then(response => response.data)
        },
        /**
         * 导入yaml模板
         */
        yamlTplImport ({ commit }, data) {
            return axios.post('template/api/import_yaml_templates/', data, {
                headers: {
                    'content-type': 'application/form-data'
                }
            }).then(response => response.data)
        },
        /**
         * 导入dat模板
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
            const { common, list, type, is_full } = data
            const { project_id } = store.state.project
            let url = ''
            const params = {
                template_id_list: list,
                is_full
            }
            if (type === 'exportDatFile') {
                url = common ? 'common_template/api/export/' : `/template/api/export/${project_id}/`
            } else {
                url = '/template/api/export_yaml_templates/'
                if (common) {
                    params.template_type = 'common'
                } else {
                    params.template_type = 'project'
                    params.project_id = project_id
                }
            }

            return axios.post(url, params, {
                headers: {
                    responseType: 'arraybuffer'
                }
            }).then((res) => {
                let result
                if (res.headers['content-type'].indexOf('json') === -1) { // 处理arraybuffer数据
                    const { site_url } = store.state
                    const { project_id } = store.state.project
                    let filename = `${site_url}_${project_id}.bat`
                    const disposition = res.headers['content-disposition'].split(',')
                    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
                    const matches = filenameRegex.exec(disposition)
                    if (matches !== null && matches[1]) {
                        filename = matches[1].replace(/['"]/g, '')
                    }
                    fileDownload(res.data, filename)
                    result = { result: true }
                } else { // 处理json格式数据
                    const text = Buffer.from(JSON.stringify(res.data)).toString('utf8')
                    result = JSON.parse(text)
                }
                return result
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
