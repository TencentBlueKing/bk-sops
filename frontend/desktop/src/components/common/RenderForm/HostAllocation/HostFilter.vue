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
    <div class="resource-filter">
        <header class="host-form">
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
            <bk-form ref="hostForm" :model="formData" :rules="hostRules">
                <!--筛选方案-->
                <bk-form-item :label="i18n.screenScheme" property="scheme">
                    <div class="scheme-select">
                        <bk-select :value="formData.schemeValue" :loading="pending.scheme" @selected="onSchemeSelect">
                            <bk-option
                                v-for="scheme in schemeListArr"
                                :key="scheme.id"
                                :id="scheme.id"
                                :name="scheme.name">
                            </bk-option>
                        </bk-select>
                        <bk-button theme="success" size="small" class="scheme-save-btn" @click="isSchemeDialogShow = true">{{ i18n.saveScheme }}</bk-button>
                    </div>
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
                        <bk-big-tree
                            ref="resourceTree"
                            show-checkbox
                            :height="216"
                            :check-strictly="false"
                            :options="{ nameKey: 'label' }"
                            :default-expanded-nodes="defaultExpandNodes"
                            :data="resourceList"
                            @check-change="onResourceSelect">
                        </bk-big-tree>
                    </bk-select>
                </bk-form-item>
                <!--主机筛选条件-->
                <div class="condition-wrapper">
                    <select-condition
                        ref="filterConditions"
                        :label="i18n.filterExcludeTitle"
                        :condition-fields="conditions"
                        :conditions="formData.host_filter_list"
                        @change="updateCondition($event)">
                    </select-condition>
                </div>
            </bk-form>
        </section>
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="i18n.screenScheme"
            :loading="pending.saveScheme"
            :value="isSchemeDialogShow"
            @confirm="onSchemeConfirm"
            @cancel="isSchemeDialogShow = false">
            <bk-form ref="schemeForm" class="scheme-dialog" :model="schemeData" :rules="schemeNameRules">
                <bk-form-item property="name" :label="i18n.schemeName">
                    <bk-input v-model="schemeData.name" />
                    <div class="scheme-tip">{{ i18n.schemeTips }}</div>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>
<script >
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
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
                        host_count: 0,
                        host_screen_value: '',
                        host_resources: [],
                        host_filter_detail: []
                    }
                }
            },
            urls: {
                type: Object,
                default () {
                    return {}
                }
            },
            cols: {
                type: Array
            }
        },
        data () {
            const { host_count, host_resources, host_screen_value, host_filter_detail } = tools.deepClone(this.config)
            return {
                formData: {
                    clusterCount: host_count,
                    schemeValue: host_screen_value,
                    resource: host_resources,
                    // 传递给SelectCondition的所有数据
                    host_filter_list: host_filter_detail
                },
                // 用来做筛选排除的
                filterExcludeSet: {
                    filter: [],
                    exclude: []
                },
                schemeData: {
                    name: ''
                },
                schemeNameRules: {
                    name: [
                        {
                            required: true,
                            message: gettext('必选项'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: gettext('方法名称不能超过50个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                hostRules: {
                    clusterCount: [
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
                    ]
                },
                resourceList: [], // 主机资源所属 tree
                defaultExpandNodes: [],
                conditions: [],
                pending: {
                    scheme: false,
                    screen: false,
                    resource: false,
                    condition: false,
                    host: false,
                    saveScheme: false
                },
                i18n: {
                    title: gettext('资源筛选'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消'),
                    resource: gettext('主机资源所属'),
                    resourceNum: gettext('主机数量'),
                    filterExcludeTitle: gettext('筛选条件和排除条件'),
                    save: gettext('保存'),
                    screenScheme: gettext('筛选方案'),
                    schemeName: gettext('方案名称'),
                    schemeTips: gettext('修改名称会新建方案记录'),
                    saveScheme: gettext('保存筛选方案')
                },
                schemeListArr: [],
                isSchemeDialogShow: false
            }
        },
        async mounted () {
            this.getSetTopo()
            this.getResource()
            this.getCondition()
        },
        methods: {
            ...mapActions([
                'getHostInCC',
                'getCCSearchTopoResource',
                'getCCSearchObjAttrHost'
            ]),
            ...mapActions('task/', [
                'configProgramList',
                'saveResourceScheme',
                'createResourceScheme',
                'getResourceConfig'
            ]),
            // 获取筛选方案数据
            async getSetTopo () {
                try {
                    this.pending.scheme = true
                    const resp = await this.configProgramList('host')
                    if (resp.result) {
                        this.schemeListArr = resp.data
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.scheme = false
                }
            },
            // 筛选方案列表选中事件
            onSchemeSelect (id) {
                const scheme = this.schemeListArr.find(item => item.id === id)
                const { host_resources, module_detail } = JSON.parse(scheme.data)
                let hostCount
                const hostFilterList = []
                module_detail.forEach(item => {
                    const { clusterCount, host_filter_list } = item
                    hostCount = clusterCount
                    if (host_filter_list.length) {
                        host_filter_list.forEach(filterItem => {
                            hostFilterList.push({
                                type: filterItem.type,
                                field: filterItem.field,
                                value: filterItem.value
                            })
                        })
                    }
                })
                this.formData = {
                    clusterCount: hostCount,
                    resource: host_resources,
                    host_filter_list: hostFilterList
                }
                this.formData.schemeValue = scheme.id
            },
            // 保存或创建筛选方案
            onSchemeConfirm () {
                if (this.pending.saveScheme) {
                    return
                }
                this.$refs.schemeForm.validate().then(async result => {
                    if (result) {
                        this.pending.saveScheme = true
                        let resp
                        try {
                            const scheme = this.schemeListArr.find(item => item.name === this.schemeData.name)
                            const configData = this.getConfigData()
                            configData.config_type = 'host'
                            const params = {
                                url: `api/v3/resource_config/`,
                                data: {
                                    project_id: $.context.project ? $.context.project.id : '',
                                    config_type: 'host',
                                    name: this.schemeData.name
                                }
                            }
                            if (scheme) {
                                configData.id = scheme.id
                                configData.name = scheme.name
                                params.data.data = JSON.stringify(configData)
                                resp = await this.saveResourceScheme(params)
                            } else {
                                configData.name = this.schemeData.name
                                params.data.data = JSON.stringify(configData)
                                resp = await this.createResourceScheme(params)
                            }
                            if (resp.result) {
                                this.isSchemeDialogShow = false
                                this.schemeData.name = ''
                                await this.getSetTopo()
                                this.formData.schemeValue = resp.data.id
                            }
                        } catch (e) {
                            console.log(e)
                        } finally {
                            this.pending.saveScheme = false
                        }
                    }
                })
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
                        if (Array.isArray(resp.data) && resp.data.length > 0) {
                            this.defaultExpandNodes = [resp.data[0].id]
                        }
                        this.$nextTick(() => {
                            if (this.formData.resource.length > 0) {
                                const keys = this.formData.resource.map(item => item.id)
                                if (this.$refs.resourceTree) {
                                    this.$refs.resourceTree.setChecked(keys, { checked: true })
                                    this.setNodesDefaultDisabled() // tips：tree 组件配置节点 disabled、checked 属性不生效，需手动设置组件修复
                                }
                            }
                        })
                    }
                } catch (e) {
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.condition = false
                }
            },
            
            // 主机资源所属，选中父节点后子节点不可选
            hostResourceDisabled (data, node) {
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
            // 由集群ID递归查找集群名称
            filterSetName (id, list) {
                let name = ''
                list.some(item => {
                    if (item.id === id) {
                        name = item.label
                        return true
                    } else if (item.children && item.children.length > 0) {
                        const val = this.filterSetName(id, item.children)
                        if (val) {
                            name = val
                            return true
                        }
                    }
                })
                return name
            },
            /**
             * 设置默认被禁用的节点
             */
            setNodesDefaultDisabled () {
                let defaultDisabledIds = []
                this.formData.resource.forEach(item => {
                    const node = this.$refs.resourceTree.getNodeById(item.id)
                    if (node.children && node.children.length > 0) {
                        defaultDisabledIds = defaultDisabledIds.concat(this.traverseNodesToList(node.children))
                    }
                })
                this.$refs.resourceTree.setDisabled(defaultDisabledIds, { disabled: true })
            },
            /**
             * 遍历获取子节点列表
             */
            traverseNodesToList (nodes) {
                let list = []
                nodes.forEach(item => {
                    list.push(item.id)
                    if (item.children && item.children.length > 0) {
                        list = list.concat(this.traverseNodesToList(item.children))
                    }
                })
                return list
            },
            // 主机资源所属，选中父节点后取消所有子节点的选中态
            changeChildrenNodeState (node, checkedList, isChecked) {
                node.children.forEach(item => {
                    const index = checkedList.findIndex(id => id === item.id)
                    if (index > -1) {
                        checkedList.splice(index, 1)
                        this.$refs.resourceTree.setChecked(item.id, { checked: false })
                    }
                    this.$refs.resourceTree.setDisabled(item.id, { disabled: isChecked })
                    if (item.children && item.children.length > 0) {
                        this.changeChildrenNodeState(item, checkedList, isChecked)
                    }
                })
            },
            // 清空所选主机资源
            onResourceClear () {
                this.formData.resource = []
                this.$refs.resourceTree.setData(this.resourceList)
            },
            // 主机资源所属节点点击事件
            onResourceSelect (selectedNodes, node) {
                const checkedList = selectedNodes.slice(0)
                const isChecked = selectedNodes.includes(node.id)
                if (node.children && node.children.length) {
                    this.changeChildrenNodeState(node, checkedList, isChecked)
                }
                this.formData.resource = checkedList.map(id => {
                    const label = this.filterSetName(id, this.resourceList)
                    return { id, label }
                })
                this.$refs.resourceTree.setChecked(checkedList, { checked: true })
            },
            // 主机筛选条件change事件
            updateCondition (value) {
                this.formData.host_filter_list = value
            },
            // 点击确定，校验表单，提交数据
            onConfigConfirm () {
                if (this.pending.host) {
                    return
                }
                const newFilterList = []
                this.formData.host_filter_list.forEach(item => {
                    if (item.field !== '' && item.value.length > 0) {
                        newFilterList.push({
                            type_val: item.type === 'filter' ? 1 : 0,
                            name: item.field,
                            value: item.value
                        })
                    }
                })
                newFilterList.forEach(item => {
                    const type = item.type_val === 1 ? 'filter' : 'exclude'
                    this.filterExcludeSet[type].push(item)
                })
                this.$refs.hostForm.validate().then(async validator => {
                    this.getHostsAndSave()
                })
            },
            // 保存资源筛选面板的表单数据，向父级同步
            async getHostsAndSave () {
                const { clusterCount, resource, schemeValue } = this.formData
                try {
                    this.pending.host = true
                    const fields = []
                    for (const k in this.filterExcludeSet) {
                        this.filterExcludeSet[k].forEach(item => {
                            if (item.name !== '' && !fields.includes(item.name)) {
                                fields.push(item.name)
                            }
                        })
                    }
                    this.cols.forEach(item => {
                        const tagCode = item.config.tag_code
                        if (tagCode !== 'tb_btns') {
                            fields.push(tagCode)
                        }
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
                    const eligibleHosts = this.filterHost(hostData.data)
                    const { filter, exclude } = this.filterExcludeSet
                    const oldConditionsArr = [...filter, ...exclude]
                    const newConditionsArr = oldConditionsArr.map(item => {
                        return {
                            type: item.type_val === 1 ? 'filter' : 'exclude',
                            field: item.name,
                            value: item.value
                        }
                    })
                    const config = {
                        host_count: clusterCount,
                        host_screen_value: schemeValue,
                        host_resources: resource,
                        host_filter_detail: newConditionsArr
                    }
                    this.$emit('update', config, eligibleHosts)
                    this.$emit('update:showFilter', false)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.host = false
                }
            },
            /**
             * 根据接口返回的全量 host 数据，筛选出符合条件的 host 值
             * host 值需要同时满足筛选条件和排除条件
             *
             * @param {Array} data 全量的 host 数据
             *
             * @return {Object} 符合筛选条件的 host 值，格式: [{...}, ...]
             */
            filterHost (data) {
                let hostLists = [] // 所有满足主机数据
                const { filter, exclude } = this.filterExcludeSet
                const validFilters = filter.filter(item => item.name !== '' && item.value.length > 0)
                const validExclude = exclude.filter(item => item.name !== '' && item.value.length > 0)
                // 筛选条件和排序条件为空，按照设置的主机数截取
                if (validFilters.length === 0 && validExclude.length === 0) {
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
            },
            // 将本地表单编辑数据格式转换为接口所需数据格式
            getConfigData () {
                const { clusterCount, resource, host_filter_list } = this.formData
                const moduleDetail = []
                moduleDetail.push({
                    clusterCount,
                    host_filter_list
                })
                return {
                    host_resources: resource,
                    module_detail: moduleDetail
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .host-form {
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
    .scheme-select {
        position: relative;
        /deep/ .bk-select {
            margin-right: 150px;
        }
        .scheme-save-btn {
            position: absolute;
            right: 0;
            top: 3px;
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
    .scheme-dialog {
        padding: 30px;
        /deep/ .bk-form-content {
            margin-right: 60px;
        }
        .scheme-tip {
            font-size: 12px;
            color: #ffb400;
        }
    }
    /deep/ .bk-big-tree-node .node-content {
        font-size: 12px;
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
