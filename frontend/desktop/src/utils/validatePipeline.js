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
import { NODE_DICT } from '@/constants/index.js'
import validator, { pipelineTreeSchema } from '@/constants/pipelineTreeSchema.js'

const NODE_RULE = {
    'startpoint': {
        min_in: 0,
        max_in: 0,
        min_out: 1,
        max_out: 1,
        allowed_out: ['tasknode', 'branchgateway', 'parallelgateway', 'subflow'],
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
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'convergegateway', 'endpoint'],
        unique: false
    },
    'subflow': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'convergegateway', 'endpoint'],
        unique: false
    },
    'branchgateway': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1000,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'convergegateway', 'endpoint'],
        unique: false
    },
    'parallelgateway': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1000,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway'],
        unique: false
    },
    'convergegateway': {
        min_in: 1,
        max_in: 1000,
        min_out: 1,
        max_out: 1,
        allowed_out: ['tasknode', 'subflow', 'branchgateway', 'parallelgateway', 'convergegateway', 'endpoint'],
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
            const i18n_text = gettext('相同节点不能回连')
            const message = `${NODE_DICT[sourceNode.type]}${i18n_text}`
            return this.getMessage(false, message)
        }
        if (sourceRule.max_out === 0) {
            const i18n_text = gettext('只能添加输入连线')
            const message = `${NODE_DICT[sourceNode.type]}${i18n_text}`
            return this.getMessage(false, message)
        }

        if (targetRule.max_in === 0) {
            const i18n_text = gettext('只能添加输出连线')
            const message = `${NODE_DICT[targetNode.type]}${i18n_text}`
            return this.getMessage(false, message)
        }

        if (sourceRule.allowed_out.indexOf(targetNode.type) === -1) {
            const i18n_text = gettext('不能连接')
            const message = `${NODE_DICT[sourceNode.type]}${i18n_text}${NODE_DICT[targetNode.type]}`
            return this.getMessage(false, message)
        }
        const isSameLine = lines.some(item => {
            if (item.source.id === sourceId) {
                sourceLinesLinked += 1
                if (item.target.id === targetId) {
                    return true
                }
            }
            if (item.target.id === targetId) {
                targetLinesLinked += 1
            }
            if (item.source.id === targetId && item.target.id === sourceId) {
                isLoop = true
            }
        })

        if (isLoop) {
            const message = gettext('相同节点不能回连')
            return this.getMessage(false, message)
        }

        if (isSameLine) {
            const message = gettext('重复添加连线')
            return this.getMessage(false, message)
        } else {
            const i18n_text1 = gettext('已达到')
            if (sourceLinesLinked >= sourceRule.max_out) {
                const i18n_text2 = gettext('最大输出连线条数')
                const message = `${i18n_text1}${NODE_DICT[sourceNode.type]}${i18n_text2}`
                return this.getMessage(false, message)
            }
            if (targetLinesLinked >= targetRule.max_in) {
                const i18n_text2 = gettext('最大输入连线条数')
                const message = `${i18n_text1}${NODE_DICT[targetNode.type]}${i18n_text2}`
                return this.getMessage(false, message)
            }
        }
        return this.getMessage()
    },
    isLocationValid (loc, data) {
        const rule = NODE_RULE[loc.type]
        if (rule.unique) { // 节点唯一性
            const isLocationOverMount = data.some(item => {
                return item.type === loc.type && item.id !== loc.id
            })
            if (isLocationOverMount) {
                const i18n_text = gettext('在模板中只能添加一个')
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
        const isLineNumValid = data.locations.every(loc => {
            const rule = NODE_RULE[loc.type]
            const name = loc.name || NODE_DICT[loc.type]
            let sourceLinesLinked = 0
            let targetLinesLinked = 0
            if (loc.type === 'tasknode') {
                tasknode += 1
            } else if (loc.type === 'subflow') {
                subflow += 1
            }
            data.lines.forEach(line => {
                if (line.source.id === loc.id) {
                    targetLinesLinked += 1
                }
                if (line.target.id === loc.id) {
                    sourceLinesLinked += 1
                }
            })
            const i18n_text1 = gettext('至少需要')
            if (sourceLinesLinked < rule.min_in) {
                const i18n_text2 = gettext('条输入连线')
                message = `${name}${i18n_text1}${rule.min_in}${i18n_text2}`
                return false
            }
            if (targetLinesLinked < rule.min_out) {
                const i18n_text2 = gettext('条输出连线')
                message = `${name}${i18n_text1}${rule.min_out}${i18n_text2}`
                return false
            }
            return true
        })

        if (!isLineNumValid) {
            return this.getMessage(false, message)
        }

        if ((tasknode + subflow) === 0) {
            message = gettext('请添加任务节点')
            return this.getMessage(false, message)
        }

        return this.getMessage()
    },
    /**
     * 画布pipeline_tree数据校验
     */
    isPipelineDataValid (data) {
        return validator.validate(data, pipelineTreeSchema)
    },
    getMessage (result = true, message = '') {
        return { result, message }
    }
}

export default validatePipeline
