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
import axios from 'axios'
import qs from 'qs'
import './interceptors.js'
import store from '@/store/index.js'

import { getUrlSetting } from './urls.js'

const axiosDefaults = require('axios/lib/defaults')

axiosDefaults.xsrfCookieName = window.APP_CODE + '_csrftoken'
axiosDefaults.xsrfHeaderName = 'X-CSRFToken'
axiosDefaults.withCredentials = true
axiosDefaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

const fullURL = window.location.protocol + '//' + window.location.host

export function request (opts) {
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
        const { site_url } = store.state
        const { project_id } = store.state.project
        return getUrlSetting(site_url, project_id)[path]
    },
    /**
     * 加载轻应用数据
     */
    loadAppmaker (data) {
        const prefixUrl = this.getPrefix('appmaker')
        const querystring = Object.assign({}, data)
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: querystring
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
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data
        }
        return request(opts)
    },
    queryAtom (data) {
        const prefixUrl = this.getPrefix('analysisAtom')
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data
        }
        return request(opts)
    },
    queryInstance (data) {
        const prefixUrl = this.getPrefix('analysisInstance')
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data
        }
        return request(opts)
    },
    queryAppmaker (data) {
        const prefixUrl = this.getPrefix('analysisAppmaker')
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data
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
    /**
     * 创建定时任务
     * @param {Object} data 包含 template_id模板名称, name定时名称, cron定时表达式
     */
    createPeriodic (data) {
        const prefixUrl = this.getPrefix('periodic')
        const { project_id } = store.state.project
        const { name, cron, templateId, execData, templateSource } = data
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                project: `api/v3/project/${project_id}/`,
                cron: cron,
                name: name,
                template_id: templateId,
                pipeline_tree: execData,
                template_source: templateSource
            }
        }
        return request(opts)
    },
    /**
     * 获取定时任务列表
     * @param {Object} data 筛选条件
     */
    getPeriodicList (data) {
        const prefixUrl = this.getPrefix('periodic')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: { ...data }
        }
        return request(opts)
    },
    /**
     * 设置定时任务执行状态
     * @param {Object} data task_id 定时任务id, enabled 需要切换的状态
     */
    setPeriodicEnable (data) {
        const { enabled, taskId } = data
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
        const { cron, taskId } = data
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
        const { project_id } = store.state.project
        const { taskId } = data
        const querystring = Object.assign({}, { 'project_id': project_id })
        const prefixUrl = this.getPrefix('periodic') + taskId + '/'
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: querystring
        }
        return request(opts)
    },
    modifyPeriodicConstants (data) {
        const { constants, taskId } = data
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
    /**
     * 加载插件包源配置
     * @param {Object} fields 包源查询字段
     */
    loadPackageSource (fields) {
        const prefixUrl = this.getPrefix('packageSource')
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
     * 新增插件包源配置
     * @param {Object} data 插件包源配置
     */
    createPackageSource (data) {
        const { origins, caches } = data
        const prefixUrl = this.getPrefix('packageSource')

        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                origins,
                caches
            }
        }
        return request(opts)
    },
    /**
     * 删除所有插件包源
     */
    deletePackageSource (data) {
        const prefixUrl = this.getPrefix('packageSource')

        const opts = {
            method: 'DELETE',
            url: prefixUrl,
            data
        }
        return request(opts)
    },
    /**
     * 更新插件包源配置
     * @param {Object} data 插件包源配置
     */
    updatePackageSource (data) {
        const { origins, caches } = data
        const prefixUrl = this.getPrefix('packageSource')

        const opts = {
            method: 'POST',
            url: prefixUrl,
            headers: {
                'content-type': 'application/json',
                'X-HTTP-Method-Override': 'PATCH'
            },
            data: {
                origins,
                caches
            }
        }
        return request(opts)
    },
    /**
     * 加载远程包源同步任务列表
     */
    loadSyncTask (params) {
        const { limit, offset } = params
        const prefixUrl = this.getPrefix('syncTask')

        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                limit,
                offset
            }
        }
        return request(opts)
    },
    /**
     * 创建远程包源同步
     */
    createSyncTask () {
        const creator = store.state.username
        const create_method = 'manual'
        const prefixUrl = this.getPrefix('syncTask')

        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                creator,
                create_method
            }
        }
        return request(opts)
    },
    /**
     * 获取人员列表
     */
    getMemberList () {
        const prefixUrl = this.getPrefix('userList')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    loadApiList () {
        const prefixUrl = this.getPrefix('esbGetSystems')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    loadApiComponent (params) {
        const { name } = params
        const prefixUrl = this.getPrefix('esbGetComponents')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                system_names: JSON.stringify(name)
            }
        }
        return request(opts)
    },
    loadApiPluginCode (params) {
        const { system, component } = params
        const prefixUrl = this.getPrefix('esbGetPluginInitialCode')

        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                esb_system: system,
                esb_component: component
            }
        }
        return request(opts)
    },
    adminSearch (data) {
        const prefixUrl = this.getPrefix('adminSearch')
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                keyword: data.keyword
            }
        }
        return request(opts)
    },
    adminTemplate (data) {
        const prefixUrl = this.getPrefix('adminTemplate')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: { ...data }
        }
        return request(opts)
    },
    adminTemplateRestore (data) {
        const { template_id } = data
        const prefixUrl = this.getPrefix('adminTemplateRestore')
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                template_id
            }
        }
        return request(opts)
    },
    adminTaskflow (data) {
        const prefixUrl = this.getPrefix('adminTaskflow')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: { ...data }
        }
        return request(opts)
    },
    adminTaskflowDetail (data) {
        const { task_id } = data

        const prefixUrl = this.getPrefix('adminTaskflowDetail')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                task_id
            }
        }
        return request(opts)
    },
    adminTaskflowHistroyLog (data) {
        const prefixUrl = this.getPrefix('adminTaskflowHistroyLog')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: { ...data }
        }
        return request(opts)
    },
    adminTaskflowNodeForceFail (data) {
        const { task_id, node_id } = data
        const prefixUrl = this.getPrefix('taskflowNodeForceFail')
        const opts = {
            method: 'POST',
            url: prefixUrl,
            data: {
                task_id,
                node_id
            }
        }
        return request(opts)
    },
    adminTaskflowNodeDetail (data) {
        const prefixUrl = this.getPrefix('adminTaskflowNodeDetail')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: { ...data }
        }
        return request(opts)
    },
    adminPeriodTask (data) {
        const prefixUrl = this.getPrefix('adminPeriodTask')
        const opts = {
            method: 'GET',
            url: prefixUrl
        }
        return request(opts)
    },
    adminPeriodTaskHistory (data) {
        const { task_id } = data
        const prefixUrl = this.getPrefix('adminPeriodTaskHistory')
        const opts = {
            method: 'GET',
            url: prefixUrl,
            params: {
                task_id
            }
        }
        return request(opts)
    }
}

export default api
