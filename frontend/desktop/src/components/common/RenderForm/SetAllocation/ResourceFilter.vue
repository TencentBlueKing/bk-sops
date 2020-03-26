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
    <div class="resource-filter">
        <header class="set-form">
            <span class="title">{{ i18n.title }}</span>
            <div class="btns">
                <bk-button theme="primary" :loading="pending.host" @click="onConfigConfirm">{{ i18n.confirm }}</bk-button>
                <bk-button
                    theme="default"
                    @click="$emit('update:showFilter', false)">
                    {{ i18n.cancel }}
                </bk-button>
            </div>
        </header>
        <section class="module-form">
            <bk-form ref="setForm" :model="formData" :rules="setRules">
                <bk-form-item :label="i18n.cluster" :required="true" property="clusterCount">
                    <bk-input v-model="formData.clusterCount" type="number" :min="0"></bk-input>
                </bk-form-item>
                <bk-form-item :label="i18n.set" :required="true" property="set">
                    <bk-select
                        ref="setSelect"
                        :value="formData.set[0] && formData.set[0].id"
                        :clearable="false"
                        :loading="pending.set"
                        ext-popover-cls="common-bk-select-hide-option">
                        <template v-if="formData.set.length > 0">
                            <bk-option
                                v-for="item in formData.set"
                                :key="item.id"
                                :id="item.id"
                                :name="item.label">
                            </bk-option>
                        </template>
                        <el-tree
                            ref="setTree"
                            node-key="id"
                            default-expand-all
                            show-checkbox
                            check-strictly
                            :data="setList"
                            :props="{
                                disabled: setLeafDisabled
                            }"
                            @check="onSetSelect">
                        </el-tree>
                    </bk-select>
                </bk-form-item>
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
            </bk-form>
            <div class="module-wrapper" v-bkloading="{ isLoading: pending.module, opacity: 1 }">
                <bk-tab
                    v-if="moduleList.length > 0 && formData.modules.length > 0"
                    class="module-tabs"
                    :active.sync="activeTab">
                    <bk-tab-panel
                        v-for="(moduleItem, moduleIndex) in moduleList"
                        :key="moduleItem.name"
                        :name="moduleItem.bk_module_id"
                        :label="moduleItem.bk_module_name">
                        <bk-form :model="formData.modules[moduleIndex]" ref="moduleTab" :rules="moduleRules">
                            <bk-form-item :label="i18n.resourceNum" :required="true" property="count">
                                <bk-input v-model="formData.modules[moduleIndex].count" type="number" :min="0"></bk-input>
                            </bk-form-item>
                            <bk-form-item :label="i18n.reuse" property="isReuse">
                                <bk-switcher
                                    v-model="formData.modules[moduleIndex].isReuse"
                                    theme="primary"
                                    size="min"
                                    @change="onChangeReuse($event, formData.modules[moduleIndex])">
                                </bk-switcher>
                            </bk-form-item>
                            <bk-form-item
                                v-show="formData.modules[moduleIndex].isReuse"
                                property="reuse"
                                :label="i18n.reuseModule"
                                :required="true">
                                <bk-select v-model="formData.modules[moduleIndex].reuse">
                                    <bk-option
                                        v-for="item in canReusedModules"
                                        :key="item.bk_module_id"
                                        :name="item.bk_module_name"
                                        :id="item.bk_module_id">
                                    </bk-option>
                                </bk-select>
                            </bk-form-item>
                            <div class="condition-wrapper" v-if="!formData.modules[moduleIndex].isReuse">
                                <select-condition
                                    ref="filterConditions"
                                    :label="i18n.filter"
                                    :condition-fields="conditions"
                                    :conditions="formData.modules[moduleIndex].filters"
                                    @change="updateCondition('filters', $event, formData.modules[moduleIndex])">
                                </select-condition>
                                <select-condition
                                    ref="excludeConditions"
                                    :label="i18n.exclude"
                                    :condition-fields="conditions"
                                    :conditions="formData.modules[moduleIndex].excludes"
                                    @change="updateCondition('excludes', $event, formData.modules[moduleIndex])">
                                </select-condition>
                            </div>
                        </bk-form>
                    </bk-tab-panel>
                </bk-tab>
            </div>
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
        name: 'ResourceFilter',
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
            const { set_count, host_resources, module_detail } = tools.deepClone(this.config)
            const $this = this
            return {
                formData: {
                    clusterCount: set_count,
                    set: [],
                    resource: host_resources,
                    modules: module_detail
                },
                setRules: {
                    clusterCount: [
                        {
                            required: true,
                            message: gettext('必选项'),
                            trigger: 'blur'
                        }
                    ],
                    set: [
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
                moduleRules: {
                    count: [{
                        required: true,
                        message: gettext('必填项'),
                        trigger: 'blur'
                    }],
                    reuse: [{
                        validator (val) {
                            if ($this.formData.modules[$this.validatingTabIndex].isReuse
                                && $this.formData.modules[$this.validatingTabIndex].reuse === ''
                            ) {
                                return false
                            }
                            return true
                        },
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
                    set: false,
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
                    exclude: gettext('主机排除条件')
                }
            }
        },
        computed: {
            // 模块可引用列表，去掉相互引用，暂未处理三层或更多层的循环引用
            canReusedModules (id) {
                return this.moduleList.filter((item, index) => {
                    return item.bk_module_id !== this.activeTab && this.formData.modules[index].reuse !== this.activeTab
                })
            }
        },
        async mounted () {
            this.getSetTopo()
            this.getResource()
            this.getCondition()
            if (this.config.set_template_id !== '') { // 筛选面板编辑时，组装模块列表数据
                await this.getModule(this.config.set_template_id)
                this.moduleList.forEach((item, index) => {
                    const moduleItem = this.config.module_detail.find(md => md.id === item.bk_module_id)
                    if (moduleItem) {
                        const { host_count: count, name, id, reuse_module: reuse, filters, excludes } = tools.deepClone(moduleItem)
                        const isReuse = reuse !== ''
                        const moduleData = {
                            count, name, id, isReuse, reuse, filters, excludes
                        }
                        this.$set(this.formData.modules, index, moduleData)
                    } else {
                        this.$set(this.formData.modules, index, {
                            count: 0,
                            name: item.bk_module_name,
                            id: item.bk_module_id,
                            isReuse: false,
                            reuse: '',
                            filters: [],
                            excludes: []
                        })
                    }
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
            async getSetTopo () {
                try {
                    this.pending.set = true
                    const resp = await this.getCCSearchTopoSet({
                        url: this.urls['cc_search_topo_set']
                    })
                    if (resp.result) {
                        this.setList = resp.data
                        if (this.config.set_template_id !== '') { // 筛选面板编辑时，由集群id筛选出集群名称
                            this.$refs.setTree && this.$refs.setTree.setCheckedKeys([this.config.set_template_id])
                            const checkedName = this.filterSetName(this.config.set_template_id, resp.data)
                            this.formData.set = [{
                                id: this.config.set_template_id,
                                label: checkedName
                            }]
                        }
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.set = false
                }
            },
            async getResource () {
                try {
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
            async getModule (id) {
                const setId = id.replace(/^set_/, '')
                try {
                    this.pending.set = true
                    const params = {
                        url: this.urls['cc_search_module'],
                        bk_set_id: setId
                    }
                    const resp = await this.getCCSearchModule(params)
                    if (resp.result) {
                        this.moduleList = resp.data.info
                        this.formData.modules = []
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.set = false
                }
            },
            async getCondition () {
                try {
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
            async onSetSelect (checked) {
                this.formData.set = [checked]
                this.$refs.setTree.setCheckedKeys([checked.id])
                this.$refs.setSelect.close()
                await this.getModule(checked.id)
                this.moduleList.forEach((item, index) => {
                    this.$set(this.formData.modules, index, {
                        count: 0,
                        name: item.bk_module_name,
                        id: item.bk_module_id,
                        isReuse: false,
                        reuse: '',
                        filters: [],
                        excludes: []
                    })
                })
            },
            // 由集群ID递归查找集群名称
            filterSetName (id, list) {
                let name
                list.some(item => {
                    if (item.id === id) {
                        name = item.label
                        return true
                    } else if (item.children && item.children.length > 0) {
                        name = this.filterSetName(id, item.children)
                    }
                })
                return name
            },
            // 集群模板只有 id 以 "set_" 开头的节点可选
            setLeafDisabled (data) {
                return !data.id.startsWith('set_')
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
            onResourceSelect (checked, data) {
                const checkedNodes = data.checkedNodes
                if (checked.children && checked.children.length > 0) {
                    this.unCheckChildrenNodes(checked, checkedNodes)
                }
                this.formData.resource = [{
                    id: checked.id,
                    label: checked.label
                }]
                this.$refs.resourceTree.setCheckedNodes(checkedNodes)
            },
            onChangeReuse (val, data) {
                if (val) {
                    data.filters = []
                    data.excludes = []
                } else {
                    data.reuse = ''
                }
            },
            updateCondition (type, value, data) {
                data[type] = value
            },
            // 点击确定，校验表单，提交数据
            onConfigConfirm () {
                if (this.pending.host) {
                    return
                }

                // 检查模块复用是否有循环引用，a->b,b->c,c->a
                let cycleCiting = false
                let cycled = []
                const passedModule = {}
                this.formData.modules.some(md => {
                    if (md.isReuse) {
                        if (passedModule.hasOwnProperty(md.reuse)) {
                            cycleCiting = true
                            cycled = [passedModule[md.reuse], md.name]
                            return true
                        } else {
                            passedModule[md.id] = md.name
                        }
                    }
                })
                // 节点循环引用退出保存，弹出提示
                if (cycleCiting) {
                    errorHandler({
                        message: gettext('模块') + cycled.join(',') + gettext('存在循环引用')
                    }, this)
                    return
                }

                this.$refs.setForm.validate().then(async validator => {
                    let tabValid = true
                    if (this.$refs.moduleTab && this.$refs.moduleTab.length) {
                        const len = this.$refs.moduleTab.length
                        for (let i = 0; i < len; i++) {
                            this.validatingTabIndex = i
                            try {
                                await this.$refs.moduleTab[i].validate()
                            } catch (error) {
                                tabValid = false
                            }
                        }
                    }

                    if (tabValid) {
                        this.getHostsAndSave()
                    } else {
                        errorHandler({ message: gettext('参数错误，请检查模块表单项') }, this)
                    }
                })
            },
            // 保存资源筛选面板的表单数据，向父级同步
            async getHostsAndSave () {
                const { clusterCount, modules, resource, set } = this.formData

                try {
                    this.pending.host = true
                    const fields = []
                    modules.forEach(md => {
                        md.filters.forEach(item => {
                            if (item.field !== '' && !fields.includes(item.field)) {
                                fields.push(item.field)
                            }
                        })
                        md.excludes.forEach(item => {
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
                    const moduleDetail = modules.map(item => {
                        const { count, name, id, reuse, filters, excludes } = item
                        // 取有效筛选、排除条件，不做校验（和 ip 选择器有区别，这里多个 tab 有多个相同 refs）
                        const validFilters = filters.filter(item => item.filed !== '' && item.value.length > 0)
                        const validExclude = excludes.filter(item => item.filed !== '' && item.value.length > 0)

                        return {
                            name,
                            id,
                            filters: validFilters,
                            excludes: validExclude,
                            host_count: count,
                            reuse_module: reuse
                        }
                    })
                    const config = {
                        set_count: clusterCount,
                        set_template_id: set[0].id,
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
             * 根据接口返回的全量 host 数据，筛选出对应模块的 host 值
             * host 值需要同时满足筛选条件和排除条件
             * 非复用模块间主机不能重复，先计算所有满足模块条件的主机，计算所需主机数与满足条件主机的比值，值大的优先取
             * 模块复用时，取其复用的模块主机数据
             * 每个模块的 host 数量不能超过 moudule.count 设置
             *
             * @param {Array} data 全量的 host 数据
             *
             * @return {Object} 满足每个 module 设置条件的 host 值，格式: {gamserver: [xx.xx.x.x, x.x.x.xxx], ...}
             */
            filterModuleHost (data) {
                let fullMdHosts = [] // 所有满足各模块的主机数据
                const hosts = {} // 去重、按照实际数量截取的模块主机数据
                const reuseOthers = []
                const usedHosts = []
                this.formData.modules.forEach(md => {
                    const { filters, excludes, name, isReuse } = md
                    const validFilters = filters.filter(item => item.filed !== '' && item.value.length > 0)
                    const validExclude = excludes.filter(item => item.filed !== '' && item.value.length > 0)
                    let list = []

                    if (isReuse) {
                        reuseOthers.push(md)
                    } else { // 未复用其他模块主机，则计算本模块数据
                        if (validFilters.length === 0 && validExclude.length === 0) { // 筛选条件和排序条件为空，按照设置的主机数截取
                            list = data.map(d => d.bk_host_innerip)
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
                                    list.push(item.bk_host_innerip)
                                }
                            })
                        }
                        fullMdHosts.push({
                            name,
                            list,
                            percent: data.length > 0 ? list.length / data.length : 0
                        })
                    }
                })
                fullMdHosts = fullMdHosts.sort((a, b) => b.percent - a.percent)
                fullMdHosts.forEach(item => {
                    const md = this.formData.modules.find(m => m.name === item.name)
                    hosts[item.name] = []
                    item.list.forEach(h => {
                        if (!usedHosts.includes(h) && hosts[item.name].length < md.count) {
                            hosts[item.name].push(h)
                            usedHosts.push(h)
                        }
                    })
                })

                reuseOthers.forEach(md => { // 复用其他模块主机数据，数量取按照本模块设置数
                    let citedModule = this.formData.modules.find(item => item.id === md.reuse)
                    const citePath = [md]
                    while (!hosts[citedModule.name]) {
                        citePath.unshift(Object.assign({}, citedModule))
                        citedModule = this.formData.modules.find(item => item.id === citedModule.reuse)
                    }
                    citePath.forEach(item => {
                        const cModule = this.formData.modules.find(cm => cm.id === item.reuse)
                        hosts[item.name] = hosts[cModule.name].slice(0, item.count)
                    })
                })

                return hosts
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
        }
    }
    .module-form {
        padding: 20px;
        border-radius: 2px;
        .module-wrapper {
            margin-top: 20px;
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
</style>
<style lang="scss">
    .common-bk-select-hide-option {
        .bk-option,
        .bk-select-empty {
            display: none;
        }
    }
</style>
