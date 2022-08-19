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
import Vue from 'vue'
import nodeFilter from '@/utils/nodeFilter.js'
import { uuid, random4 } from '@/utils/uuid.js'
import tools from '@/utils/tools.js'
import validatePipeline from '@/utils/validatePipeline.js'
import axios from 'axios'
import i18n from '@/config/i18n/index.js'

const ATOM_TYPE_DICT = {
    startpoint: 'EmptyStartEvent',
    endpoint: 'EmptyEndEvent',
    tasknode: 'ServiceActivity',
    subflow: 'SubProcess',
    parallelgateway: 'ParallelGateway',
    branchgateway: 'ExclusiveGateway',
    convergegateway: 'ConvergeGateway',
    conditionalparallelgateway: 'ConditionalParallelGateway'
}
// 默认流程模板，默认节点
const generateInitLocation = () => {
    return [
        {
            id: 'node' + uuid(),
            x: 40,
            y: 150,
            type: 'startpoint'
        },
        {
            id: 'node' + uuid(),
            x: 240,
            y: 140,
            name: '',
            stage_name: '',
            type: 'tasknode'
        },
        {
            id: 'node' + uuid(),
            x: 540,
            y: 150,
            type: 'endpoint'
        }
    ]
}
// 默认流程模板，activities 字段
const generateInitActivities = (location, line) => {
    return {
        [location[1].id]: {
            component: {
                version: undefined,
                code: undefined,
                data: undefined
            },
            error_ignorable: false,
            id: location[1].id,
            incoming: [line[0].id],
            loop: null,
            name: '',
            optional: true,
            outgoing: line[1].id,
            stage_name: '',
            type: 'ServiceActivity',
            retryable: true,
            skippable: true,
            auto_retry: {
                enable: false,
                interval: 0,
                times: 1
            },
            timeout_config: {
                enable: false,
                seconds: 10,
                action: 'forced_fail'
            }
        }
    }
}
// 默认流程模板，开始节点
const generateStartNode = (location, line) => {
    return {
        id: location.id,
        incoming: '',
        name: '',
        outgoing: line.id,
        type: 'EmptyStartEvent'
    }
}
// 默认流程模板，结束节点
const generateEndNode = (location, line) => {
    return {
        id: location.id,
        incoming: [line.id],
        name: '',
        outgoing: '',
        type: 'EmptyEndEvent'
    }
}
// 默认流程模板，初始化 line 字段
const generateInitLine = (location) => {
    const line = []
    const locationLength = location.length
    if (locationLength < 2) {
        return line
    }

    location.forEach((item, index) => {
        if (index > locationLength - 2) {
            return
        }
        line.push({
            id: 'line' + uuid(),
            source: {
                arrow: 'Right',
                id: item.id
            },
            target: {
                arrow: 'Left',
                id: location[index + 1].id
            }
        })
    })
    return line
}
// 默认流程模板，初始化 flows 字段
const generateInitFlow = (line) => {
    const flow = {}
    line.forEach((item) => {
        flow[item.id] = {
            id: item.id,
            is_default: false,
            source: item.source.id,
            target: item.target.id
        }
    })
    return flow
}

/**
 * 更新数据的 incoming 字段，兼容旧数据 string => array
 * @param {String、Array} data 原始数据
 * @param {String} id 待新增或删除数据
 * @param {String} type 操作类型，新增(add)或删除(delete)
 */
const updateIncoming = (incoming, id, type) => {
    let data = Array.isArray(incoming) ? incoming.slice(0) : incoming
    if (type === 'add') {
        if (Array.isArray(data)) {
            data.push(id)
        } else {
            data = data === '' ? [id] : [data, id]
        }
    } else {
        if (Array.isArray(data)) {
            data = data.filter(line => line !== id)
        } else {
            data = []
        }
    }
    return data
}

const template = {
    namespaced: true,
    state: {
        name: '',
        activities: {},
        end_event: {},
        flows: {},
        gateways: {},
        line: [],
        location: [],
        outputs: [],
        start_event: {},
        template_id: '',
        constants: {},
        projectBaseInfo: {},
        notify_receivers: {
            receiver_group: [],
            more_receiver: ''
        },
        notify_type: { success: [], fail: [] },
        time_out: '',
        category: '',
        description: '',
        executor_proxy: '',
        template_labels: '',
        subprocess_info: {
            details: [],
            subproc_has_update: false
        },
        internalVariable: [],
        default_flow_type: 'common'
    },
    mutations: {
        setTemplateName (state, name) {
            state.name = name
        },
        setReceiversGroup (state, data) {
            state.notify_receivers.receiver_group = data
        },
        setNotifyType (state, data) {
            state.notify_type = data
        },
        setOvertime (state, data) {
            state.time_out = data
        },
        setCategory (state, data) {
            state.category = data
        },
        setTplConfig (state, data) {
            const { name, category, notify_type, receiver_group, description, executor_proxy, template_labels, default_flow_type } = data
            state.name = name
            state.category = category
            state.notify_type = notify_type
            state.notify_receivers.receiver_group = receiver_group
            state.description = description
            state.executor_proxy = executor_proxy
            state.template_labels = template_labels
            state.default_flow_type = default_flow_type
        },
        setSubprocessUpdated (state, subflow) {
            if (state.subprocess_info.loadTemplateData) {
                state.subprocess_info.loadTemplateData.some((item) => {
                    if (subflow.subprocess_node_id === item.subprocess_node_id) {
                        item.expired = subflow.expired
                        if (subflow.version) {
                            item.version = subflow.version
                        }
                        return true
                    }
                    return false
                })
            }
        },
        setPipelineTree (state, data) {
            const pipelineTreeOrder = [
                'activities', 'constants', 'end_event', 'flows', 'gateways',
                'line', 'location', 'outputs', 'start_event'
            ]
            pipelineTreeOrder.forEach((key) => {
                let val = data[key]

                if (key === 'constants') {
                    // 全局变量 index 修正，3.5版本之前变量 index 存在不连续的情况，导致新增变量时 index 不正确
                    Object.keys(val).map(varKey => val[varKey])
                        .sort((a, b) => a.index - b.index)
                        .forEach((item, index) => {
                            item.index = index
                        })
                } else {
                    // 节点、连线不和规则 id 替换
                    // 3.1版本之前节点和连线的 id 可能存在以数字开头的情况，导致使用 docuement.getElementById 等查找DOM节点失败
                    val = nodeFilter.convertInvalidIdData(key, val)
                    if (key === 'activities') { // 兼容脏数据 can_retry、isSkipped 字段不存在问题
                        Object.keys(val).forEach((nodeId) => {
                            const item = val[nodeId]
                            const has = Object.prototype.hasOwnProperty
                            if (!has.call(item, 'can_retry') && !has.call(item, 'retryable')) {
                                item.can_retry = true
                            }
                            if (!has.call(item, 'isSkipped') && !has.call(item, 'skippable')) {
                                item.isSkipped = true
                            }
                        })
                    }
                    if (key === 'location') {
                        val = val.map((item) => {
                            if (item.type === 'tasknode' || item.type === 'subflow') {
                                const node = state.activities[item.id]
                                const loc = Object.assign({}, item, {
                                    name: node.name,
                                    stage_name: node.stage_name,
                                    optional: node.optional,
                                    error_ignorable: node.error_ignorable,
                                    retryable: node.can_retry || node.retryable,
                                    skippable: node.isSkipped || node.skippable,
                                    auto_retry: node.auto_retry || { enable: false, interval: 0, times: 1 },
                                    timeout_config: node.timeout_config || {
                                        enable: false,
                                        seconds: 10,
                                        action: 'forced_fail'
                                    }
                                })
                                return loc
                            }
                            return item
                        })
                    }
                }

                state[key] = val
            })
        },
        // 更新模板各相关字段数据
        setTemplateData (state, data) {
            const {
                name, template_id, pipeline_tree, notify_receivers, template_labels, notify_type, description,
                executor_proxy, time_out, category, subprocess_info, default_flow_type
            } = data

            const pipelineData = JSON.parse(pipeline_tree)
            const receiver = JSON.parse(notify_receivers)
            state.name = name
            state.template_id = template_id
            state.notify_receivers.receiver_group = receiver.receiver_group || []
            state.notify_type = typeof notify_type === 'string' ? { success: JSON.parse(notify_type), fail: [] } : notify_type
            state.description = description
            state.executor_proxy = executor_proxy
            state.template_labels = template_labels || []
            state.time_out = time_out
            state.category = category
            state.subprocess_info = subprocess_info
            state.default_flow_type = default_flow_type
            this.commit('template/setPipelineTree', pipelineData)
        },
        setProjectBaseInfo (state, data) {
            state.projectBaseInfo = data
        },
        // 初始化模板数据
        initTemplateData (state) {
            const location = generateInitLocation()
            const line = generateInitLine(location)
            const flow = generateInitFlow(line)
            const activities = generateInitActivities(location, line)
            const start_event = generateStartNode(location[0], line[0])
            const end_event = generateEndNode(location[2], line[1])
            state.name = ''
            state.activities = activities
            state.end_event = end_event
            state.flows = flow
            state.gateways = {}
            state.line = line
            state.location = location
            state.outputs = []
            state.start_event = start_event
            state.template_id = ''
            state.constants = {}
            state.category = 'Default'
            state.notify_type = { success: [], fail: [] }
            state.notify_receivers = {
                receiver_group: [],
                more_receiver: ''
            }
            state.description = ''
            state.executor_proxy = ''
            state.template_labels = []
            state.default_flow_type = 'common'
        },
        // 重置模板数据
        resetTemplateData (state) {
            state.name = ''
            state.activities = {}
            state.end_event = {}
            state.flows = {}
            state.gateways = {}
            state.line = []
            state.location = []
            state.outputs = []
            state.start_event = {}
            state.template_id = ''
            state.constants = {}
            state.category = 'Default'
            state.notify_type = { success: [], fail: [] }
            state.notify_receivers = {
                receiver_group: [],
                more_receiver: ''
            }
            state.description = ''
            state.executor_proxy = ''
            state.template_labels = []
            state.default_flow_type = 'common'
        },
        // 增加全局变量
        addVariable (state, variable) {
            Vue.set(state.constants, variable.key, variable)
        },
        // 编辑全局变量
        editVariable (state, payload) {
            const { key, variable } = payload
            Vue.delete(state.constants, key)
            Vue.set(state.constants, variable.key, variable)
        },
        // 删除全局变量
        deleteVariable (state, key) {
            const constant = state.constants[key]
            const { source_info } = constant

            // 遍历节点，去掉表单的勾选状态，并将变量值复制给对应表单
            Object.keys(source_info).forEach((id) => {
                if (state.activities[id]) {
                    source_info[id].forEach((item) => {
                        let data
                        if (state.activities[id].type === 'ServiceActivity') {
                            data = state.activities[id].component.data[item]
                        } else {
                            const variableKey = /^\$\{[\w]*\}$/.test(item) ? item : '${' + item + '}'
                            data = state.activities[id].constants[variableKey]
                        }
                        if (data) {
                            data.hook = false
                            data.value = constant.value
                        }
                    })
                }
            })
            // 删除输出变量的勾选状态
            if (state.outputs.includes(key)) {
                state.outputs.splice(state.outputs.indexOf(key), 1)
            }

            Object.keys(state.constants).forEach((key) => {
                const varItem = state.constants[key]
                if (varItem.index > constant.index) {
                    varItem.index = varItem.index - 1
                }
            })

            Vue.delete(state.constants, key)
        },
        // 配置全局变量 source_info 字段
        setVariableSourceInfo (state, payload) {
            const { type, id, key, tagCode } = payload
            const constant = state.constants[key]
            if (!constant) return
            const sourceInfo = constant.source_info
            if (type === 'add') {
                if (sourceInfo[id]) {
                    sourceInfo[id].push(tagCode)
                } else {
                    Vue.set(sourceInfo, id, [tagCode])
                }
            } else if (type === 'delete') {
                if (sourceInfo[id].length <= 1) {
                    Vue.delete(sourceInfo, id)
                } else {
                    let atomIndex
                    sourceInfo[id].some((item, index) => {
                        if (item === tagCode) {
                            atomIndex = index
                            return true
                        }
                        return false
                    })
                    sourceInfo[id].splice(atomIndex, 1)
                }
                if (!Object.keys(sourceInfo).length) {
                    this.commit('template/deleteVariable', key)
                }
            }
        },
        // 配置分支网关条件
        setBranchCondition (state, condition) {
            const { id, nodeId, name, value, loc, default_condition } = condition
            const conditions = state.gateways[nodeId].conditions
            if (default_condition) {
                state.gateways[nodeId]['default_condition'] = default_condition
                Vue.delete(conditions, id)
            } else if (conditions[id]) {
                conditions[id].name = name
                conditions[id].evaluate = value
            } else if (!conditions[id]) {
                const { tag } = state.gateways[nodeId].default_condition
                conditions[id] = {
                    tag,
                    name,
                    evaluate: value
                }
                Vue.delete(state.gateways[nodeId], 'default_condition')
            }
            if (loc !== undefined) {
                if (default_condition) {
                    state.gateways[nodeId]['default_condition'].loc = loc
                } else if (conditions[id]) {
                    conditions[id].loc = loc
                }
            }
        },
        // 节点增加、删除、编辑、复制,操作，数据更新
        setLocation (state, payload) {
            const { type, location } = payload
            let locationIndex
            const isLocationExist = state.location.some((item, index) => {
                if (item.id === location.id) {
                    locationIndex = index
                    return true
                }
                return false
            })
            if (['add', 'copy'].indexOf(type) > -1 && !isLocationExist) {
                const loc = tools.deepClone(location)
                delete loc.atomId // 添加节点后删除标准插件类型字段
                state.location.push(loc)
            } else {
                if (type === 'edit') {
                    state.location.splice(locationIndex, 1, location)
                } else if (type === 'delete') {
                    state.location.splice(locationIndex, 1)
                }
            }
        },
        // 节点拖动，位置更新
        setLocationXY (state, location) {
            const { id, x, y } = location
            state.location.some((item) => {
                if (item.id === id) {
                    item.x = x
                    item.y = y
                    return true
                }
                return false
            })
        },
        // 增加、删除节点连线操作，更新模板各相关字段数据
        setLine (state, payload) {
            const { type, line } = payload
            const isLineExist = state.line.some((item, index) => {
                if (
                    item.source.id === line.source.id
                    && item.target.id === line.target.id
                ) {
                    return true
                }
                return false
            })

            if (type === 'add' && !isLineExist) { // 添加连线(手动拖拽连接的情况)
                const id = 'line' + uuid()
                const newLine = Object.assign({}, line, { id })
                const sourceNode = newLine.source.id
                const targetNode = newLine.target.id

                Vue.set(state.flows, id, {
                    id,
                    is_default: false,
                    source: sourceNode,
                    target: targetNode
                })

                if (state.activities[sourceNode]) {
                    state.activities[sourceNode].outgoing = id
                }

                if (state.activities[targetNode]) {
                    state.activities[targetNode].incoming = updateIncoming(state.activities[targetNode].incoming, id, 'add')
                }

                if (state.start_event.id === sourceNode) {
                    state.start_event.outgoing = id
                }

                if (state.end_event.id === targetNode) {
                    state.end_event.incoming = updateIncoming(state.end_event.incoming, id, 'add')
                }

                if (state.gateways[sourceNode]) {
                    const gatewayNode = state.gateways[sourceNode]
                    if (Array.isArray(gatewayNode.outgoing)) {
                        const len = gatewayNode.outgoing.length
                        Vue.set(gatewayNode.outgoing, len, id)
                        if (gatewayNode.type === ATOM_TYPE_DICT['branchgateway'] || gatewayNode.type === ATOM_TYPE_DICT['conditionalparallelgateway']) {
                            const { conditions } = gatewayNode
                            let evaluate
                            let name
                            // copy 连线，需复制原来的分支条件信息
                            if (line.oldSouceId) {
                                const sourceNodeId = state.flows[line.oldSouceId].source
                                const sourceGateWayNode = state.gateways[sourceNodeId]
                                const sourceCondition = sourceGateWayNode.conditions[line.oldSouceId]

                                evaluate = sourceCondition.evaluate || sourceCondition.name
                                name = sourceCondition.name
                            } else if (line.condition) { // 自动重连，保留原连线分支条件
                                evaluate = line.condition.evaluate
                                name = line.condition.name
                            } else {
                                evaluate = Object.keys(conditions).length ? '1 == 0' : '1 == 1'
                                name = evaluate
                            }

                            const conditionItem = {
                                evaluate,
                                name,
                                tag: `branch_${sourceNode}_${targetNode}`
                            }
                            Vue.set(conditions, id, conditionItem)
                        }
                    } else {
                        gatewayNode.outgoing = id
                    }
                }
                if (state.gateways[targetNode]) {
                    const gatewayNode = state.gateways[targetNode]
                    gatewayNode.incoming = updateIncoming(gatewayNode.incoming, id, 'add')
                }
                state.line.push(newLine)
            } else if (type === 'delete') { // sync activities、flows、gateways、start_event、end_event
                let deletedLine
                Object.keys(state.flows).forEach((item) => {
                    const flow = state.flows[item]
                    if (flow.source === line.source.id && flow.target === line.target.id) {
                        deletedLine = Object.assign({}, flow)
                    }
                })
                if (!deletedLine) {
                    return
                }
                const sourceNode = state.flows[deletedLine.id].source
                const targetNode = state.flows[deletedLine.id].target

                if (state.activities[sourceNode]) {
                    state.activities[sourceNode].outgoing = ''
                }

                if (state.activities[targetNode]) {
                    state.activities[targetNode].incoming = updateIncoming(state.activities[targetNode].incoming, deletedLine.id, 'delete')
                }

                if (state.start_event.id === sourceNode) {
                    state.start_event.outgoing = ''
                }

                if (state.end_event.id === targetNode) {
                    state.end_event.incoming = updateIncoming(state.end_event.incoming, deletedLine.id, 'delete')
                }

                state.line = state.line.filter(ln => ln.id !== deletedLine.id)
                if (state.gateways[sourceNode]) {
                    const gatewayNode = state.gateways[sourceNode]
                    if (Array.isArray(gatewayNode.outgoing)) {
                        gatewayNode.outgoing = gatewayNode.outgoing.filter(item => item !== deletedLine.id)
                        if (gatewayNode.type === ATOM_TYPE_DICT['branchgateway'] || gatewayNode.type === ATOM_TYPE_DICT['conditionalparallelgateway']) {
                            const { conditions } = gatewayNode
                            conditions[deletedLine.id] && Vue.delete(conditions, deletedLine.id)
                        }
                    } else {
                        gatewayNode.outgoing = ''
                    }
                    // 删除默认网关分支连线时需要清除网关处理的default_condition
                    const tag = `branch_${sourceNode}_${targetNode}`
                    if (gatewayNode.default_condition && gatewayNode.default_condition.tag === tag) {
                        Vue.delete(gatewayNode, 'default_condition')
                    }
                }
                if (state.gateways[targetNode]) {
                    const gatewayNode = state.gateways[targetNode]
                    gatewayNode.incoming = updateIncoming(gatewayNode.incoming, deletedLine.id, 'delete')
                }
                Vue.delete(state.flows, deletedLine.id)
            }
        },
        // 任务节点增加、删除、编辑,复制操作，更新模板各相关字段数据
        setActivities (state, payload) {
            const { type, location } = payload
            if (type === 'add') {
                if (!state.activities[location.id]) {
                    let activity = {}
                    if (location.type === 'tasknode') {
                        activity = {
                            component: {
                                code: location.atomId,
                                data: location.data,
                                version: location.version
                            },
                            error_ignorable: false,
                            id: location.id,
                            incoming: [],
                            loop: null,
                            name: location.name || '',
                            optional: true,
                            outgoing: '',
                            stage_name: '',
                            type: 'ServiceActivity',
                            retryable: true,
                            skippable: true,
                            auto_retry: { enable: false, interval: 0, times: 1 },
                            timeout_config: {
                                enable: false,
                                seconds: 10,
                                action: 'forced_fail'
                            }
                        }
                    } else if (location.type === 'subflow') {
                        activity = {
                            constants: {},
                            hooked_constants: [],
                            id: location.id,
                            incoming: [],
                            loop: null,
                            name: location.name || '',
                            optional: true,
                            outgoing: '',
                            stage_name: '',
                            template_id: location.atomId,
                            version: location.atomVersion,
                            type: 'SubProcess',
                            always_use_latest: false,
                            scheme_id_list: [],
                            template_source: location.tplSource || 'business'
                        }
                    }
                    Vue.set(state.activities, location.id, activity)
                }
            } else if (type === 'edit') {
                Vue.set(state.activities, location.id, location)
                state.location.forEach((item) => {
                    if (item.id === location.id) {
                        Vue.set(item, 'name', location.name)
                        Vue.set(item, 'stage_name', location.stage_name)
                    }
                })
            } else if (type === 'delete') {
                Vue.delete(state.activities, location.id)
                Object.keys(state.constants).forEach((cKey) => {
                    const constant = state.constants[cKey]
                    const sourceInfo = constant.source_info
                    if (sourceInfo && sourceInfo[location.id]) {
                        if (Object.keys(sourceInfo).length > 1) {
                            Vue.delete(sourceInfo, location.id)
                        } else {
                            this.commit('template/deleteVariable', cKey)
                        }
                    }
                })
            } else if (type === 'copy') { // 复制节点
                const { oldSouceId } = location
                const newActivitie = tools.deepClone(state.activities[oldSouceId])
                if (!state.activities[location.id]) {
                    if (location.type === 'tasknode' || location.type === 'subflow') {
                        newActivitie.id = location.id
                        newActivitie.incoming = ''
                        newActivitie.loop = null
                        newActivitie.outgoing = ''
                        state.activities[location.id] = newActivitie
                    }
                }
                // 勾选变量处理
                Object.keys(state.constants).forEach((key) => {
                    const item = state.constants[key]
                    const { source_info } = item
                    const info = source_info[oldSouceId]
                    if (info) {
                        const { source_type } = state.constants[key]
                        if (source_type === 'component_inputs') { // 复用输入变量
                            Vue.set(source_info, location.id, info)
                        } else if (source_type === 'component_outputs') { // 新建输出变量
                            const constantsLen = Object.keys(state.constants).length
                            const varId = '${' + info[0] + '_' + random4() + '}'
                            const varValue = tools.deepClone(item)
                            const changeObj = {
                                source_info: { [location.id]: info },
                                key: varId,
                                index: constantsLen
                            }
                            Vue.set(state.constants, varId, Object.assign(varValue, changeObj))
                        }
                    }
                })
            }
        },
        // 网关节点增加、删除操作，更新模板各相关字段数据
        setGateways (state, payload) {
            const { type, location } = payload
            if (['add', 'copy'].indexOf(type) > -1) {
                if (!state.gateways[location.id]) {
                    state.gateways[location.id] = {
                        id: location.id,
                        incoming: [],
                        name: location.name || '',
                        outgoing: location.type === 'convergegateway' ? '' : [],
                        type: ATOM_TYPE_DICT[location.type]
                    }
                    if (location.type === 'branchgateway' || location.type === 'conditionalparallelgateway') {
                        state.gateways[location.id].conditions = {}
                    }
                }
            } else if (type === 'delete') {
                Vue.delete(state.gateways, location.id)
            }
        },
        // 开始节点增加、删除操作，更新模板各相关字段数据
        setStartpoint (state, payload) {
            const { type, location } = payload
            if (type === 'add') {
                if (!state.start_event.id) {
                    state.start_event = {
                        id: location.id,
                        incoming: '',
                        name: location.name || '',
                        outgoing: '',
                        type: 'EmptyStartEvent'
                    }
                }
            } else if (type === 'delete') {
                Vue.set(state, 'start_event', {})
            }
        },
        // 终止节点增加、删除操作，更新模板各相关字段数据
        setEndpoint (state, payload) {
            const { type, location } = payload
            if (type === 'add') {
                if (!state.end_event.id) {
                    state.end_event = {
                        id: location.id,
                        incoming: '',
                        name: location.name || '',
                        outgoing: '',
                        type: 'EmptyEndEvent'
                    }
                }
            } else if (type === 'delete') {
                Vue.set(state, 'end_event', {})
            }
        },
        // 更新全局变量
        setConstants (state, data) {
            state.constants = tools.deepClone(data)
        },
        // 全局变量勾选是否为输出
        setOutputs (state, payload) {
            const { changeType, key, newKey } = payload
            if (changeType === 'add') {
                if (state.outputs.includes(key)) {
                    return
                }
                state.outputs.push(key)
            } else if (changeType === 'delete') {
                state.outputs = state.outputs.filter(item => item !== key)
            } else {
                const index = state.outputs.findIndex(item => item === key)
                state.outputs.splice(index, 1, newKey)
            }
        },
        // 修改state中的模板数据
        replaceTemplate (state, template) {
            if (template !== undefined) {
                Object.keys(template).forEach((prop) => {
                    state[prop] = template[prop]
                })
            }
        },
        // 修改lines和locations
        replaceLineAndLocation (state, payload) {
            //  需要做一次深层拷贝
            const { lines, locations } = tools.deepClone(payload)
            state.line = lines
            state.location = locations
        },
        // 设置内置变量
        setInternalVariable (state, payload) {
            state.internalVariable = payload
        }
    },
    actions: {
        loadProjectBaseInfo () {
            return axios.get('core/api/get_basic_info/').then(response => response.data)
        },
        loadTemplateData ({ commit }, data) {
            const { templateId, common, checkPermission = false } = data
            let prefixUrl = ''
            if (common) {
                prefixUrl = 'api/v3/common_template/'
            } else {
                prefixUrl = 'api/v3/template/'
            }
            return axios({
                method: 'get',
                url: `${prefixUrl}${templateId}/`,
                headers: {
                    'Tpl-Node-Permission-Check': checkPermission
                }
            }).then(response => response.data.data)
        },
        loadCustomVarCollection () {
            return axios.get('api/v3/variable/').then(response => {
                return response.data.data
            })
        },
        /**
         * 保存模板数据
         * @param {Object} data 模板完整数据
         */
        saveTemplateData ({ state }, { templateId, projectId, common }) {
            const { activities, constants, end_event, flows, gateways, line,
                location, outputs, start_event, notify_receivers, notify_type,
                time_out, category, description, executor_proxy, template_labels, default_flow_type
            } = state
            // 剔除 location 的冗余字段
            const pureLocation = location.map(item => ({
                id: item.id,
                type: item.type,
                name: item.name,
                stage_name: item.stage_name,
                x: item.x,
                y: item.y,
                group: item.group,
                icon: item.icon
            }))
            // 剔除 gateways condition中默认分支配置
            const pureGateways = Object.values(gateways).reduce((acc, cur) => {
                if (cur.default_condition) {
                    const lineId = cur.default_condition.flow_id
                    if (cur.conditions[lineId]) {
                        Vue.delete(cur.conditions, lineId)
                    }
                }
                acc[cur.id] = cur
                return acc
            }, {})
            // 完整的画布数据
            const fullCanvasData = {
                activities,
                constants,
                end_event,
                flows,
                gateways: pureGateways,
                line,
                location: pureLocation,
                outputs,
                start_event
            }
            const validateResult = validatePipeline.isPipelineDataValid(fullCanvasData)

            if (!validateResult.result) {
                return new Promise((resolve, reject) => {
                    const info = {
                        message: `${i18n.t('流程数据格式错误，请检查节点、连线或者全局变量')} error_message: ${validateResult.message}`
                    }
                    reject(info)
                })
            }
            const { name } = state
            const pipelineTree = JSON.stringify(fullCanvasData)
            const notifyReceivers = JSON.stringify(notify_receivers)
            const timeout = time_out
            const headers = {}
            const project = projectId || undefined
            let url = ''
            if (common) {
                url = 'api/v3/common_template/'
            } else {
                url = 'api/v3/template/'
            }

            if (templateId !== undefined) {
                url = `${url}${templateId}/`
                headers['X-HTTP-Method-Override'] = 'PATCH'
            }

            // 新增用post, 编辑用put
            return axios[templateId === undefined ? 'post' : 'put'](url, {
                name,
                project,
                category,
                timeout,
                description,
                executor_proxy,
                template_labels,
                default_flow_type,
                notify_type,
                pipeline_tree: pipelineTree,
                notify_receivers: notifyReceivers
            }, {
                headers
            }).then(response => response.data)
        },
        // 自动排版
        getLayoutedPipeline ({ commit }, data) {
            return axios.post('template/api/draw_pipeline/', data).then(response => response.data)
        },
        // 获取内置变量
        loadInternalVariable () {
            return axios.get('taskflow/api/context/').then(response => response.data)
        },
        // 获取节点标签列表
        getLabels ({ commit }, data = {}) {
            return axios.get('api/v3/label/', { params: data }).then(response => {
                if (!('limit' in data)) { // 不传limit代表拉取全量列表
                    return { results: response.data.data }
                } else {
                    return response.data.data
                }
            })
        },
        // 获取变量预览值
        getConstantsPreviewResult ({ commit }, data) {
            return axios.post('template/api/get_constant_preview_result/', data).then(response => response.data)
        },
        // 获取全局变量被引用数据
        getVariableCite ({ commit }, data) {
            return axios.post('template/api/analysis_constants_ref/', data).then(response => response.data)
        },
        checkKey ({ commit }, data) {
            return axios.get('core/api/check_variable_key/', { params: data }).then(response => response.data)
        },
        getBatchForms ({ commit }, data) {
            const { projectId, tpls } = data
            return axios.post(`template/api/batch_form_with_schemes/`, {
                project_id: projectId,
                template_list: tpls
            }).then(response => response.data)
        },
        // 获取所有mako模板操作
        getMakoOperations ({ commit }) {
            return axios.get('mako_operations/').then(response => response.data)
        },
        getVariableFieldExplain ({ commit }) {
            return axios.get('template/api/variable_field_explain/').then(response => response.data)
        },
        // 获取流程是否开启独立子流程
        getProcessOpenChdProcess ({ commit }, data) {
            const { id } = data
            return axios.get(`/api/v3/template/${id}/enable_independent_subprocess/`, { params: data }).then(response => response.data)
        },
        // 批量获取任务是否有独立子任务
        getTaskHasSubTasks ({ commit }, data) {
            return axios.get(`/api/v3/taskflow/root_task_info/`, { params: data }).then(response => response.data)
        },
        // 获取某个任务的子任务列表
        getTaskHasSubTaskList ({ commit }, data) {
            return axios.get(`/api/v3/taskflow/list_children_taskflow/`, { params: data }).then(response => response.data)
        }
    },
    getters: {
        // 获取所有模板数据
        getLocalTemplateData (state) {
            return tools.deepClone(state)
        },
        getPipelineTree (state) {
            const {
                activities, constants, end_event, flows, gateways,
                line, location, outputs, start_event
            } = state
            // 剔除 location 的冗余字段
            const pureLocation = location.map(item => ({
                id: item.id,
                type: item.type,
                name: item.name,
                stage_name: item.stage_name,
                status: item.status,
                x: item.x,
                y: item.y
            }))
            return {
                activities,
                constants,
                end_event,
                flows,
                gateways,
                line,
                location: pureLocation,
                outputs,
                start_event
            }
        }
    }
}

export default template
