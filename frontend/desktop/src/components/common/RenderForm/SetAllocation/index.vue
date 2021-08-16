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
            :loading="colsLoading || moduleLoading"
            :has-diff="hasColsChanged || deletedMds.length > 0"
            :editable="editable"
            :view-value="viewValue"
            :show-filter.sync="showFilter"
            :cols="tbCols"
            :config="localConfig"
            :urls="urls"
            :separator="localSeparator"
            :value="localValue"
            @importData="importData"
            @handleDiff="handleDiff"
            @update="updateValue"
            @update:separator="updateSeparator">
        </resource-list>
        <resource-filter
            v-else
            :show-filter.sync="showFilter"
            :config="localConfig"
            :urls="urls"
            @update="updateConfig">
        </resource-filter>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import ResourceList from './ResourceList.vue'
    import ResourceFilter from './ResourceFilter.vue'

    export default {
        name: 'ResourceAllocation',
        components: {
            ResourceList,
            ResourceFilter
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
                        set_template_id: '',
                        host_resources: [],
                        set_count: 0,
                        module_detail: []
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
                localValue: this.tranformPropsModuleData(this.value),
                localSeparator: this.separator,
                originalCols: [], // 已保存数据属性列
                crtCols: [], // 从CMDB拉取的当前最新的属性列
                colsLoading: false,
                hasColsChanged: false, // 是否存在已保存的数据中属性列与当前从CMDB拉取的属性存在差异的情况
                crtModules: [], // 已选择集群模板当前的模块信息
                deletedMds: [], // 是否存在已保存的数据中有模块在当前从CMDB拉取的模块中被删除的情况
                moduleLoading: false,
                tbCols: [] // 增加模块列后的表格配置项
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
                    this.localValue = this.tranformPropsModuleData(val)
                },
                deep: true
            },
            separator (val) {
                this.localSeparator = val
            }
        },
        mounted () {
            this.getColsConfig()
            if (this.config.set_template_id !== '') {
                this.getModule(this.config.set_template_id)
            }
        },
        methods: {
            ...mapActions([
                'getCCSearchColAttrSet',
                'getCCSearchModule'
            ]),
            /**
             * 转换 value 的格式
             * value 中保存的模块数据统一放在 key 为 `__module` 的数组里，需要把里面的数据提取出来
             *
             */
            tranformPropsModuleData (data) {
                const localData = []
                data.forEach(item => {
                    const dataItem = {}
                    Object.keys(item).forEach(key => {
                        if (key !== '__module') {
                            dataItem[key] = { // renderForm 组件 value 需要接受 object 类型数据
                                [key]: tools.deepClone(item[key])
                            }
                        } else {
                            if (item[key].length > 0) {
                                item[key].forEach(md => {
                                    dataItem[md.key] = {
                                        [md.key]: md.value.join('\n')
                                    }
                                })
                            }
                        }
                    })
                    localData.push(dataItem)
                })
                return localData
            },
            /**
             * 转换组件的 localValue 格式
             * 把组件模块数据收到 `__module` 属性中
             */
            transformLocalModuleData (data) {
                const propsValue = []
                data.forEach((rowData) => {
                    const dataItem = {
                        '__module': []
                    }
                    this.tbCols.forEach(col => {
                        const { tag_code: tagCode, module } = col.config
                        if (tagCode !== 'tb_btns') {
                            if (module) { // 模块列
                                dataItem.__module.push({
                                    key: tagCode,
                                    value: rowData[tagCode][tagCode].split('\n').map(item => item.trim()).filter(item => item !== '')
                                })
                            } else { // 普通数据列
                                dataItem[tagCode] = tools.deepClone(rowData[tagCode][tagCode])
                            }
                        }
                    })
                    propsValue.push(dataItem)
                })

                return propsValue
            },
            async getModule (id) {
                const setId = id.replace(/^set_/, '')
                try {
                    if (!this.urls['cc_search_module']) {
                        return
                    }
                    this.moduleLoading = true
                    const params = {
                        url: this.urls['cc_search_module'],
                        bk_set_id: setId
                    }
                    const resp = await this.getCCSearchModule(params)
                    if (resp.result) {
                        this.crtModules = resp.data.info
                        if (Array.isArray(this.value) && this.value.length > 0) {
                            this.value[0].__module.forEach(m => {
                                if (!this.crtModules.find(item => item.bk_module_name === m.key)) {
                                    this.deletedMds.push(m.key)
                                }
                            })
                        }
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.moduleLoading = false
                }
            },
            // 获取表格原始列配置项
            async getColsConfig () {
                try {
                    if (!this.urls['cc_search_create_object_attribute_set']) {
                        return
                    }
                    this.colsLoading = true
                    const resp = await this.getCCSearchColAttrSet({
                        url: this.urls['cc_search_create_object_attribute_set']
                    })
                    if (resp.result) {
                        const index = resp.data.findIndex(item => item.tag_code === 'bk_set_name')
                        if (index > 0) { // 处理接口返回的列数据，集群名固定在第一列
                            const cols = resp.data.slice(0)
                            const firstCol = cols.splice(index, 1)
                            this.crtCols = firstCol.concat(cols)
                        } else {
                            this.crtCols = resp.data
                        }
                        const modules = this.localConfig.module_detail.slice(0)
                        if (Array.isArray(this.value) && this.value.length > 0) { // 编辑
                            this.value[0].__module.forEach(m => {
                                if (!modules.find(i => i.name === m.key)) {
                                    modules.push({
                                        name: m.key
                                    })
                                }
                            })
                            Object.keys(this.value[0]).forEach(key => {
                                if (key !== '__module') {
                                    const col = this.crtCols.find(i => i.tag_code === key)
                                    if (col) {
                                        this.originalCols.push(col)
                                    } else {
                                        this.hasColsChanged = true
                                    }
                                }
                            })
                            if (!this.hasColsChanged) {
                                this.crtCols.some(c => {
                                    if (!this.value[0][c.tag_code]) {
                                        this.hasColsChanged = true
                                        return true
                                    }
                                })
                            }
                        } else {
                            this.originalCols = tools.deepClone(this.crtCols)
                        }
                        this.joinCols(modules)
                    }
                } catch (e) {
                    console.log(e)
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
                    const count = item.host_count
                    modulesConfig.push({
                        width: 150,
                        config: {
                            tag_code: item.name,
                            type: 'textarea',
                            module: true, // module 字段用来标识表格列是否为模块数据
                            attrs: {
                                name: gettext('模块：') + item.name + ('host_count' in item ? `(${item.host_count})` : ''),
                                editable: true,
                                validation: [
                                    {
                                        type: 'custom',
                                        args (val) {
                                            let result = true
                                            let message = ''
                                            const hosts = val.split('\n').map(item => item.trim()).filter(item => item !== '')
                                            if (hosts.length < count) {
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
                    })
                })
                const cols = [...originalConfig.slice(0, 1), ...modulesConfig, ...originalConfig.slice(1)]
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
             * @param {Array} data 表格原始数据 [{bk_set_name: 'aaa', gamser: ''}...]
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
                                    let val = item.config.module ? rowData[tagCode].join('\n') : rowData[tagCode]
                                    if (item.config.type === 'int' && typeof val === 'string' && !!val) {
                                        val = Number(val)
                                    }
                                    if (item.config.type === 'input' && typeof val === 'number') {
                                        val = String(val)
                                    }
                                    valItem[tagCode] = { // renderForm 组件 value 需要接受 object 类型数据
                                        [tagCode]: val
                                    }
                                } else {
                                    // renderForm 组件 value 需要接受 object 类型数据, 优先取标准插件配置项默认值
                                    const val = atomFilter.getFormItemDefaultValue([item.config])
                                    valItem[tagCode] = val
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
                    data.push(Object.assign({}, moduleData[i]))
                }

                this.localConfig = conf
                this.hasColsChanged = false
                this.deletedMds = []
                this.joinCols(this.localConfig.module_detail)
                this.joinValue(conf.set_count, data)
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
                this.validate()
                this.updatePropsData()
            },
            // 同步本地组件数据到父组件
            updatePropsData () {
                const propsData = {
                    config: tools.deepClone(this.localConfig),
                    data: this.transformLocalModuleData(this.localValue),
                    separator: this.localSeparator
                }
                this.$emit('update', propsData)
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
                const moduleNameReg = /[\u4e00-\u9fa5\w]+\uff1a(\w+)\((\d+)\)$/ // 表头模块列字符匹配，eg: 模块：console(3)
                
                this.colsLoading = true
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
                            value[key] = row[header].split('\n').map(ip => ip.trim()).filter(item => item !== '')
                        } else {
                            const key = headerMap[header]
                            if (key) {
                                value[key] = row[header]
                            }
                        }
                    })
                    data.push(value)
                })
                this.$nextTick(() => {
                    this.joinCols(modules)
                    this.joinValue(rowCount, data)
                    this.localConfig = {
                        set_template_id: '',
                        host_resources: [],
                        set_count: 0,
                        module_detail: []
                    }
                    this.updatePropsData()
                    this.colsLoading = false
                })
            },
            // 处理变量保存的数据与最新的CMDB集群配置存在的差异
            // 变量保存的模块被删除，移除对应模块数据
            // 变量保存的属性被删除，移除对应属性数据，CMDB属性有增加，则添加到保存数据里
            handleDiff () {
                const val = tools.deepClone(this.localValue)
                if (this.deletedMds.length > 0) {
                    this.deletedMds.forEach(key => {
                        this.localValue.forEach(item => {
                            delete item[key]
                        })
                    })
                }
                if (this.hasColsChanged) {
                    val.forEach(item => {
                        Object.keys(this.value[0]).forEach(key => {
                            if (key !== '__module') {
                                const col = this.crtCols.find(c => c.tag_code === key)
                                if (!col) {
                                    delete item[key]
                                    this.localConfig.module_detail = this.localConfig.module_detail.filter(item => item.name !== key)
                                }
                            }
                        })
                        this.crtCols.forEach(c => {
                            if (c.tag_code !== '__module' && !(c.tag_code in this.value[0])) {
                                item[c.tag_code] = {
                                    [c.tag_code]: atomFilter.getFormItemDefaultValue([c])
                                }
                            }
                        })
                    })
                    this.originalCols = tools.deepClone(this.crtCols)
                }
                this.joinCols(this.localConfig.module_detail)
                this.updateValue(val)
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
