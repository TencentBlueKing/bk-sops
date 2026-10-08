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

/**
 * 变量引用分组定义，与后端 analysis_constants_ref 接口返回的字段保持一致
 */
export const CITED_GROUPS = [
    {
        key: 'activities',
        title: '任务节点'
    },
    {
        key: 'conditions',
        title: '分支条件'
    },
    {
        key: 'constants',
        title: '全局变量'
    }
]

/**
 * 解析单个变量的引用详情，生成用于展示的分组数据
 * @param {Object} citedList 变量引用数据，结构为 { activities: [], conditions: [], constants: [] }
 * @param {Object} source 解析引用名称所需的数据源
 * @param {Object} source.activities 任务节点数据
 * @param {Array} source.lines 流程连线数据
 * @param {Object} source.gateways 网关节点数据
 * @param {Object} source.variableList 变量数据（内置变量 + 全局变量）
 * @return {Array} 引用分组详情，仅返回存在引用数据的分组
 */
export function getCitedGroups (citedList = {}, source = {}) {
    const {
        activities = {},
        lines = [],
        gateways = {},
        variableList = {}
    } = source

    return CITED_GROUPS.map(group => {
        const { key, title } = group
        const citedIds = citedList[key] || []
        const data = citedIds.map(id => {
            let name = ''
            if (key === 'activities') {
                name = activities[id] ? activities[id].name : ''
            } else if (key === 'conditions') {
                const line = lines.find(item => item.id === id)
                const nodeId = line && line.source ? line.source.id : ''
                const gateway = nodeId ? gateways[nodeId] : null
                name = gateway && gateway.conditions[id] ? gateway.conditions[id].name : ''
            } else {
                name = variableList[id] ? variableList[id].name : ''
            }
            return { id, name }
        })
        return { key, title, data }
    }).filter(group => group.data.length > 0)
}
