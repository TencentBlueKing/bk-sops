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
import i18n from '@/config/i18n/index.js'
import { NODE_DICT } from '@/constants/index.js'
import validator from '@/constants/pipelineTreeSchema.js'

const NODE_RULE = {
    'startpoint': {
        min_in: 0,
        max_in: 0,
        min_out: 1,
        max_out: 1,
        allowed_out: ['tasknode', 'branchgateway', 'parallelgateway', 'conditionalparallelgateway', 'subflow'],
        unique: true
    },
    'endpoint': {
        min_in: 1,
        max_in: 1000,
        min_out: 0,
        max_out: 0,
        allowed_out: [],
        unique: true
    },
    'tasknode': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'conditionalparallelgateway', 'convergegateway', 'endpoint'],
        unique: false
    },
    'subflow': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'conditionalparallelgateway', 'convergegateway', 'endpoint'],
        unique: false
    },
    'branchgateway': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1000,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'conditionalparallelgateway', 'convergegateway', 'endpoint'],
        unique: false
    },
    'conditionalparallelgateway': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1000,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'conditionalparallelgateway', 'convergegateway', 'endpoint'],
        unique: false
    },
    'parallelgateway': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1000,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'conditionalparallelgateway'],
        unique: false
    },
    'convergegateway': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'conditionalparallelgateway', 'convergegateway', 'endpoint'],
        unique: false
    }
}

const validatePipeline = {
    /**
     * 判断连线是否合法
     * step:
     *  1.源节点(输出连线最大条数、输出节点是否允许连接)
     *  2.目标节点(输入连线的条数)
     * @param {Object} line
     * @param {Object} data
     */
    isLineValid (line, data) {
        const { lines, locations } = data
        const { source, target } = line
        const sourceId = source.id
        const targetId = target.id
        const sourceNode = locations.filter(item => item.id === sourceId)[0]
        const targetNode = locations.filter(item => item.id === targetId)[0]
        const sourceRule = NODE_RULE[sourceNode.type]
        const targetRule = NODE_RULE[targetNode.type]
        let sourceLinesLinked = 0
        let targetLinesLinked = 0
        let isLoop = false

        if (source.id === target.id) {
            const i18n_text = i18n.t('节点不可连接自身')
            const message = `${NODE_DICT[sourceNode.type]}${i18n_text}`
            return this.getMessage(false, message)
        }
        if (sourceRule.max_out === 0) {
            const i18n_text = i18n.t('只能添加输入连线')
            const message = `${NODE_DICT[sourceNode.type]}${i18n_text}`
            return this.getMessage(false, message)
        }

        if (targetRule.max_in === 0) {
            const i18n_text = i18n.t('只能添加输出连线')
            const message = `${NODE_DICT[targetNode.type]}${i18n_text}`
            return this.getMessage(false, message)
        }

        if (sourceRule.allowed_out.indexOf(targetNode.type) === -1) {
            const i18n_text = i18n.t('不能连接')
            const message = `${NODE_DICT[sourceNode.type]}${i18n_text}${NODE_DICT[targetNode.type]}`
            return this.getMessage(false, message)
        }
        const isSameLine = lines.some((item) => {
            if (item.source.id === sourceId) {
                sourceLinesLinked += 1
                if (item.target.id === targetId) {
                    return true
                }
            }
            if (item.target.id === targetId) {
                targetLinesLinked += 1
            }
            if (item.source.id === targetId && item.target.id === sourceId && sourceNode.type !== 'branchgateway') {
                isLoop = true
            }
        })

        if (isLoop) {
            const message = i18n.t('相同节点不能回连')
            return this.getMessage(false, message)
        }

        if (isSameLine) {
            const message = i18n.t('重复添加连线')
            return this.getMessage(false, message)
        }
        if (!isSameLine) {
            const i18n_text1 = i18n.t('已达到')
            if (sourceLinesLinked >= sourceRule.max_out) {
                const i18n_text2 = i18n.t('最大输出连线条数')
                const message = `${i18n_text1}${NODE_DICT[sourceNode.type]}${i18n_text2}`
                return this.getMessage(false, message)
            }
            if (targetLinesLinked >= targetRule.max_in) {
                const i18n_text2 = i18n.t('最大输入连线条数')
                const message = `${i18n_text1}${NODE_DICT[targetNode.type]}${i18n_text2}`
                return this.getMessage(false, message)
            }
        }
        return this.getMessage()
    },
    isLocationValid (loc, data) {
        const rule = NODE_RULE[loc.type]
        if (rule.unique) { // 节点唯一性
            const isLocationOverMount = data.some(item => item.type === loc.type && item.id !== loc.id)
            if (isLocationOverMount) {
                const i18n_text = i18n.t('在模板中只能添加一个')
                const message = `${NODE_DICT[loc.type]}${i18n_text}`
                return this.getMessage(false, message)
            }
        }
        return this.getMessage()
    },
    /**
     * 画布节点连线数目校验
     * @param {Object} data
     */
    isNodeLineNumValid (data) {
        let message
        let tasknode = 0
        let subflow = 0
        const errorId = []
        const isLineNumValid = data.locations.every((loc) => {
            const rule = NODE_RULE[loc.type]
            const name = loc.name || NODE_DICT[loc.type]
            let sourceLinesLinked = 0
            let targetLinesLinked = 0
            if (loc.type === 'tasknode') {
                tasknode += 1
            } else if (loc.type === 'subflow') {
                subflow += 1
            }
            data.lines.forEach((line) => {
                if (line.source.id === loc.id) {
                    targetLinesLinked += 1
                }
                if (line.target.id === loc.id) {
                    sourceLinesLinked += 1
                }
            })
            const i18n_text1 = i18n.t('至少需要')
            if (sourceLinesLinked < rule.min_in) {
                const i18n_text2 = i18n.t('条输入连线')
                message = `${name}${i18n_text1}${rule.min_in}${i18n_text2}`
                errorId.push(loc.id)
                return false
            }
            if (targetLinesLinked < rule.min_out) {
                const i18n_text2 = i18n.t('条输出连线')
                message = `${name}${i18n_text1}${rule.min_out}${i18n_text2}`
                errorId.push(loc.id)
                return false
            }
            return true
        })

        if (!isLineNumValid) {
            return this.getMessage(false, message, errorId)
        }

        if ((tasknode + subflow) === 0) {
            message = i18n.t('请添加任务节点')
            return this.getMessage(false, message)
        }

        return this.getMessage()
    },
    /**
     * 校验 activities、start_event、end_event、gateways 的 incoming、outging 和 flows 的 source、target 是否对应
     * @params {String} node 节点数据
     * @params {Object} flows 数据
     */
    isFlowValid (node, flows) {
        let message = ''
        const { id, incoming, outgoing } = node
        const lineGroup = [incoming, outgoing]
        const valid = !lineGroup.some((item, index) => {
            const type = index === 0 ? 'target' : 'source'
            const lines = Array.isArray(item) ? item : [item]
            return lines.some((line) => {
                if (line === '') {
                    return false
                }
                if (!flows[line]) {
                    message = `flows.${line} data doesn't exist`
                    return true
                }
                if (flows[line][type] !== id) {
                    message = i18n.t(`flows.${line}.${type} doesn't equal to ${id}`)
                    return true
                }
                return false
            })
        })

        return { valid, message }
    },
    /**
     * 画布pipeline_tree数据校验
     */
    isPipelineDataValid (data) {
        const { activities, start_event, end_event, gateways, flows } = data
        let valid = validator(data)
        let message = ''
        let errorId = ''
        if (!valid) {
            const error = validator.errors[0]
            let nodeName = ''
            const nodeReg = /^\.activities\['(\w+)'\]/
            const matchResult = error.dataPath.match(nodeReg)
            if (matchResult) {
                const activity = activities[matchResult[1]]
                if (activity) {
                    nodeName = activity.name
                    errorId = activity.id
                }
            }
            message = `${nodeName} ${error.dataPath} ${error.message}`
            return this.getMessage(valid, message)
        }

        const nodes = [
            start_event,
            end_event,
            ...Object.keys(activities).map(id => activities[id]),
            ...Object.keys(gateways).map(id => gateways[id])
        ]

        valid = !nodes.some((node) => {
            const result = this.isFlowValid(node, flows)
            if (!result.valid) {
                message = result.message
                return true
            }
            // 检查并行网关/条件并行网关是否和汇聚网关相连
            if (['ParallelGateway', 'ConditionalParallelGateway'].includes(node.type)) {
                let branchSinkNodes = new Set()
                this.getBranchNodes(data, node.id, '', branchSinkNodes)
                branchSinkNodes = [...branchSinkNodes]
                if (branchSinkNodes.length === 1 && gateways[branchSinkNodes[0]]?.type === 'ConvergeGateway') {
                    return false
                } else {
                    message = node.type === 'ParallelGateway'
                        ? i18n.t('并行网关缺少对应的汇聚网关')
                        : i18n.t('条件并行网关缺少对应的汇聚网关')
                    errorId = node.id
                    return true
                }
            }
            return false
        })

        return this.getMessage(valid, message, errorId)
    },
    /**
     * id 起始节点
     * firstId 分支上首个节点
     * branchSinkNodes 存在分支
     */
    getBranchNodes (data, id, firstId, branchSinkNodes) {
        const { flows, activities, gateways, end_event } = data
        const targetIds = Object.values(flows).reduce((acc, cur) => {
            if (cur.source === id) {
                acc.push(cur.target)
            }
            return acc
        }, [])
        if (targetIds.length > 1) {
            if (branchSinkNodes.has(firstId)) {
                branchSinkNodes.delete(firstId)
            }
            // 先获取到所有的分支再去递归查找!
            targetIds.forEach(targetId => {
                branchSinkNodes.add(targetId)
            })
            targetIds.forEach(targetId => {
                this.getBranchNodes(data, targetId, targetId, branchSinkNodes)
            })
        } else if (targetIds.length === 1) {
            const targetId = targetIds[0]
            const curId = firstId ? id : targetId
            const { incoming = [], type } = activities[curId] || gateways[curId] || {}
            // 如果只有一条分支并且找到了汇聚网关则退出递归
            if (branchSinkNodes.size <= 1 && type === 'ConvergeGateway') {
                branchSinkNodes.delete(firstId)
                branchSinkNodes.add(curId)
            } else if (incoming.length <= 1) { // 单条输出
                // 找到结束节点则退出递归
                if (end_event.id === targetId) {
                    branchSinkNodes.clear(firstId)
                } else {
                    this.getBranchNodes(data, targetId, firstId, branchSinkNodes)
                }
            } else {
                // 如果该节点有多个输入连线则不继续查找
                branchSinkNodes.delete(firstId)
                branchSinkNodes.add(curId)
            }
        }
    },
    getMessage (result = true, message = '', errorId) {
        return { result, message, errorId }
    }
}

export default validatePipeline
