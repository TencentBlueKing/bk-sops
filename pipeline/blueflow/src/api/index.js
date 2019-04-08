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
import axios from 'axios'
import qs from 'qs'
import './interceptors.js'
import store from '@/store/index.js'

import { getUrlSetting } from './urls.js'
import { fileDownload } from './fileDownload.js'

const axiosDefaults = require("axios/lib/defaults")

axiosDefaults.xsrfCookieName = window.APP_CODE + "_csrftoken"
axiosDefaults.xsrfHeaderName = "X-CSRFToken"
axiosDefaults.withCredentials = true
axiosDefaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

const fullURL = window.location.protocol + '//' + window.location.host

function request (opts){
    const defaultOptions = {
        method: 'GET',
        url: '',
        baseURL: fullURL,
        data: {},
        params: {}

    }
    const options = Object.assign({}, defaultOptions, opts)
    return axios(options)
}

const api = {
    /**
     * 异步请求url配置项
     * @param {String} path 路径名称
     */
    getPrefix (path) {
        const {site_url, cc_id} = store.state
        return getUrlSetting(site_url, cc_id)[path]
    },
    /**
     * 获取当前用户有权限业务
     */
    getBizList () {
        const prefixUrl = this.getPrefix('business')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    /**
     * 更新默认业务
     */
    changeDefaultBiz (ccId) {
        const prefixUrl = this.getPrefix('bizDefaultChange')
        const opts = {
            method: 'POST',
            url: `${prefixUrl}${ccId}/`,
            headers: { 'content-type': 'application/x-www-form-urlencoded' }
        }
        return request(opts)
    },
    /**
     * 获取管理员用户分组和列表
     */
    getBizPerson () {
        const prefixUrl = this.getPrefix('bizPerson')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                use_for: 'template_auth'
            }
        }
        return request(opts)
    },
    /**
     * 获取业务基础配置信息
     */
    getBusinessBaseInfo () {
        const { cc_id } = store.state
        const prefixUrl = this.getPrefix('businessBaseInfo')
        const opts = {
            method: 'GET',
            url: `${prefixUrl}${cc_id}/`
        }
        return request(opts)
    },
    /**
     * 获取模板列表
     * @param {Object} data 筛选条件
     */
    getTemplateList (data) {
        const { cc_id } = store.state
        let prefixUrl = ''
        if (data) {
            const {common} = data
            if (common) {
                prefixUrl = this.getPrefix('commonTemplate')
            } else {
                prefixUrl = this.getPrefix('template')
            }
        } else {
            prefixUrl = this.getPrefix('template')
        }
        const querystring = Object.assign({}, data, {business__cc_id: cc_id})
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: querystring
        }
        return request(opts)
    },
    /**
     * 删除模板
     */
    deleteTemplate (data) {
        const {templateId, common} = data
        let prefixUrl = ''
        if (common) {
            prefixUrl = this.getPrefix('commonTemplate')
        } else {
            prefixUrl = this.getPrefix('template')
        }
        const opts = {
            method: 'DELETE',
            url: `${prefixUrl}${templateId}/`
        }
        return request(opts)
    },
    /**
     * 获取标准插件列表
     */
    getSingleAtomList () {
        const prefixUrl = this.getPrefix('component')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    /**
     * 获取子流程列表
     */
    getSubAtomList (data) {
        let prefixUrl = ''
        const {ccId, common} = data
        if (common) {
            prefixUrl = this.getPrefix('commonTemplate')
        } else {
            prefixUrl = this.getPrefix('template')
        }
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                business__cc_id: ccId
            }
        }
        return request(opts)
    },
    /**
     * 获取标准插件节点配置项url
     * @param {String} type 标准插件code
     * @param {String} classify 标准插件分类
     */
    getAtomFormURL (type, classify, isMeta) {
        const prefixUrl = this.getPrefix(classify)
        let url = ''
        if (isMeta) {
            url = `${prefixUrl}${type}/?meta=1`
        } else {
            url = `${prefixUrl}${type}/`
        }
        const opts = {
            method: 'GET',
            url: url
        }
        return request(opts)
    },
    /**
     * 获取标准插件配置项，挂载到$.atom对象上
     * @param {String} type 标准插件code
     * @param {String} classify 标准插件分类
     */
    $getAtomForm (type, classify, isMeta) {
        return this.getAtomFormURL(type, classify, isMeta).then(response => {
            const { output: outputData, form: url } = response.data
            store.commit('atomForm/setAtomForm', {atomType: type, data: response.data, isMeta})
            store.commit('atomForm/setAtomOutput', {atomType: type, outputData})
            return $.getScript(url)
        }).catch(e => {
            return Promise.reject(e)
        })
    },
    /**
     * 获取模板数据
     * @param {String} template_id 模板id
     */
    getTemplateData (data) {
        const {templateId, common} = data
        let prefixUrl = ''
        if (common) {
            prefixUrl = this.getPrefix('commonTemplate')
        } else {
            prefixUrl = this.getPrefix('template')
        }
        const opts = {
            method: 'GET',
            url: `${prefixUrl}${templateId}/`
        }
        return request(opts)
    },
    /**
     * 获取模板对应有权限人员列表
     * @param {String} data 包含templateId 模板Id, common 是否是公共流程
     */
    getTemplatePersons (data) {
        const {cc_id} = store.state
        const {templateId, common} = data
        let prefixUrl = ''
        const params = {
            template_id: templateId
        }
        if (common) {
            prefixUrl = this.getPrefix('commonTemplatePersons')
            params['biz_cc_id'] = cc_id
        } else {
            prefixUrl = this.getPrefix('templatePersons')
        }
        const opts = {
            method: 'GET',
            url: `${prefixUrl}`,
            params: params
        }
        return request(opts)
    },
    /**
     * 更新模板对人有权限人员列表
     * @param {Object} data 模板人员配置数据
     */
    saveTemplatePersons (data) {
        const {cc_id} = store.state
        const { templateId, createTask, fillParams, executeTask, common } = data
        let prefixUrl = ''
        const bodyData = {
            template_id: templateId,
            create_task: JSON.stringify(createTask),
            fill_params: JSON.stringify(fillParams),
            execute_task: JSON.stringify(executeTask)
        }
        if (common) {
            prefixUrl = this.getPrefix('commonTemplatePersonsSave')
            bodyData['biz_cc_id'] = cc_id
        } else {
            prefixUrl = this.getPrefix('templatePersonsSave')
        }
        const opts = {
            method: 'POST',
            url: `${prefixUrl}`,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: qs.stringify(bodyData)
        }
        return request(opts)
    },
    /**
     * 模板收藏
     * @param {String} list 模板列表
     */
    templateCollectSelect (list) {
        const prefixUrl = this.getPrefix('templateCollect')
        const data = qs.stringify({
            template_list: list
        })
        const opts = {
            method: 'POST',
            url: `${prefixUrl}`,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data
        }
        return request(opts)
    },
    /**
     * 删除收藏模板
     * @param {String} template_id 模板id
     */
    templateCollectDelete (template_id) {
        const prefixUrl = this.getPrefix('templateCollect')
        const data = qs.stringify({
            'method': 'remove',
            template_id
        })
        const opts = {
            method: 'POST',
            url: `${prefixUrl}`,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data
        }
        return request(opts)
    },
    /**
     * 检测上传模板合法性
     * @param {Object} data formData数据
     */
    templateUploadCheck (data) {
        let prefixUrl = ''
        const {common, formData} = data
        if (common) {
            prefixUrl = this.getPrefix('commonTemplateUploadCheck')
        } else {
            prefixUrl = this.getPrefix('templateUploadCheck')
        }
        const opts = {
            method: 'POST',
            url: `${prefixUrl}`,
            headers: { 'content-type': 'application/form-data' },
            data: formData
        }
        return request(opts)
    },
    /**
     * 导入模板
     * @param {Object} data {common是否是公共流程,formData数据}
     */
    templateImport (data) {
        const {formData, common} = data
        let prefixUrl = ''
        if (common) {
            prefixUrl = this.getPrefix('commonTemplateImport')
        } else {
            prefixUrl = this.getPrefix('templateImport')
        }
        const opts = {
            method: 'POST',
            url: `${prefixUrl}`,
            headers: { 'content-type': 'application/form-data' },
            data: formData
        }
        return request(opts)
    },
    /**
     * 导出模板
     * @param {String} data 模板列表数组字符串
     */
    templateExport (data) {
        const {common, list} = data
        let prefixUrl = ''
        if (common) {
            prefixUrl = this.getPrefix('commonTemplateExport')
        } else {
            prefixUrl = this.getPrefix('templateExport')
        }
        const opts = {
            method: 'GET',
            url: `${prefixUrl}`,
            responseType: 'arraybuffer',
            params: {
                template_id_list: list
            }
        }
        return request(opts).then(res => {
            if (res.headers['content-type'].indexOf('json') === -1) { // 处理arraybuffer数据
                const { site_url, cc_id } = store.state
                let filename = `${site_url}_${cc_id}.bat`
                const disposition = res.headers['content-disposition'].split(',')
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
                const matches = filenameRegex.exec(disposition)
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '')
                }
                fileDownload(res.data, filename)
                return {
                    data: {
                        result: true
                    }
                }
            } else { // 处理json格式数据
                const text = Buffer.from(res.data).toString('utf8')
                const data = JSON.parse(text)
                return { data }
            }
        })
    },
    /**
     * 获取子流程模板表单配置数据
     * @param {String} template_id 模板id
     * @param {String} version 版本
     */
    getFormByTemplateId (templateId, version, common) {
        let prefixUrl = ''
        if (common) {
            prefixUrl = this.getPrefix('commonSubAtom')
        } else {
            prefixUrl = this.getPrefix('subform')
        }
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                template_id: templateId,
                version
            }
        }
        return request(opts)
    },
    /**
     * 保存模板数据
     * @param {Object} data 模板完整数据
     */
    saveTemplate (data) {
        const { ccId ,name, templateId, pipelineTree, category, notifyReceivers, notifyType, timeout, common } = data
        let prefixUrl = ''
        if (common) {
            prefixUrl = this.getPrefix('commonTemplate')
        } else {
            prefixUrl = this.getPrefix('template')
        }
        const business = this.getPrefix('business') + ccId + '/'
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                name,
                pipeline_tree: pipelineTree,
                business: business,
                category,
                notify_receivers: notifyReceivers,
                notify_type: notifyType,
                timeout
            }
        }
        if (templateId != undefined) {
            opts.url = `${prefixUrl}${templateId}/`
            opts.headers = {'X-HTTP-Method-Override': 'PATCH'}
        }
        return request(opts)
    },
    /**
     * 获取任务列表
     * @param {Object} data 筛选条件
     */
    getTaskList (data) {
        const { cc_id } = store.state
        const {common, template_id} = data
        const querystring = Object.assign({}, data, {business__cc_id: cc_id})
        const prefixUrl = this.getPrefix('instance')
        if (template_id) {
            querystring['template_source'] = 'business'
        }
        if (common) {
            querystring['template_source'] = 'common'
        }
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: querystring
        }
        return request(opts)
    },
    /**
     * 删除任务
     * @param {String} task_id 任务id
     */
    deleteTask (task_id) {
        const prefixUrl = this.getPrefix('instance')
        const opts = {
            method: 'DELETE',
            url: `${prefixUrl}${task_id}/`
        }
        return request(opts)
    },
    /**
     * 克隆任务
     * @param {Object} 包含：task_id 任务id；name 任务名称
     */
    cloneTask (data) {
        const { task_id, name } = data
        const prefixUrl = this.getPrefix('instanceClone')
        const { app_id, view_mode } = store.state
        const dataString = qs.stringify({
            name,
            instance_id: task_id,
            create_method: view_mode == 'appmaker' ? 'app_maker' : 'app',
            create_info: app_id
        })
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: dataString
        }
        return request(opts)
    },
    /**
     * 获取任务可选节点的选择方案
     * @param {Object} data 筛选条件
     */
    getTaskScheme (data) {
        const prefixUrl = this.getPrefix('schemes')
        const { cc_id, template_id } = data
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                'biz_cc_id': cc_id,
                'template__template_id': template_id
            }
        }
        return request(opts)
    },
    /**
     * 创建任务可选节点的选择方案
     * @param {Object}} schemeData 方案配置数据
     */
    createTaskScheme (schemeData) {
        const prefixUrl = this.getPrefix('schemes')
        const { cc_id, template_id, data, name } = schemeData
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                template_id,
                data,
                name,
                biz_cc_id: cc_id
            }
        }
        return request(opts)
    },
    /**
     * 删除任务节点选择方案
     * @param {String} schemeId 方案id
     */
    deleteTaskScheme (schemeId) {
        const prefixUrl = this.getPrefix('schemes')
        const opts = {
            method: 'DELETE',
            url: `${prefixUrl}${schemeId}/`
        }
        return request(opts)
    },
    /**
     * 获取任务节点选择方案详情
     * @param {String} schemeId 方案id
     */
    getSchemeDetail (schemeId) {
        const prefixUrl = this.getPrefix('schemes')
        const opts = {
            method: 'GET',
            url: `${prefixUrl}${schemeId}/`
        }
        return request(opts)
    },
    /**
     * 获取任务节点预览数据
     * @param {Object} data 筛选条件
     */
    getPreviewNodeData (data) {
        const prefixUrl = this.getPrefix('instancePreview')
        const {templateId, excludeTaskNodesId, common} = data
        const dataJson = {
            template_id: templateId,
            exclude_task_nodes_id: excludeTaskNodesId,
            template_source: 'business'
        }
        if (common) {
            dataJson['template_source'] = 'common'
        }
        const dataString = qs.stringify(dataJson)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: dataString
        }
        return request(opts)
    },
    /**
     * 创建任务
     * @param {Object} data 模板数据
     */
    createTask (data) {
        const { cc_id, app_id, view_mode, username } = store.state
        const {templateId, name, description, execData, flowType, common} = data
        const prefixUrl = this.getPrefix('instance')
        const requestData = {
            'business': `api/v3/business/${cc_id}/`,
            'template_id': templateId,
            'creator': username,
            'name': name,
            'description': description,
            'pipeline_tree': execData,
            'create_method': view_mode == 'appmaker' ? 'app_maker' : 'app',
            'create_info': app_id,
            'flow_type': flowType,
            'template_source': 'business'
        }
        if (common) {
            requestData['template_source'] = 'common'
        }
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: requestData
        }
        return request(opts)
    },
    /**
     * 获取任务实例详细数据
     * @param {String} instance_id 实例id
     */
    getTaskInstanceData (instance_id) {
        const prefixUrl = this.getPrefix('instance')
        const opts = {
            method: 'GET',
            url: `${prefixUrl}${instance_id}/`
        }
        return request(opts)
    },
    /**
     * 职能化认领
     * @param {String} data 模板数据
     */
    claimFuncTask (data) {
        const prefixUrl = this.getPrefix('instanceClaim')
        const requestData = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: requestData
        }

        return request(opts)
    },
    /**
     * 获取任务实例状态信息
     * @param {String} instance_id 实例id
     */
    getInstanceStatus (data) {
        const {instance_id, cc_id} = data
        const prefixUrl = this.getPrefix('instanceStatus')
        const opts = {
            method: 'GET',
            url: `${prefixUrl}${cc_id}/`,
            params: {
                instance_id
            }
        }

        return request(opts)
    },
    /**
     * 开始执行任务实例
     * @param {String} instance_id 实例id
     */
    instanceStart (instance_id) {
        const prefixUrl = this.getPrefix('instanceStart')
        const data = qs.stringify({instance_id: instance_id})
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 暂停执行任务实例
     * @param {String} instance_id 实例id
     */
    instancePause (instance_id) {
        const prefixUrl = this.getPrefix('instancePause')
        const data = qs.stringify({instance_id: instance_id})
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 继续执行子任务
     * @param {Object} data 子任务数据
     */
    subInstanceResume (data) {
        const { instance_id, node_id } = data
        const prefixUrl = this.getPrefix('resumeSubProcess')
        const dataString = qs.stringify({instance_id: instance_id, node_id: node_id})
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: dataString
        }

        return request(opts)
    },
    /**
     * 继续执行任务实例
     * @param {String} instance_id 任务id
     */
    instanceResume (instance_id) {
        const prefixUrl = this.getPrefix('instanceResume')
        const data = qs.stringify({instance_id: instance_id})
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 暂停子流程任务
     * @param {Object} data 子任务数据
     */
    subInstancePause (data) {
        const { instance_id, node_id } = data
        const prefixUrl = this.getPrefix('pauseSubProcess')
        const dataString = qs.stringify({instance_id: instance_id, node_id: node_id})
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: dataString
        }

        return request(opts)
    },
    /**
     * 撤销任务实例执行
     * @param {String} instance_id 任务实例id
     */
    instanceRevoke (instance_id) {
        const prefixUrl = this.getPrefix('instanceRevoke')
        const data = qs.stringify({instance_id: instance_id})
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 修改实例参数
     * @param {Object} data 表单配置数据
     */
    instanceModifyParams (data) {
        const prefixUrl = this.getPrefix('instanceModify')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 获取节点执行详情
     * @param {Object} data 节点配置数据
     */
    getNodeActDetail (data) {
        const prefixUrl = this.getPrefix('nodeActDetails')
        const {instance_id, node_id, component_code, subprocess_stack} = data
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                instance_id,
                node_id,
                component_code,
                subprocess_stack
            }
        }

        return request(opts)
    },
    /**
     * 获取作业执行详情
     * @param {Object} data 作业实例ID等信息
     */
    getJobInstanceLog (data) {
        const prefixUrl = this.getPrefix('jobInstanceLog')
        const {job_instance_id} = data
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                job_instance_id
            }
        }

        return request(opts)
    },
    /**
     * 获取节点执行信息
     * @param {Object} data 节点配置数据
     */
    getNodeActInfo (data) {
        const prefixUrl = this.getPrefix('nodeActInfo')
        const {instance_id, node_id, component_code, subprocess_stack} = data
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                instance_id,
                node_id,
                component_code,
                subprocess_stack
            }
        }

        return request(opts)
    },
    /**
     * 重试任务实例
     * @param {Object} data 任务实例数据
     */
    instanceRetry (data) {
        const prefixUrl = this.getPrefix('nodeRetry')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 设置定时间节点时间
     * @param {Object} data 节点配置数据
     */
    setSleepNode (data) {
        const prefixUrl = this.getPrefix('setSleepNode')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 跳过失败节点
     * @param {Object} data 节点配置数据
     */
    instanceNodeSkip (data) {
        const prefixUrl = this.getPrefix('nodeSkip')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 跳过分支网关节点
     * @param {Object} data 节点配置数据
     */
    instanceBranchSkip (data) {
        const prefixUrl = this.getPrefix('skipExclusiveGateway')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 跳过汇聚网关节点
     * @param {Object} data 节点配置数据
     */
    skipExclusiveGateway (data) {
        const prefixUrl = this.getPrefix('skipExclusiveGateway')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 暂停节点继续
     * @param {Object} data 节点配置数据
     */
    pauseNodeResume (data) {
        const prefixUrl = this.getPrefix('pauseNodeResume')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }

        return request(opts)
    },
    /**
     * 获取任务分类数据
     * @param {Object} query 筛选条件
     */
    loadTaskCount (query) {
        const prefixUrl = this.getPrefix('taskCount')
        const querystring = Object.assign({}, query)
        const data = qs.stringify(querystring)
        const opts = {
            method: 'POST',
            url: `${prefixUrl}`,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data
        }

        return request(opts)
    },
    /**
     * 获取业务配置
     */
    loadBizConfig () {
        const { cc_id } = store.state
        const prefixUrl = this.getPrefix('bizConfig')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    /**
     * 配置任务执行人员
     * @param {Object} data 配置信息
     */
    configBizExecutor (data) {
        const prefixUrl = this.getPrefix('configBizExecutor')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: `${prefixUrl}`,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data
        }

        return request(opts)
    },
    /**
     * 加载轻应用数据
     */
    loadAppmaker () {
        const { cc_id } = store.state
        const prefixUrl = this.getPrefix('appmaker')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                business__cc_id: cc_id
            }
        }
        return request(opts)
    },
    /**
     * 加载轻应用总数
     */
    loadAppmakerSummary (data) {
        const prefixUrl = this.getPrefix('appmakerSummary')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                group_by: data['groupBy']
            }
        }
        return request(opts)
    },
    /**
     * 加载对应轻应用详情
     * @param {String} id 轻应用id
     */
    loadAppmakerDetail (id) {
        const prefixUrl = this.getPrefix('appmaker')
        const opts = {
            method: 'GET',
            url: `${prefixUrl}${id}/`,
            params: {
                appmaker_id: id
            }
        }

        return request(opts)
    },
    /**
     * 编辑轻应用
     * @param {Object} data 轻应用数据
     */
    appmakerEdit (data) {
        const prefixUrl = this.getPrefix('appmakerEdit')
        const opts = {
            method: 'POST',
            url: `${prefixUrl}`,
            headers: { 'content-type': 'multipart/form-data' },
            data
        }

        return request(opts)
    },
    /**
     * 删除轻应用
     * @param {String} id 轻应用id
     */
    appmakerDelete (id) {
        const prefixUrl = this.getPrefix('appmaker')
        const opts = {
            method: 'DELETE',
            url: `${prefixUrl}${id}/`
        }

        return request(opts)
    },
    queryTemplate (data) {
        const prefixUrl = this.getPrefix('analysisTemplate')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }
        return request(opts)
    },
    queryAtom (data) {
        const prefixUrl = this.getPrefix('analysisAtom')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }
        return request(opts)
    },
    queryInstance (data) {
        const prefixUrl = this.getPrefix('analysisInstance')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }
        return request(opts)
    },
    queryAppmaker (data) {
        const prefixUrl = this.getPrefix('analysisAppmaker')
        data = qs.stringify(data)
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: data
        }
        return request(opts)
    },
    getCategorys () {
        const prefixUrl = this.getPrefix('categorys')
        const opts = {
            method: 'Get',
            url: prefixUrl
        }
        return request(opts)
    },
    getFunctionTaskList (data) {
        const prefixUrl = this.getPrefix('function')
        const querystring = Object.assign({}, data)
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: querystring
        }
        return request(opts)
    },
    loadFunctionBusinessList () {
        const prefixUrl = this.getPrefix('business')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    loadFunctionTemplateList (cc_id) {
        const prefixUrl = this.getPrefix('template')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                business__cc_id: cc_id
            }
        }
        return request(opts)
    },
    loadAuditTaskList (data) {
        const prefixUrl = this.getPrefix('instance')
        const querystring = Object.assign({}, data)
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: querystring
        }
        return request(opts)
    },
    loadTemplateSummary (data) {
        const prefixUrl = this.getPrefix('templateSummary')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                group_by: data['groupBy']
            }
        }
        return request(opts)
    },
    /**
     * 创建定时任务
     * @param {Object} data 包含 template_id模板名称, name定时名称, cron定时表达式
     */
    createPeriodic (data) {
        const prefixUrl = this.getPrefix('periodic')
        const { cc_id } = store.state
        const requestData = {
            'business': `api/v3/business/${cc_id}/`
        }
        const {name, cron, templateId, execData} = data
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                business: `api/v3/business/${cc_id}/`,
                cron: cron,
                name: name,
                template_id: templateId,
                pipeline_tree: execData
            }
        }
        return request(opts)
    },
    /**
     * 获取定时任务列表
     * @param {Object} data 筛选条件
     */
    getPeriodicList (data) {
        const { cc_id } = store.state
        const querystring = Object.assign({}, data, {business__cc_id: cc_id})
        const prefixUrl = this.getPrefix('periodic')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: querystring
        }
        return request(opts)
    },
    loadCreateMethod () {
        const prefixUrl = this.getPrefix('taskCreateMethod')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    loadTemplateCollectList () {
        const prefixUrl = this.getPrefix('templateCollectList')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    /**
     * 设置定时任务执行状态
     * @param {Object} data task_id 定时任务id, enabled 需要切换的状态
     */
    setPeriodicEnable (data) {
        const {enabled, taskId} = data
        const prefixUrl = this.getPrefix('periodicEnable') + taskId + '/'
        const dataString = qs.stringify({
            enabled
        })
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: dataString
        }
        return request(opts)
    },
    /**
     * 修改定时任务表达式
     * @param {Object} data task_id 定时任务id, cron 表达式
     */
    modifyPeriodicCron (data) {
        const {cron, taskId} = data
        const prefixUrl = this.getPrefix('periodicModifyCron') + taskId + '/'
        const dataString = qs.stringify({
            'cron': cron
        })
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: dataString
        }
        return request(opts)
    },
    getPeriodic (data) {
        const { cc_id } = store.state
        const {taskId} = data
        const querystring = Object.assign({}, {business__cc_id: cc_id})
        const prefixUrl = this.getPrefix('periodic') + taskId + '/'
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: querystring
        }
        return request(opts)
    },
    modifyPeriodicConstants (data) {
        const {constants, taskId} = data
        const prefixUrl = this.getPrefix('periodicModifyConstants') + taskId + '/'
        const dataString = qs.stringify({
            'constants': constants
        })
        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
            data: dataString
        }
        return request(opts)
    },
    deletePeriodic (id) {
        const prefixUrl = this.getPrefix('periodic')
        const opts = {
            method: 'DELETE',
            url: `${prefixUrl}${id}/`
        }
        return request(opts)
    },
    getBusinessTimezone () {
        const { cc_id } = store.state
        const prefixUrl = this.getPrefix('business') + cc_id + '/'

        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    
    /**
     * 查询业务在 CMDB 的主机
     * @param {Array} filels 主机查询字段
     */
    loadHostInCC (fields) {
        const prefixUrl = this.getPrefix('cc_search_host')
        
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                fields: JSON.stringify(fields)
            }
        }
        return request(opts)
    },
    /**
     * 查询业务在 CMDB 的拓扑树
     */
    loadTopoTreeInCC () {
        const prefixUrl = this.getPrefix('cc_search_topo_tree')
        
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    /**
     * 查询业务在 CMDB 的拓扑模型
     */
    loadTopoModelInCC () {
        const prefixUrl = this.getPrefix('cc_get_mainline_object_topo')
        
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    }
}

export default api
