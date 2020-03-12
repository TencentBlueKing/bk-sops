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
<template>
    <div class="resource-allocation">
        <resource-list
            v-show="!showFilter"
            ref="resourceList"
            :show-filter.sync="showFilter"
            :cols="tbCols"
            :config="localConfig"
            :value="localValue"
            @importData="importData"
            @update="updateValue">
        </resource-list>
        <resource-filter
            v-if="showFilter"
            :show-filter.sync="showFilter"
            :config="localConfig"
            @update="updateConfig">
        </resource-filter>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import ResourceList from './ResourceList.vue'
    import ResourceFilter from './ResourceFilter.vue'

    export default {
        name: 'ResourceAllocation',
        components: {
            ResourceList,
            ResourceFilter
        },
        props: {
            config: {
                type: Object,
                default () {
                    return {
                        set_template_id: '',
                        host_resources: [],
                        set_count: 0,
                        module_detail: []
                    }
                }
            },
            value: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                showFilter: false,
                localConfig: this.config,
                localValue: this.value,
                colsLoading: false,
                originalCols: [], // 表格列原始配置项
                tbCols: [] // 增加模块列后的表格配置项
            }
        },
        mounted () {
            this.getColsConfig()
        },
        methods: {
            ...mapActions([
                'getCCSearchColAttrSet'
            ]),
            async getColsConfig () {
                try {
                    this.colsLoading = true
                    const resp = await this.getCCSearchColAttrSet()
                    if (resp.result) {
                        this.originalCols = resp.data
                        this.joinCols(this.localConfig.module_detail)
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.colsLoading = false
                }
            },
            // 将模块列拼接到表格中，从第二列开始
            joinCols (modules) {
                const modulesConfig = []
                const originalConfig = this.originalCols.map(item => {
                    return {
                        width: 100,
                        config: item
                    }
                })
                modules.forEach(item => {
                    modulesConfig.push({
                        width: 120,
                        config: {
                            tag_code: item.name,
                            type: 'textarea',
                            module: true, // module 字段用来标识表格列是否为模块数据
                            attrs: {
                                name: gettext('模块:') + item.name + '(' + item.host_count + ')',
                                editable: true,
                                validation: [{ type: 'required' }]
                            }
                        }
                    })
                })
                const cols = [...originalConfig.slice(0, 1), ...modulesConfig, ...originalConfig.slice(1)]
                cols.push({
                    width: 100,
                    config: {
                        tag_code: 'tb_btns',
                        attrs: {
                            name: gettext('操作')
                        }
                    }
                })
                this.tbCols = cols
            },
            /**
             * 组装表格数据对象为 renderForm 组件使用的数据格式
             * @param {Number} rowCount 表格行数
             * @param {Array} data 表格原始数据 [{bk_set_name: 'aaa', gamser: ''}...]
             */
            joinValue (rowCount, data) {
                const value = []
                if (rowCount > 0) {
                    for (let i = 0; i < rowCount; i++) {
                        const valItem = []
                        this.tbCols.forEach(item => {
                            const tagCode = item.config.tag_code
                            if (tagCode !== 'tb_btns') {
                                const rowData = data[i]
                                if (rowData.hasOwnProperty(tagCode)) {
                                    const val = item.config.module ? rowData[tagCode].join('\n') : rowData[tagCode]
                                    valItem.push({
                                        [tagCode]: val
                                    })
                                } else {
                                    valItem.push({})
                                }
                            }
                        })
                        value.push(valItem)
                    }
                }
                this.localValue = value
            },
            /**
             * 同步资源筛选面板的数据
             *
             * @param {Object} conf 资源筛选表单配置项数据
             * @param {Object} moduleData 包含模块的主机数据
             */
            updateConfig (conf, moduleData) {
                const data = []
                for (let i = 0; i < conf.set_count; i++) {
                    data.push(Object.assign({}, moduleData))
                }

                this.localConfig = conf
                this.joinCols(this.localConfig.module_detail)
                this.joinValue(conf.set_count, data)
            },
            /**
             * 同步表格编辑的数据
             */
            updateValue (val) {
                this.localValue = val
            },
            /**
             * excel 数据导入到表格
             * 解析表头数据，模块列取导入数据，其他表单列以表格原始配置项基准，匹配导入数据对应列的数据
             *
             * @param {Object} sheetData excel数据
             */
            importData (sheetData) {
                const modules = []
                const data = []
                const rowCount = sheetData.length
                const headerMap = {}
                const moduleNameReg = /[\u4e00-\u9fa5\w]+\:(\w+)\((\d+)\)$/ // 表头模块列字符匹配

                this.originalCols.forEach(col => {
                    const tagCode = col.tag_code
                    const name = col.attrs.name
                    const header = `${name}(${tagCode})`
                    headerMap[header] = tagCode
                })
                sheetData.forEach(row => {
                    const value = {}
                    Object.keys(row).map(header => {
                        const moduleMatchResult = header.match(moduleNameReg)
                        if (moduleMatchResult) { // 模块列
                            const key = moduleMatchResult[1]
                            const count = moduleMatchResult[2]
                            if (!headerMap.hasOwnProperty(header)) {
                                headerMap[header] = key
                                modules.push({
                                    name: key,
                                    host_count: count
                                })
                            }
                            value[key] = row[header].split('\n').map(ip => ip.trim())
                        } else {
                            const key = headerMap[header]
                            if (key) {
                                value[key] = row[header]
                            }
                        }
                    })
                    data.push(value)
                })
                this.joinCols(modules)
                this.joinValue(rowCount, data)
            },
            validate () {
                this.$refs.resourceList && this.$refs.resourceList.validate()
            }
        }
    }
</script>
<style style="scss" scoped>
    .resource-allocation {
        width: 800px;
        background: #ffffff;
    }
</style>
