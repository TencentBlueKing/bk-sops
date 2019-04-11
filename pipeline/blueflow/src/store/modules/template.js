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
import nodeFilter from '@/utils/nodeFilter.js'
import { uuid } from '@/utils/uuid.js'
import tools from '@/utils/tools.js'
const ATOM_TYPE_DICT = {
    startpoint: 'EmptyStartEvent',
    endpoint: 'EmptyEndEvent',
    tasknode: 'ServiceActivity',
    subflow: 'SubProcess',
    parallelgateway: 'ParallelGateway',
    branchgateway: 'ExclusiveGateway',
    convergegateway: 'ConvergeGateway'
}
// 默认流程模板，默认节点
function generateInitLocation () {
    return [
        {
            id: 'node' + uuid(),
            x: 80,
            y: 150,
            type: 'startpoint'
        },
        {
            id: 'node' + uuid(),
            x: 300,
            y: 135,
            name: '',
            stage_name: gettext('步骤1'),
            type: 'tasknode'
        },
        {
            id: 'node' + uuid(),
            x: 600,
            y: 150,
            type: 'endpoint'
        }
    ]

}
// 默认流程模板，activities 字段
function generateInitActivities (location, line) {
    return {
        [location[1].id]: {
            component: {
                code: undefined,
                data: undefined
            },
            error_ignorable: false,
            id: location[1].id,
            incoming: line[0].id,
            loop: null,
            name: '',
            optional: false,
            outgoing: line[1].id,
            stage_name: gettext('步骤1'),
            type: 'ServiceActivity',
            can_retry: true,
            isSkipped: true
        }
    }
}
// 默认流程模板，开始节点
function generateStartNode (location, line) {
    return {
        id: location.id,
        incoming: '',
        name: '',
        outgoing: line.id,
        type: 'EmptyStartEvent'
    }
}
// 默认流程模板，结束节点
function generateEndNode (location, line) {
    return {
        id: location.id,
        incoming: line.id,
        name: '',
        outgoing: '',
        type: 'EmptyEndEvent'
    }
}
// 默认流程模板，初始化 line 字段
function generateInitLine (location) {
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
function generateInitFlow (line) {
    const flow = {}
    line.forEach(item => {
        flow[item.id] = {
            id: item.id,
            is_default: false,
            source: item.source.id,
            target: item.target.id
        }
    })
    return flow
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
        businessBaseInfo: {},
        notify_receivers: {
            receiver_group: [],
            more_receiver: ''
        },
        notify_type: [],
        time_out: '',
        category: '',
        subprocess_info: {}
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
        setSubprocessUpdated (state, subflow) {
            state.subprocess_info.details.some(item => {
                if (
                    subflow.template_id === item.template_id &&
                    subflow.subprocess_node_id === item.subprocess_node_id
                ) {
                    item.expired = false
                    subflow.version && (item.version = subflow.version)
                    return true
                }
            })
        },
        // 更新模板各相关字段数据
        setTemplateData (state, data) {
            const { name, template_id, pipeline_tree, notify_receivers,
                notify_type, time_out, category, subprocess_info
            } = data
            const pipelineTreeOrder = [
                'activities', 'constants', 'end_event', 'flows', 'gateways',
                'line', 'location', 'outputs', 'start_event'
            ]
            const pipelineData = JSON.parse(pipeline_tree)
            const receiver = JSON.parse(notify_receivers)
            state.name = name
            state.template_id = template_id
            state.notify_receivers.receiver_group = receiver.receiver_group || []
            state.notify_type = notify_type ? JSON.parse(notify_type) : []
            state.time_out = time_out
            state.category = category
            state.subprocess_info = subprocess_info

            pipelineTreeOrder.forEach(key => {
                let val = pipelineData[key]
                if (key !== 'constants'){
                    val = nodeFilter.convertInvalidIdData(key, val) // convert old invalid data =_=!
                }
                if (key === 'location') {
                    val = val.map(item => {
                        if (item.type === 'tasknode' || item.type === 'subflow') {
                            const node = state.activities[item.id]
                            const loc = Object.assign({}, item, {
                                name: node.name,
                                stage_name: node.stage_name,
                                optional: node.optional,
                                error_ignorable: node.error_ignorable,
                                can_retry: node.can_retry,
                                isSkipped: node.isSkipped
                            })
                            return loc
                        }
                        return item
                    })
                }
                state[key] = val
            })

        },
        setBusinessBaseInfo (state, data) {
            state.businessBaseInfo = data
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
            state.category = ''
        },
        // 重置模板数据
        resetTemplateData (state) {
            state.name = ''
            state.activities  = {}
            state.end_event = {}
            state.flows = {}
            state.gateways = {}
            state.line = []
            state.location = []
            state.outputs = []
            state.start_event = {}
            state.template_id = ''
            state.constants = {}
            state.notify_type = []
            state.notify_receivers = {
                receiver_group: [],
                more_receiver: ''
            }
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

            for (let id in source_info) {
                if (state.activities[id]) {
                    source_info[id].forEach(item => {
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
            }
            const vIndex = state.outputs.indexOf(key)
            vIndex > -1 && state.outputs.splice(vIndex, 1)
            Vue.delete(state.constants, key)
        },
        // 配置全局变量 source_info 字段
        setVariableSourceInfo (state, payload) {
            const {type, id, key, tagCode} = payload
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
                    sourceInfo[id].some((item, index)=> {
                        if (item === tagCode) {
                            atomIndex = index
                            return true
                        }
                    })
                    sourceInfo[id].splice(atomIndex, 1)
                }
            }
        },
        // 配置分支网关条件
        setBranchCondition (state, condition) {
            const {id, nodeId, name} = condition
            state.gateways[nodeId]['conditions'][id].evaluate = name
        },
        // 节点增加、删除、编辑操作，数据更新
        setLocation (state, payload) {
            const { type, location } = payload
            let locationIndex
            const isLocationExist = state.location.some((item, index) => {
                if (item.id === location.id) {
                    locationIndex = index
                    return true
                }
            })
            if (type === 'add' && !isLocationExist) {
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
            const {id, x, y} = location
            state.location.some(item => {
                if (item.id === id) {
                    item.x = x
                    item.y = y
                    return true
                }
            })
        },
        // 增加、删除节点连线操作，更新模板各相关字段数据
        setLine (state, payload) {
            const { type, line } = payload
            let lineIndex
            const isLineExist = state.line.some((item, index) => {
                if (
                    item.source.id === line.source.id &&
                    item.target.id === line.target.id
                ) {
                    lineIndex = index
                    return true
                }
            })
            if (type === 'add' && !isLineExist) {
                const id = 'line' + uuid()
                const newLine = Object.assign({}, line, { id })
                const sourceNode = newLine.source.id
                const targetNode = newLine.target.id
                state.activities[sourceNode] && (state.activities[sourceNode].outgoing = id)
                state.activities[targetNode] && (state.activities[targetNode].incoming = id)
                state.flows[id] = {
                    id,
                    is_default: false,
                    source: sourceNode,
                    target: targetNode
                }
                state.start_event.id === sourceNode && (state.start_event.outgoing = id)
                state.end_event.id === targetNode && (state.end_event.incoming = id)
                if (state.gateways[sourceNode]) {
                    const gatewayNode = state.gateways[sourceNode]
                    if (Array.isArray(gatewayNode.outgoing)) {
                        gatewayNode.outgoing.push(id)
                        if (gatewayNode.type === ATOM_TYPE_DICT['branchgateway']) {
                            const conditions = gatewayNode.conditions
                            const conditionItem = {
                                evaluate: Object.keys(conditions).length ? '1 == 0' : '1 == 1',
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
                    if (Array.isArray(gatewayNode.incoming)) {
                        gatewayNode.incoming.push(id)
                    } else {
                        gatewayNode.incoming = id
                    }
                }
                state.line.push(newLine)
            } else if (type === 'delete') { // async activities、flows、gateways、start_event、end_event
                let deletedLine
                for (let item in state.flows) {
                    const flow =  state.flows[item]
                    if (flow.source === line.source.id && flow.target === line.target.id) {
                        deletedLine = Object.assign({}, flow)
                    }
                }
                const sourceNode = state.flows[deletedLine.id].source
                const targetNode = state.flows[deletedLine.id].target
                state.activities[sourceNode] && (state.activities[sourceNode].outgoing = '')
                state.activities[targetNode] && (state.activities[targetNode].incoming = '')
                state.start_event.id === sourceNode && (state.start_event.outgoing = '')
                state.end_event.id === sourceNode && (state.end_event.incoming = '')
                state.line = state.line.filter(ln => ln.id !== deletedLine.id)
                if (state.gateways[sourceNode]) {
                    const gatewayNode = state.gateways[sourceNode]
                    if (Array.isArray(gatewayNode.outgoing)) {
                        gatewayNode.outgoing = gatewayNode.outgoing.filter(item => { return item !== deletedLine.id})
                        if (gatewayNode.type === ATOM_TYPE_DICT['branchgateway']) {
                            const conditions = gatewayNode.conditions
                            conditions[deletedLine.id] && Vue.delete(conditions, deletedLine.id)
                        }
                    } else {
                        gatewayNode.outgoing = ''
                    }
                }
                if (state.gateways[targetNode]) {
                    const gatewayNode = state.gateways[targetNode]
                    if (Array.isArray(gatewayNode.incoming)) {
                        gatewayNode.incoming = gatewayNode.incoming.filter(item => { return item !== deletedLine.id})
                    } else {
                        gatewayNode.incoming = ''
                    }
                }
                Vue.delete(state.flows, deletedLine.id)
            }
        },
        // 任务节点增加、删除、编辑操作，更新模板各相关字段数据
        setActivities (state, payload) {
            const { type, location } = payload
            if (type === 'add') {
                if (!state.activities[location.id]) {
                    if (location.type === 'tasknode') {
                        state.activities[location.id] = {
                            component: {
                                code: location.atomId,
                                data: location.data
                            },
                            error_ignorable: false,
                            id: location.id,
                            incoming: "",
                            loop: null,
                            name: location.name,
                            optional: false,
                            outgoing: "",
                            stage_name: gettext('步骤1'),
                            type: "ServiceActivity",
                            can_retry: true,
                            isSkipped: true
                        }
                    } else if (location.type === 'subflow') {
                        state.activities[location.id] = {
                            constants: {},
                            hooked_constants: [],
                            id: location.id,
                            incoming: "",
                            loop: null,
                            name: location.name,
                            optional: false,
                            outgoing: "",
                            stage_name: gettext('步骤1'),
                            template_id: location.atomId,
                            version: location.atomVersion,
                            type: "SubProcess"
                        }
                    }
                }
            } else if (type === 'edit') {
                state.activities[location.id] = location
                state.location.some(item => {
                    if (item.id === location.id) {
                        Vue.set(item, 'name', location.name)
                        Vue.set(item, 'stage_name', location.stage_name)
                    }
                })
            } else if (type === 'delete') {
                const { incoming, outgoing } = state.activities[location.id]
                const deletedlines = [incoming, outgoing]
                deletedlines.forEach(line => {
                    const flow = state.flows[line]
                    if (flow) {
                        const targetNode = flow.target
                        const sourceNode = flow.source
                        state.activities[targetNode] && (state.activities[targetNode].incoming = '')
                        state.activities[sourceNode] && (state.activities[sourceNode].outgoing = '')
                        state.start_event.id === sourceNode && (state.start_event.outgoing = '')
                        state.end_event.id === sourceNode && (state.end_event.incoming = '')
                        state.line = state.line.filter(item => {
                            return item.id !== line
                        })
                        if (state.gateways[sourceNode]) {
                            const gatewayNode = state.gateways[sourceNode]
                            if (Array.isArray(gatewayNode.outgoing)) {
                                gatewayNode.outgoing = gatewayNode.outgoing.filter(item => { return item !== line})
                                if (gatewayNode.type === ATOM_TYPE_DICT['branchgateway']) {
                                    const conditions = gatewayNode.conditions
                                    conditions[line] && Vue.delete(conditions, line)
                                }
                            } else {
                                gatewayNode.outgoing = ''
                            }
                        }
                        if (state.gateways[targetNode]) {
                            const gatewayNode = state.gateways[targetNode]
                            if (Array.isArray(gatewayNode.incoming)) {
                                gatewayNode.incoming = gatewayNode.incoming.filter(item => { return item !== line})
                            } else {
                                gatewayNode.incoming = ''
                            }
                        }
                        Vue.delete(state.flows, line)
                    }
                })
                for (let cKey in state.constants) {
                    const constant = state.constants[cKey]
                    const sourceInfo = constant.source_info

                    if (sourceInfo && sourceInfo[location.id]) {
                        if (Object.keys(sourceInfo).length > 1) {
                            Vue.delete(sourceInfo, location.id)
                        } else {
                            Vue.delete(state.constants, constant.key)
                        }
                    }
                }
                Vue.delete(state.activities, location.id)
            }
        },
        // 网关节点增加、删除操作，更新模板各相关字段数据
        setGateways (state, payload) {
            const { type, location } = payload
            if (type === 'add') {
                if (!state.gateways[location.id]) {
                    state.gateways[location.id] = {
                        id: location.id,
                        incoming: location.type === 'convergegateway' ? [] : '',
                        name: location.name,
                        outgoing: location.type === 'convergegateway' ? '' : [],
                        type: ATOM_TYPE_DICT[location.type]
                    }
                    if (location.type === 'branchgateway') {
                        state.gateways[location.id].conditions = {}
                    }
                }
            } else if (type === 'delete') {
                const { incoming, outgoing } = state.gateways[location.id]
                const deletedlines = Array.isArray(incoming) ? incoming.concat(outgoing) : outgoing.concat(incoming)
                deletedlines.forEach(line => {
                    const flow = state.flows[line]
                    if (flow) {
                        const targetNode = flow.target
                        const sourceNode = flow.source
                        const targetGateway = state.gateways[targetNode]
                        const sourceGateway = state.gateways[sourceNode]
                        state.activities[targetNode] && (state.activities[targetNode].incoming = '')
                        state.activities[sourceNode] && (state.activities[sourceNode].outgoing = '')
                        state.start_event.id === sourceNode && (state.start_event.outgoing = '')
                        state.end_event.id === sourceNode && (state.end_event.incoming = '')
                        if (targetGateway && targetNode !== location.id) {
                            if (typeof targetGateway.incoming === 'string') {
                                targetGateway.incoming = ''
                            } else {
                                targetGateway.incoming = targetGateway.incoming.filter(item => {
                                    return item !== line
                                })
                            }

                        }
                        if (sourceGateway && sourceNode !== location.id) {
                            if (typeof sourceGateway.outgoing === 'string') {
                                sourceGateway.outgoing = ''
                            } else {
                                sourceGateway.outgoing = sourceGateway.outgoing.filter(item => {
                                    return item !== line
                                })
                            }
                        }
                        Vue.delete(state.flows, line)
                    }
                    state.line = state.line.filter(item => {
                        return item.id !== line
                    })
                })
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
                        incoming: "",
                        name: location.name,
                        outgoing: "",
                        type: "EmptyStartEvent"
                    }
                }
            } else if (type === 'delete') {
                let targetNode
                let lineId
                for (let item in state.flows){
                    if (state.flows[item].source === location.id) {
                        targetNode = state.flows[item].target
                        lineId = state.flows[item].id
                    }
                }
                state.activities[targetNode] && (state.activities[targetNode].incoming = '')
                const gatewayNode = state.gateways[targetNode]
                if (gatewayNode) {
                    if (typeof gatewayNode.incoming === 'string') {
                        gatewayNode.incoming = ''
                    } else {
                        gatewayNode.incoming = gatewayNode.incoming.filter(item => item !== lineId)
                    }
                }
                state.line = state.line.filter(item => {
                    return item.id !== lineId
                })
                Vue.delete(state.flows, lineId)
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
                        incoming: "",
                        name: location.name,
                        outgoing: "",
                        type: "EmptyEndEvent"
                    }
                }
            } else if (type === 'delete') {
                let sourceNode
                let lineId
                for (let item in state.flows){
                    if (state.flows[item].target === location.id) {
                        sourceNode = state.flows[item].source
                        lineId = state.flows[item].id
                    }
                }
                state.activities[sourceNode] && (state.activities[sourceNode].outgoing = '')
                const gatewayNode = state.gateways[sourceNode]
                if (gatewayNode) {
                    if (typeof gatewayNode.outgoing === 'string') {
                        gatewayNode.outgoing = ''
                    } else {
                        gatewayNode.outgoing = gatewayNode.outgoing.filter(item => item !== lineId)
                        if (gatewayNode.type === ATOM_TYPE_DICT['branchgateway']) {
                            const conditions = gatewayNode.conditions
                            conditions[lineId] && Vue.delete(conditions, lineId)
                        }
                    }
                }
                state.line = state.line.filter(item => {
                    return item.id !== lineId
                })
                Vue.delete(state.flows, lineId)
                Vue.set(state, 'end_event', {})
            }
        },
        // 全局变量勾选是否为输出
        setOutputs (state, payload) {
            const { changeType, key } = payload
            if (changeType === 'add') {
                state.outputs.push(key)
            } else {
                state.outputs = state.outputs.filter(item => {
                    return item !== key
                })
            }
        },
        // 修改state中的模板数据
        replaceTemplate (state, template) {
            if (template !== undefined) {
                for (let prop in template) {
                    state[prop] = template[prop]
                }
            }
        },
        // 修改lines和locations
        replaceLineAndLocation (state, payload) {
            //  需要做一次深层拷贝
            const {lines, locations} = tools.deepClone(payload)
            state.line = lines
            state.location = locations
        }
    },
    actions: {
        loadBusinessBaseInfo () {
            return api.getBusinessBaseInfo().then(response => response.data)
        },
        loadTemplateData ({commit}, data) {
            return api.getTemplateData(data).then(response => response.data)
        },
        // 保存模板数据
        saveTemplateData ({state}, {templateId, ccId, common}) {
            const { activities, constants, end_event, flows, gateways, line,
                location, outputs, start_event, notify_receivers, notify_type, time_out, category
            } = state
            // 剔除 location 的冗余字段
            const pureLocation = location.map(item => {
                return {
                    id: item.id,
                    type: item.type,
                    name: item.name,
                    stage_name: item.stage_name,
                    status: item.status,
                    x: item.x,
                    y: item.y
                }
            })
            // 完整的画布数据
            const fullCanvasData = JSON.stringify({
                activities, constants, end_event, flows, gateways, line,
                location: pureLocation, outputs,  start_event
            })
            const data = {
                ccId,
                templateId,
                timeout: time_out,
                category,
                notifyReceivers: JSON.stringify(notify_receivers),
                notifyType: JSON.stringify(notify_type),
                name: state.name,
                pipelineTree: fullCanvasData,
                common
            }
            return api.saveTemplate(data).then(response => {
                return response.data
            })
        },
        // 收藏模板，批量操作
        templateCollectSelect ({commit}, list) {
            return api.templateCollectSelect(list).then(response => response.data)
        },
        // 删除收藏模板，单个删除
        templateCollectDelete ({commit}, id) {
            return api.templateCollectDelete(id).then(response => response.data)
        },
        queryTemplateData ({commit}, data) {
            return api.queryTemplate(data).then(response => response.data)
        },
        loadTemplateSummary ({commit}, data) {
            return api.loadTemplateSummary(data).then(response => response.data)
        },
        loadTemplateCollectList ({commit}) {
            return api.loadTemplateCollectList().then(response => response.data)
        }
    },
    getters: {
        // 获取所有模板数据
        getLocalTemplateData (state) {
            return tools.deepClone(state)
        }
    }
}

export default template
