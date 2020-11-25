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
import tools from '@/utils/tools.js'

/**
 * 转换原始标准插件，匹配继承配置项
 * @param {Object} atoms // 已加载的标准插件列表
 * @param {String} name // 当前标准插件名称
 */
export default function transAtoms (atoms = {}, name = '') {
    if (Object.prototype.toString.call(atoms) !== '[object Object]') {
        atoms = {}
        throw new TypeError('"atoms" should be an object type')
    }
    if (typeof name !== 'string') {
        name = ''
        throw new TypeError('"name" should be a string type')
    }
    if (!atoms[name] || !Array.isArray(atoms[name])) {
        return
    }

    const atomConfig = []
    atoms[name].forEach(conf => {
        const tagItem = tools.deepClone(conf)
        if ('extend' in tagItem) {
            if (typeof tagItem.extend === 'string' && tagItem.extend) {
                const extendPath = tagItem.extend.split('.')
                if (!extendPath.length) {
                    return
                }

                const targetConfig = extendPath.reduce((acc, crt) => {
                    if (Object.prototype.toString.call(acc) === '[object Object]') {
                        if (acc.type === 'combine') {
                            return acc.attrs.children.find(item => item.tag_code === crt)
                        }
                        return acc[crt]
                    } else if (Array.isArray(acc)) {
                        return acc.find(item => item.tag_code === crt)
                    }
                }, atoms)
                const sourceConfig = 'config' in tagItem ? tagItem.config : null
                let mergedConfig = targetConfig
                if (Array.isArray(targetConfig)) {
                    if (sourceConfig) {
                        if (!Array.isArray(sourceConfig)) {
                            throw new TypeError('"config" should be an array type')
                        } else {
                            sourceConfig.forEach(sourceItem => {
                                const index = targetConfig.findIndex(item => item.tag_code === sourceItem.tag_code)
                                if (index > -1) {
                                    const mergedTag = tools.assign(targetConfig[index], sourceItem)
                                    mergedConfig.splice(index, 1, mergedTag)
                                } else {
                                    mergedConfig.push(sourceItem)
                                }
                            })
                        }
                    }
                    atomConfig.push(...mergedConfig)
                } else {
                    if (sourceConfig) {
                        if (Object.prototype.toString.call(sourceConfig) !== '[object Object]') {
                            throw new TypeError('"config" should be a object type')
                        } else {
                            mergedConfig = tools.assign(targetConfig, sourceConfig)
                        }
                    }
                    atomConfig.push(mergedConfig)
                }
            } else {
                throw new TypeError('"extend" should be a string type')
            }
        } else {
            atomConfig.push(tagItem)
        }
    })

    return atomConfig
}
