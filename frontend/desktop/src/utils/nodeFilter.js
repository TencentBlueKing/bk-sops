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
import { uuid } from './uuid.js'
const nodeFilter = {
    isNodeExisted (type, data) {
        if (type && data) {
            return data.some(item => {
                return item.type === type
            })
        }
    },
    getNodeTypeById (id, data) {
        let nodeIndex
        data.some((item, index) => {
            if (item.id === id) {
                nodeIndex = index
                return true
            }
        })
        return data[nodeIndex].type
    },
    getNewValidId (id, prefix = 'temp') {
        const reg = new RegExp('^[a-zA-Z]+')
        if (!reg.test(id)) {
            return `${prefix}${uuid()}`
        }
        return id
    },
    convertInvalidIdData (key, primaryData) {
        const keysOfIdRelated = ['id', 'incoming', 'outgoing', 'source', 'target', 'conditions']
        let newData = {}
        switch (key) {
            case 'activities':
            case 'flows':
            case 'gateways':
                for (const key in primaryData) {
                    const newKey = this.getNewValidId(key)
                    newData[newKey] = primaryData[key]
                    keysOfIdRelated.forEach(item => {
                        const val = newData[newKey][item]
                        if (val !== undefined && val !== '') {
                            if (typeof val === 'string') {
                                newData[newKey][item] = this.getNewValidId(val)
                            } else if (Array.isArray(val)) {
                                newData[newKey][item] = val.map(v => {
                                    return this.getNewValidId(v)
                                })
                            }
                            if (item === 'conditions') {
                                const newVal = {}
                                for (const conditionId in val) {
                                    const newConditionId = this.getNewValidId(conditionId)
                                    newVal[newConditionId] = val[conditionId]
                                }
                                newData[newKey][item] = newVal
                            }
                        }
                    })
                }
                return newData
            case 'end_event':
            case 'start_event':
                newData = Object.assign({}, primaryData)
                keysOfIdRelated.forEach(item => {
                    const val = newData[item]
                    if (val !== undefined && val !== '') {
                        newData[item] = this.getNewValidId(val)
                    }
                })
                return newData
            case 'line':
                newData = [...primaryData]
                newData.forEach((item, index) => {
                    item.id = this.getNewValidId(item.id)
                    item.source.id = this.getNewValidId(item.source.id)
                    item.target.id = this.getNewValidId(item.target.id)
                })
                return newData
            case 'location':
                newData = [...primaryData]
                newData.forEach((item) => {
                    item.id = this.getNewValidId(item.id)
                })
                return newData
            default:
                return primaryData
        }
    }
}

export default nodeFilter
