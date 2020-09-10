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
<template>
    <div class="resource-filter">
        <header class="set-form">
            <span class="title">{{ i18n.title }}</span>
            <div class="btns">
                <bk-button theme="primary" size="small" :loading="pending.host" @click="onConfigConfirm">{{ i18n.confirm }}</bk-button>
                <bk-button
                    theme="default"
                    size="small"
                    @click="$emit('update:showFilter', false)">
                    {{ i18n.cancel }}
                </bk-button>
            </div>
        </header>
        <section class="module-form">
            <bk-form ref="setForm" :model="formData" :rules="setRules">
                <!--筛选方案-->
                <bk-form-item :label="i18n.screenScheme" :required="true" property="screenValue">
                    <el-autocomplete
                        class="inline-input"
                        v-model="formData.screenValue"
                        :fetch-suggestions="querySearch"
                        @select="handleSelect"
                    ></el-autocomplete>
                    <!-- <bk-select
                        :disabled="false"
                        v-model="formData.screenValue"
                        searchable
                        :loading="pending.screen"
                        @selected="onSelected">
                        <bk-option v-for="option in screenListArr"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select> -->
                    <!-- <bk-button theme="primary" class="save-screen" @click="onSaveProgram">{{i18n.save}}</bk-button> -->
                </bk-form-item>
                <!--主机个数-->
                <bk-form-item :label="i18n.resourceNum" :required="true" property="clusterCount">
                    <bk-input v-model="formData.clusterCount" type="number" :min="0"></bk-input>
                </bk-form-item>
                <!--主机资源所属-->
                <bk-form-item :label="i18n.resource" :required="true" property="resource">
                    <bk-select
                        multiple
                        ext-popover-cls="common-bk-select-hide-option"
                        :value="formData.resource|filterResourceId"
                        :loading="pending.resource"
                        @clear="onResourceClear">
                        <template v-if="formData.resource.length > 0">
                            <bk-option
                                v-for="item in formData.resource"
                                :key="item.id"
                                :id="item.id"
                                :name="item.label">
                            </bk-option>
                        </template>
                        <el-tree
                            ref="resourceTree"
                            node-key="id"
                            default-expand-all
                            show-checkbox
                            check-strictly
                            :props="{
                                disabled: setResourceDisabled
                            }"
                            :data="resourceList"
                            @check="onResourceSelect">
                        </el-tree>
                    </bk-select>
                </bk-form-item>
                <!--主机筛选条件-->
                <div class="condition-wrapper">
                    <select-condition
                        ref="filterConditions"
                        :label="i18n.filter"
                        :condition-fields="conditions"
                        :conditions="screenArr"
                        @change="updateCondition($event)">
                    </select-condition>
                </div>
            </bk-form>
        </section>
    </div>
</template>
<script >
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import SelectCondition from '../IpSelector/SelectCondition.vue'

    export default {
        name: 'HostFilter',
        filters: {
            filterResourceId (data) {
                return data.map(item => item.id)
            }
        },
        components: {
            SelectCondition
        },
        props: {
            config: {
                type: Object,
                default () {
                    return {
                        set_count: 0,
                        set_template_id: '',
                        host_resources: [],
                        module_detail: []
                    }
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
            const { set_count, host_resources, set_template_id } = tools.deepClone(this.config)
            return {
                screenArr: [],
                formData: {
                    clusterCount: set_count,
                    screenValue: set_template_id,
                    resource: host_resources,
                    host_filter_list: [{
                        filter: [],
                        exclude: []
                    }]
                },
                setRules: {
                    clusterCount: [
                        {
                            required: true,
                            message: gettext('必选项'),
                            trigger: 'blur'
                        }
                    ],
                    screenValue: [
                        {
                            required: true,
                            message: gettext('必选项'),
                            trigger: 'blur'
                        }
                    ],
                    resource: [
                        {
                            required: true,
                            message: gettext('必选项'),
                            trigger: 'blur'
                        }
                    ],
                    count: [{
                        required: true,
                        message: gettext('必填项'),
                        trigger: 'blur'
                    }]
                },
                validatingTabIndex: 0, // 正在被校验的 module tab，每次校验之前清零
                setList: [], // 集群模板 tree
                resourceList: [], // 主机资源所属 tree
                moduleList: [], // 集群下模块列表
                activeTab: '',
                conditions: [],
                pending: {
                    screen: false,
                    resource: false,
                    module: false,
                    condition: false,
                    host: false
                },
                i18n: {
                    title: gettext('资源筛选'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消'),
                    cluster: gettext('集群个数'),
                    set: gettext('集群模板'),
                    resource: gettext('主机资源所属'),
                    resourceNum: gettext('主机数量'),
                    reuse: gettext('复用其他模块机器'),
                    reuseModule: gettext('复用模块'),
                    filter: gettext('主机筛选条件'),
                    exclude: gettext('主机排除条件'),
                    save: gettext('保存'),
                    screenScheme: gettext('筛选方案')
                },
                screenListArr: []
            }
        },
        async mounted () {
            // this.getSetTopo()
            this.getResource()
            this.getCondition()
            const { module_detail } = tools.deepClone(this.config)
            if (module_detail.length) {
                module_detail.forEach(item => {
                    this.screenArr = [...item.exclude, ...item.filter]
                })
            }
        },
        methods: {
            ...mapActions([
                'getHostInCC',
                'getCCSearchTopoSet',
                'getCCSearchTopoResource',
                'getCCSearchModule',
                'getCCSearchObjAttrHost'
            ]),
            ...mapActions('task/', [
                'configProgramList',
                'saveScreenProgram'
            ]),
            // 获取筛选方案数据
            async querySearch (queryString, cb) {
                try {
                    this.pending.screen = true
                    const resp = await this.configProgramList('host')
                    if (resp.result) {
                        const screenListArr = resp.data
                        screenListArr.forEach(item => {
                            item['value'] = item.name
                        })
                        const results = queryString ? screenListArr.filter(this.createFilter(queryString)) : screenListArr
                        // 调用 callback 返回建议列表的数据
                        cb(results)
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.screen = false
                }
            },
            createFilter (queryString) {
                return (restaurant) => {
                    return (restaurant.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0)
                }
            },
            handleSelect (item) {
                console.log(item, '22222222')
            },
            // 获取筛选方案数据
            // async getSetTopo () {
            //     try {
            //         this.pending.screen = true
            //         const resp = await this.configProgramList('host')
            //         if (resp.result) {
            //             this.screenListArr = resp.data
            //         } else {
            //             errorHandler(resp, this)
            //         }
            //     } catch (error) {
            //         errorHandler(error, this)
            //     } finally {
            //         this.pending.screen = false
            //     }
            // },
            // 保存筛选方案
            async onSaveProgram () {
                const selectObj = this.screenListArr.filter(item => {
                    return item.id === this.formData.screenValue
                })[0]
                selectObj['config_type'] = 'host'
                try {
                    const resp = await this.saveScreenProgram(selectObj)
                    if (resp.result) {
                        this.screenListArr = resp.data
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            // 获取资源所属数据
            async getResource () {
                try {
                    if (!this.urls['cc_search_topo_module']) {
                        return
                    }
                    this.pending.resource = true
                    const resp = await this.getCCSearchTopoResource({
                        url: this.urls['cc_search_topo_module']
                    })
                    if (resp.result) {
                        this.resourceList = resp.data
                        if (this.formData.resource.length > 0) {
                            const keys = this.formData.resource.map(item => item.id)
                            this.$refs.resourceTree && this.$refs.resourceTree.setCheckedKeys(keys)
                        }
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.resource = false
                }
            },
            async getCondition () {
                try {
                    if (!this.urls['cc_search_object_attribute_host']) {
                        return
                    }
                    this.pending.condition = true
                    const resp = await this.getCCSearchObjAttrHost({
                        url: this.urls['cc_search_object_attribute_host']
                    })
                    if (resp.result) {
                        this.conditions = resp.data.map(item => {
                            return {
                                id: item.value,
                                name: item.text
                            }
                        })
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.condition = false
                }
            },
            
            // 主机资源所属，选中父节点后子节点不可选
            setResourceDisabled (data, node) {
                if (this.formData.resource.length > 0) {
                    let parentNode = node.parent
                    let isParentChecked = false
                    while (parentNode) {
                        const index = this.formData.resource.findIndex(item => item.id === parentNode.data.id)
                        if (index > -1) {
                            isParentChecked = true
                            break
                        } else {
                            parentNode = parentNode.parent
                        }
                    }
                    return isParentChecked
                } else {
                    return false
                }
            },
            // 主机资源所属，选中父节点后取消所有子节点的选中态
            unCheckChildrenNodes (current, checkedNodes) {
                current.children.forEach(item => {
                    const index = checkedNodes.findIndex(node => node.id === item.id)
                    if (index > -1) {
                        checkedNodes.splice(index, 1)
                    }
                    if (item.children && item.children.length > 0) {
                        this.unCheckChildrenNodes(item, checkedNodes)
                    }
                })
            },
            // 清空所选主机资源
            onResourceClear () {
                this.formData.resource = []
                this.$refs.resourceTree.setCheckedNodes([])
            },
            // 主机资源所属节点点击事件
            onResourceSelect (checked, data) {
                const checkedNodes = data.checkedNodes
                if (checked.children && checked.children.length > 0) {
                    this.unCheckChildrenNodes(checked, checkedNodes)
                }
                this.formData.resource = checkedNodes.map(item => {
                    return {
                        id: item.id,
                        label: item.label
                    }
                })
                this.$refs.resourceTree.setCheckedNodes(checkedNodes)
            },

            // 主机筛选条件change事件
            updateCondition (value) {
                this.screenArr = value
            },
            // 点击确定，校验表单，提交数据
            onConfigConfirm () {
                if (this.pending.host) {
                    return
                }
                this.screenArr.forEach(item => {
                    this.formData.host_filter_list[0][item.type].push(item)
                })
                this.$refs.setForm.validate().then(async validator => {
                    this.getHostsAndSave()
                })
            },
            // 保存资源筛选面板的表单数据，向父级同步
            async getHostsAndSave () {
                const { clusterCount, host_filter_list, resource, screenValue } = this.formData
                try {
                    this.pending.host = true
                    const fields = []
                    host_filter_list.forEach(md => {
                        md.filter.forEach(item => {
                            if (item.field !== '' && !fields.includes(item.field)) {
                                fields.push(item.field)
                            }
                        })
                        md.exclude.forEach(item => {
                            if (item.field !== '' && !fields.includes(item.field)) {
                                fields.push(item.field)
                            }
                        })
                    })
                    const topo = resource.map(item => {
                        const [bk_obj_id, bk_inst_id] = item.id.split('_')
                        return {
                            bk_obj_id,
                            bk_inst_id
                        }
                    })
                    const hostData = await this.getHostInCC({
                        url: this.urls['cc_search_host'],
                        fields,
                        topo
                    })
                    const moduleHosts = this.filterModuleHost(hostData.data)
                    const moduleDetail = host_filter_list.map(item => {
                        const { filter, exclude } = item
                        // 取有效筛选、排除条件，不做校验（和 ip 选择器有区别，这里多个 tab 有多个相同 refs）
                        const validFilters = filter.filter(item => item.filed !== '' && item.value.length > 0)
                        const validExclude = exclude.filter(item => item.filed !== '' && item.value.length > 0)

                        return {
                            filter: validFilters,
                            exclude: validExclude
                        }
                    })
                    const config = {
                        set_count: clusterCount,
                        set_template_id: screenValue,
                        host_resources: resource,
                        module_detail: moduleDetail
                    }
                    this.$emit('update', config, moduleHosts)
                    this.$emit('update:showFilter', false)
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.host = false
                }
            },
            /**
             * 根据接口返回的全量 host 数据，筛选出对应模块的 host 值，每个集群(资源表格的每一行)主机资源不能重复
             * host 值需要同时满足筛选条件和排除条件
             * 非复用模块间主机不能重复，先分别计算所有满足模块条件的主机，再计算模块所需主机数与满足条件主机的比值，值大的模块优先在主机里取值
             * 模块复用时，取其复用的模块主机数据
             * 每个模块的 host 数量不能超过 moudule.count 设置
             *
             * @param {Array} data 全量的 host 数据
             *
             * @return {Object} 满足每个 module 设置条件的 host 值，格式: {gamserver: [xx.xx.x.x, x.x.x.xxx], ...}
             */
            filterModuleHost (data) {
                let hostLists = [] // 所有满足主机数据
                this.formData.host_filter_list.forEach(md => {
                    const { filter, exclude } = md
                    const validFilters = filter.filter(item => item.filed !== '' && item.value.length > 0)
                    const validExclude = exclude.filter(item => item.filed !== '' && item.value.length > 0)
                    // 未复用其他模块主机，则计算本模块数据
                    if (validFilters.length === 0 && validExclude.length === 0) { // 筛选条件和排序条件为空，按照设置的主机数截取
                        hostLists = data.map(d => d)
                    } else {
                        const filterObj = this.transFieldArrToObj(validFilters)
                        const excludeObj = this.transFieldArrToObj(validExclude)
                        data.forEach(item => {
                            let included = false // 数据的条件值（筛选条件key）是否包含在用户填写的筛选条件里
                            let excluded = false // 数据的条件值（排除条件key）是否包含在用户填写的排除条件里

                            if (validFilters.length === 0) {
                                included = true
                            } else {
                                Object.keys(filterObj).some(filterKey => {
                                    if (filterObj[filterKey].includes(item[filterKey])) {
                                        included = true
                                        return true
                                    }
                                })
                            }
                            
                            if (included) {
                                Object.keys(excludeObj).some(excludeKey => {
                                    if (excludeObj[excludeKey].includes(item[excludeKey])) {
                                        excluded = true
                                        return true
                                    }
                                })
                            }

                            if (included && !excluded) { // 数据同时满足条件值被包含在筛选条件且不被包含在排除条件里，才添加ip
                                hostLists.push(item)
                            }
                        })
                    }
                })
                return hostLists
            },
            /**
             * 条件数据转换为对象，整合相同条件的 value, 减少条件遍历次数
             *
             * @param {Array} fields 条件数组 [{field: 'name', value: ['aaa']}, {field: 'bk_sn', value:['ccc']}...]
             *
             * @return {Object} 条件对象 {name:['aaa'], bk_sn: ['ccc']...}
             */
            transFieldArrToObj (fields) {
                return fields.reduce((acc, cur, index) => {
                    const { field, value } = cur
                    if (field !== '' && value.length > 0) {
                        if (acc.hasOwnProperty(field)) {
                            acc[field] = acc[field].concat(value)
                        } else {
                            acc[field] = [...value]
                        }
                    }

                    return acc
                }, {})
            }
        }
    }
</script>
<style lang="scss" scoped>
    .set-form {
        margin-bottom: 20px;
        vertical-align: middle;
        overflow: hidden;
        .title {
            display: inline-block;
            height: 32px;
            line-height: 32px;
            font-size: 14px;
            color: #313238;
        }
        .btns {
            float: right;
            margin-top: 4px;
        }
    }
    .module-form {
        border-radius: 2px;
        .module-wrapper {
            margin-top: 20px;
            min-height: 40px;
        }
        .bk-form {
            /deep/ .bk-form-item {
                .bk-label {
                    color: #313138;
                    font-size: 12px;
                }
            }
        }
    }
    .module-empty {
        padding-top: 185px;
    }
    .save-screen {
        position: absolute;
        top: 0;
        left: 620px;
    }
</style>
<style lang="scss">
    .common-bk-select-hide-option {
        .bk-option,
        .bk-select-empty {
            display: none;
        }
    }
    .bk-form-content {
        /deep/ .el-autocomplete,
            .el-input{
                height: 30px;
                width: 100%;
                /deep/.el-input__inner {
                        height: 30px !important;
                        border: 1px solid #c4c6cc;
                }
        }
        
    }
    
</style>
