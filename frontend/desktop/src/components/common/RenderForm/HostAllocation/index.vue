/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="resource-allocation" v-bkloading="{ isLoading: colsLoading, opacity: 1, zIndex: 100 }">
        <resource-list
            v-if="!showFilter"
            ref="resourceList"
            :cols-loading="colsLoading"
            :editable="editable"
            :view-value="viewValue"
            :show-filter.sync="showFilter"
            :cols="tbCols"
            :config="localConfig"
            :urls="urls"
            :separator="localSeparator"
            :value="localValue"
            @importData="importData"
            @update="updateValue"
            @update:separator="updateSeparator">
        </resource-list>
        <host-filter
            v-else
            :show-filter.sync="showFilter"
            :config="localConfig"
            :urls="urls"
            :cols="tbCols"
            @update="updateConfig">
        </host-filter>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import HostFilter from './HostFilter.vue'
    import ResourceList from '../SetAllocation/ResourceList.vue'

    export default {
        name: 'HostAllocation',
        components: {
            HostFilter,
            ResourceList
        },
        props: {
            editable: {
                type: Boolean,
                default: true
            },
            config: {
                type: Object,
                default () {
                    return {
                        host_count: 0,
                        host_screen_value: '',
                        host_resources: [],
                        host_filter_detail: []
                    }
                }
            },
            viewValue: { // 查看值模式，不需要要编辑表单操作
                type: Boolean,
                default: false
            },
            separator: {
                type: String,
                default: ','
            },
            value: {
                type: Array,
                default () {
                    return []
                }
            },
            urls: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                showFilter: false,
                localConfig: tools.deepClone(this.config),
                localValue: this.tranformPropsValueData(this.value),
                localSeparator: this.separator,
                colsLoading: false,
                originalCols: [], // 表格列原始配置项
                tbCols: [], // 增加模块列后的表格配置项
                eligibleHosts: [] // 筛选得到的主机数量
            }
        },
        watch: {
            config: {
                handler (val) {
                    this.localConfig = tools.deepClone(val)
                },
                deep: true
            },
            value: {
                handler (val) {
                    this.localValue = this.tranformPropsValueData(val)
                },
                deep: true
            },
            separator (val) {
                this.localSeparator = val
            }
        },
        mounted () {
            this.getColsConfig()
        },
        methods: {
            ...mapActions([
                'getCCSearchColAttrSet'
            ]),
            /**
             * 转换props的 value 的格式
             */
            tranformPropsValueData (data) {
                const localData = []
                data.forEach(item => {
                    const dataItem = {}
                    Object.keys(item).forEach(key => {
                        // renderForm 组件 value 需要接受 object 类型数据
                        dataItem[key] = {
                            [key]: item[key]
                        }
                    })
                    localData.push(dataItem)
                })
                return localData
            },
            /**
             * 转换组件的 localValue 格式
             */
            transformLocalValueData (data) {
                const propsValue = []
                data.forEach((rowData) => {
                    const dataItem = {}
                    this.tbCols.forEach(col => {
                        const { tag_code: tagCode } = col.config
                        if (tagCode !== 'tb_btns') {
                            dataItem[tagCode] = tools.deepClone(rowData[tagCode][tagCode])
                        }
                    })
                    propsValue.push(dataItem)
                })

                return propsValue
            },
            // 获取表格原始列配置项
            async getColsConfig () {
                try {
                    if (!this.urls['cc_search_create_object_attribute_host']) {
                        return
                    }
                    this.colsLoading = true
                    const resp = await this.getCCSearchColAttrSet({
                        url: this.urls['cc_search_create_object_attribute_host']
                    })
                    if (resp.result) {
                        this.originalCols = resp.data
                        this.joinCols()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.colsLoading = false
                    this.$nextTick(() => {
                        this.validate()
                    })
                }
            },
            // 设置表格头
            joinCols () {
                const cols = this.originalCols.map(item => {
                    let colObj = {}
                    if (item.tag_code === 'bk_host_outerip') {
                        colObj = {
                            width: 150,
                            config: {
                                tag_code: item.tag_code,
                                type: 'textarea',
                                attrs: {
                                    name: item.attrs.name,
                                    editable: true,
                                    validation: [
                                        {
                                            type: 'custom',
                                            args (val) {
                                                let result = true
                                                let message = ''
                                                const hosts = val.split('\n').map(item => item.trim()).filter(item => item !== '')
                                                if (!hosts.length) {
                                                    result = false
                                                    message = gettext('资源不足')
                                                }
                                                return {
                                                    result,
                                                    error_message: message
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    } else {
                        colObj = {
                            width: 100,
                            config: item
                        }
                    }
                    return colObj
                })
                if (!this.viewValue) {
                    cols.push({
                        width: 100,
                        config: {
                            tag_code: 'tb_btns',
                            attrs: {
                                name: gettext('操作')
                            }
                        }
                    })
                }
                this.tbCols = cols
            },
            /**
             * 组装表格数据对象为 renderForm 组件使用的数据格式
             * @param {Number} rowCount 表格行数
             * @param {Array} data 表格原始数据 [{bk_host_id: 'aaa', gamser: ''}...]
             */
            joinValue (rowCount, data) {
                const value = []
                if (rowCount > 0) {
                    for (let i = 0; i < rowCount; i++) {
                        const valItem = {}
                        this.tbCols.forEach(item => {
                            const tagCode = item.config.tag_code
                            if (tagCode !== 'tb_btns') {
                                const rowData = data[i]
                                if (rowData.hasOwnProperty(tagCode)) {
                                    valItem[tagCode] = { // renderForm 组件 value 需要接受 object 类型数据
                                        [tagCode]: rowData[tagCode]
                                    }
                                } else {
                                    // renderForm 组件 value 需要接受 object 类型数据, 优先取标准插件配置项默认值
                                    const val = atomFilter.getFormItemDefaultValue([item.config])
                                    valItem[tagCode] = {
                                        [tagCode]: val
                                    }
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
             * @param {Object} conf 表单配置项数据
             * @param {Object} eligibleHosts 主机数据
             */
            updateConfig (conf, eligibleHosts) {
                this.eligibleHosts = eligibleHosts
                const data = []
                for (let i = 0; i < conf.host_count; i++) {
                    data.push(Object.assign({}, eligibleHosts[i]))
                }
                this.localConfig = conf
                this.getColsConfig()
                this.joinValue(conf.host_count, data)
                this.updatePropsData()
            },
            /**
             * 同步表格编辑的数据
             */
            updateValue (val) {
                this.localValue = val
                this.updatePropsData()
            },
            updateSeparator (val) {
                this.localSeparator = val
                this.updatePropsData()
            },
            // 同步本地组件数据到父组件
            updatePropsData () {
                const propsData = {
                    config: tools.deepClone(this.localConfig),
                    data: this.transformLocalValueData(this.localValue),
                    separator: this.localSeparator
                }
                this.$emit('update', propsData)
            },
            /**
             * excel 数据导入到表格
             * 解析表头数据, 表单列以表格原始配置项基准，匹配导入数据对应列的数据
             *
             * @param {Object} sheetData excel数据
             */
            importData (sheetData) {
                const data = []
                const rowCount = sheetData.length
                const headerMap = {}

                this.originalCols.forEach(col => {
                    const tagCode = col.tag_code
                    const name = col.attrs.name
                    const header = `${name}(${tagCode})`
                    headerMap[header] = tagCode
                })
                sheetData.forEach(row => {
                    const value = {}
                    Object.keys(row).map(header => {
                        const key = headerMap[header]
                        if (key) {
                            value[key] = row[header]
                        }
                    })
                    data.push(value)
                })
                this.joinCols()
                this.joinValue(rowCount, data)
                this.updatePropsData()
            },
            validate () {
                return this.$refs.resourceList.validate()
            }
        }
    }
</script>
<style style="scss" scoped>
    .resource-allocation {
        padding: 10px;
        border: 1px solid #ececec;
        border-radius: 2px;
    }
</style>
<style lang="scss" scoped>
    /deep/ .data-table {
        .bk-table-empty-text {
            width: 100%;
            .no-data-wrapper {
                width: 50%;
            }
        }
    }
</style>
