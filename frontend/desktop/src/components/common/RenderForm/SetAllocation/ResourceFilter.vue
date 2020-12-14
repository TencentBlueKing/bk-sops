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
                <bk-button
                    theme="primary"
                    size="small"
                    :disabled="pending.set || pending.resource || pending.module"
                    :loading="pending.host"
                    @click="onConfigConfirm">
                    {{ i18n.confirm }}
                </bk-button>
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
                <!-- 筛选方案 -->
                <bk-form-item :label="i18n.scheme" property="scheme">
                    <div class="scheme-select">
                        <bk-select :value="formData.scheme" :loading="pending.scheme" @selected="onSchemeSelect">
                            <bk-option
                                v-for="scheme in schemes"
                                :key="scheme.id"
                                :id="scheme.id"
                                :name="scheme.name">
                            </bk-option>
                        </bk-select>
                        <bk-button theme="success" size="small" class="scheme-save-btn" @click="isSchemeDialogShow = true">{{ i18n.saveScheme }}</bk-button>
                    </div>
                </bk-form-item>
                <!-- 集群个数 -->
                <bk-form-item :label="i18n.cluster" :required="true" property="clusterCount">
                    <bk-input v-model="formData.clusterCount" type="number" :min="0"></bk-input>
                </bk-form-item>
                <!-- 集群模板 -->
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
                        <bk-big-tree
                            ref="setTree"
                            default-expand-all
                            show-checkbox
                            :height="216"
                            :check-strictly="false"
                            :disable-strictly="false"
                            :data="setList"
                            :options="{ nameKey: 'label' }"
                            @check-change="onSetSelect">
                        </bk-big-tree>
                    </bk-select>
                </bk-form-item>
                <!-- 主机资源所属 -->
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
                <!-- 互斥属性 -->
                <bk-form-item :label="i18n.exclusive" property="muteAttribute">
                    <bk-select v-model="formData.muteAttribute" @clear="onMuteAttributeClear">
                        <bk-option
                            v-for="condition in conditions"
                            :key="condition.id"
                            :id="condition.id"
                            :name="condition.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <!-- 均摊属性 -->
                <bk-form-item :label="i18n.shareEqually" property="shareEqually">
                    <bk-select v-model="formData.shareEqually">
                        <bk-option
                            v-for="condition in conditions"
                            :key="condition.id"
                            :id="condition.id"
                            :name="condition.name">
                        </bk-option>
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
                            <!-- 主机数量 -->
                            <bk-form-item :label="i18n.resourceNum" :required="true" property="count">
                                <bk-input v-model="formData.modules[moduleIndex].count" type="number" :min="0"></bk-input>
                            </bk-form-item>
                            <!-- 筛选方式 -->
                            <bk-form-item :label="i18n.selectMethod" property="selectMethod">
                                <bk-radio-group v-model="formData.modules[moduleIndex].selectMethod" class="bk-radio-group">
                                    <bk-radio :value="0">{{ i18n.default }}</bk-radio>
                                    <bk-radio :value="1">{{ i18n.manual }}</bk-radio>
                                    <bk-radio :value="2">{{ i18n.reuseModule }}</bk-radio>
                                </bk-radio-group>
                            </bk-form-item>
                            <template v-if="formData.modules[moduleIndex].selectMethod === 0">
                                <!-- 互斥方案 -->
                                <bk-form-item :label="i18n.muteMethod" property="muteMethod">
                                    <bk-radio-group v-model="formData.modules[moduleIndex].muteMethod" class="bk-radio-group">
                                        <bk-radio :value="0" :disabled="!formData.muteAttribute">{{ i18n.notMute }}</bk-radio>
                                        <bk-radio :value="1" :disabled="!formData.muteAttribute">{{ i18n.innerMute }}</bk-radio>
                                        <bk-radio :value="2" :disabled="!formData.muteAttribute">{{ i18n.moduleMute }}</bk-radio>
                                    </bk-radio-group>
                                </bk-form-item>
                                <!-- 互斥模块 -->
                                <bk-form-item v-if="formData.modules[moduleIndex].muteMethod === 2" :label="i18n.muteModule" property="muteModule" :required="true">
                                    <bk-select v-model="formData.modules[moduleIndex].muteModules" multiple>
                                        <bk-option
                                            v-for="item in canMuteModules"
                                            :key="item.bk_module_id"
                                            :name="item.bk_module_name"
                                            :id="item.bk_module_id">
                                        </bk-option>
                                    </bk-select>
                                    <div class="mute-module-tip">{{ i18n.muteModuleTips }}</div>
                                </bk-form-item>
                                <!-- 筛选条件 -->
                                <div class="condition-wrapper">
                                    <select-condition
                                        ref="filterConditions"
                                        :label="i18n.condition"
                                        :condition-fields="conditions"
                                        :conditions="formData.modules[moduleIndex].hostFilterList"
                                        @change="updateCondition($event, formData.modules[moduleIndex])">
                                    </select-condition>
                                </div>
                            </template>
                            <!-- 自定义ip -->
                            <bk-form-item
                                v-show="formData.modules[moduleIndex].selectMethod === 1"
                                :label="'ip' + i18n.list"
                                property="customIpList">
                                <bk-input
                                    type="textarea"
                                    :rows="10"
                                    :placeholder="i18n.ipPlaceholder"
                                    v-model="formData.modules[moduleIndex].customIpList">
                                </bk-input>
                            </bk-form-item>
                            <!-- 复用模块 -->
                            <bk-form-item
                                v-show="formData.modules[moduleIndex].selectMethod === 2"
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
                        </bk-form>
                    </bk-tab-panel>
                </bk-tab>
            </div>
        </section>
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="i18n.scheme"
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
            const { set_count, host_resources, mute_attribute = '', shareEqually = '', module_detail } = tools.deepClone(this.config)
            const $this = this
            return {
                formData: {
                    scheme: '',
                    clusterCount: set_count,
                    set: [],
                    resource: host_resources,
                    muteAttribute: mute_attribute,
                    shareEqually: shareEqually,
                    modules: module_detail
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
                    customIpList: [{
                        validator (val) {
                            if ($this.formData.modules[$this.validatingTabIndex].selectMethod === 1) {
                                const ipPattern = /^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$/ // ip 地址正则规则
                                const ipString = $this.formData.modules[$this.validatingTabIndex].customIpList
                                const arr = ipString.split(/[\,|\n|\uff0c]/) // 按照中英文逗号、换行符分割
                                return arr.every(item => {
                                    if (item.trim()) {
                                        return ipPattern.test(item)
                                    }
                                    return true
                                })
                            }
                            return true
                        },
                        message: gettext('IP地址不合法'),
                        trigger: 'blur'
                    }],
                    reuse: [{
                        validator (val) {
                            if ($this.formData.modules[$this.validatingTabIndex].selectMethod === 2
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
                schemes: [], // 筛选方案列表
                setList: [], // 集群模板 tree
                resourceList: [], // 主机资源所属 tree
                defaultExpandNodes: [],
                moduleList: [], // 集群下模块列表
                activeTab: '',
                conditions: [],
                isSchemeDialogShow: false,
                pending: {
                    scheme: false,
                    saveScheme: false,
                    set: false,
                    resource: false,
                    module: false,
                    condition: false,
                    host: false
                },
                i18n: {
                    title: gettext('资源筛选'),
                    scheme: gettext('筛选方案'),
                    schemeName: gettext('方案名称'),
                    schemeTips: gettext('修改名称会新建方案记录'),
                    saveScheme: gettext('保存筛选方案'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消'),
                    cluster: gettext('集群个数'),
                    set: gettext('集群模板'),
                    resource: gettext('主机资源所属'),
                    exclusive: gettext('互斥属性'),
                    shareEqually: gettext('均摊属性'),
                    resourceNum: gettext('主机数量'),
                    selectMethod: gettext('筛选方式'),
                    default: gettext('默认'),
                    manual: gettext('手动指定'),
                    list: gettext('列表'),
                    ipPlaceholder: gettext('请输入IP，多个以逗号或者换行符隔开'),
                    reuse: gettext('复用其他模块机器'),
                    reuseModule: gettext('复用模块'),
                    muteMethod: gettext('互斥方案'),
                    notMute: gettext('不互斥'),
                    innerMute: gettext('模块内互斥'),
                    moduleMute: gettext('模块间互斥'),
                    muteModuleTips: gettext('如果互斥模块复用本模块，则该互斥约束失效'),
                    muteModule: gettext('互斥模块'),
                    condition: gettext('筛选条件和排除条件')
                }
            }
        },
        computed: {
            canMuteModules () {
                return this.moduleList.filter((item, index) => {
                    return item.bk_module_id !== this.activeTab
                })
            },
            // 模块可引用列表，去掉相互引用，暂未处理三层或更多层的循环引用
            canReusedModules () {
                return this.moduleList.filter((item, index) => {
                    return item.bk_module_id !== this.activeTab && this.formData.modules[index].reuse !== this.activeTab
                })
            }
        },
        async mounted () {
            this.gitResourceSchemes()
            this.getSetTopo()
            this.getResource()
            this.getCondition()
            if (this.config.set_template_id !== '') { // 筛选面板编辑时，组装模块列表数据
                await this.getModule(this.config.set_template_id)
                this.moduleList.forEach((item, index) => {
                    const moduleItem = this.config.module_detail.find(md => md.id === item.bk_module_id)

                    if (moduleItem) {
                        const {
                            id, name, host_count, reuse_module,
                            select_method, custom_ip_list, mute_method, mute_modules, host_filter_list, // v1 迁移后新增字段
                            filters, excludes // v1 迁移前存在的字段
                        } = tools.deepClone(moduleItem)
                        
                        let filterList = []
                        if (filters && excludes) { // filters、excludes 字段存在说明是 v1 迁移前的旧数据，需要兼容
                            filterList = filters.concat(excludes)
                        } else {
                            filterList = host_filter_list.map(item => {
                                return {
                                    type: item.type_val === 1 ? 'exclude' : 'filter',
                                    field: item.name,
                                    value: item.value
                                }
                            })
                        }

                        const moduleData = {
                            id,
                            name,
                            count: host_count,
                            selectMethod: select_method === undefined ? 0 : select_method,
                            reuse: reuse_module,
                            customIpList: custom_ip_list || '',
                            muteMethod: mute_method === undefined ? 0 : mute_method,
                            muteModules: mute_modules || [],
                            hostFilterList: filterList
                        }
                        this.$set(this.formData.modules, index, moduleData)
                    } else {
                        this.$set(this.formData.modules, index, {
                            id: item.bk_module_id,
                            name: item.bk_module_name,
                            count: 0,
                            selectMethod: 0,
                            reuse: '',
                            customIpList: '',
                            muteMethod: 0,
                            muteModules: [],
                            hostFilterList: []
                        })
                    }
                })
            }
        },
        methods: {
            ...mapActions([
                'getResourceConfig',
                'saveResourceScheme',
                'createResourceScheme',
                'getHostInCC',
                'getCCSearchTopoSet',
                'getCCSearchTopoResource',
                'getCCSearchModule',
                'getCCSearchObjAttrHost'
            ]),
            async gitResourceSchemes () {
                try {
                    this.pending.scheme = true
                    const resp = await this.getResourceConfig({
                        url: $.context.canSelectBiz() ? '' : `api/v3/resource_config/?project_id=${$.context.project.id}&config_type=set`
                    })
                    if (resp.result) {
                        this.schemes = resp.data
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.scheme = false
                }
            },
            async getSetTopo () {
                try {
                    if (!this.urls['cc_search_topo_set']) {
                        return
                    }
                    this.pending.set = true
                    const resp = await this.getCCSearchTopoSet({
                        url: this.urls['cc_search_topo_set']
                    })
                    if (resp.result) {
                        this.setList = resp.data
                        if (this.config.set_template_id !== '') { // 筛选面板编辑时，由集群id筛选出集群名称
                            const checkedName = this.filterSetName(this.config.set_template_id, resp.data)
                            this.formData.set = [{
                                id: this.config.set_template_id,
                                label: checkedName
                            }]
                        }
                        this.$nextTick(() => { // tips：tree 组件配置节点 disabled、checked 属性不生效，需手动设置组件修复
                            if (this.$refs.setTree) {
                                const bizNodes = this.setList.map(item => item.id)
                                this.$refs.setTree.setDisabled(bizNodes, { disabled: true })
                                this.$refs.setTree.setChecked(this.config.set_template_id, { checked: true })
                            }
                        })
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
                    if (!this.urls['cc_search_module']) {
                        return
                    }
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
            async onSchemeSelect (id) {
                const scheme = this.schemes.find(item => item.id === id)
                const { module_detail, mute_attribute, shareEqually, set_count, host_resources, set_template_id, set_template_name } = JSON.parse(scheme.data)
                const modules = module_detail.map(item => {
                    const { custom_ip_list, host_count, host_filter_list, id, mute_method, mute_modules, name, reuse_module, select_method } = item
                    return {
                        id,
                        name,
                        count: host_count,
                        selectMethod: select_method,
                        reuse: reuse_module,
                        customIpList: custom_ip_list,
                        muteMethod: mute_method,
                        muteModules: mute_modules,
                        hostFilterList: host_filter_list
                    }
                })
                await this.getModule(set_template_id)
                this.formData = {
                    clusterCount: set_count,
                    set: [{ id: set_template_id, label: set_template_name }],
                    resource: host_resources,
                    muteAttribute: mute_attribute,
                    shareEqually,
                    modules
                }
                this.schemeData.name = scheme.name
            },
            // 保存或创建筛选方案
            onSchemeConfirm () {
                if (this.pending.saveScheme) {
                    return
                }
                this.$refs.schemeForm.validate().then(async result => {
                    if (result) {
                        const isConfigFormValid = await this.validateConfigForm()
                        if (!isConfigFormValid) {
                            this.isSchemeDialogShow = false
                            return
                        }

                        this.pending.saveScheme = true
                        let resp
                        try {
                            const scheme = this.schemes.find(item => item.name === this.schemeData.name)
                            const configData = this.getConfigData()
                            configData.config_type = 'set'
                            const params = {
                                data: {
                                    project_id: $.context.project ? $.context.project.id : '',
                                    config_type: 'set',
                                    name: this.schemeData.name
                                }
                            }
                            if (scheme) {
                                configData.id = scheme.id
                                configData.name = scheme.name
                                params.url = $.context.canSelectBiz() ? '' : `api/v3/resource_config/${scheme.id}/`
                                params.data.data = JSON.stringify(configData)
                                resp = await this.saveResourceScheme(params)
                            } else {
                                configData.name = this.schemeData.name
                                params.url = $.context.canSelectBiz() ? '' : `api/v3/resource_config/`
                                params.data.data = JSON.stringify(configData)
                                resp = await this.createResourceScheme(params)
                            }
                            if (resp.result) {
                                this.isSchemeDialogShow = false
                                this.formData.scheme = resp.data.id
                                this.gitResourceSchemes()
                            } else {
                                errorHandler(resp, this)
                            }
                        } catch (error) {
                            errorHandler(error, this)
                        } finally {
                            this.pending.saveScheme = false
                        }
                    }
                })
            },
            async onSetSelect (ids, checked) {
                this.formData.set = [{ ...checked.data }]
                this.$refs.setSelect.close()
                this.$refs.setTree.removeChecked({ emitEvent: false })
                this.$refs.setTree.setChecked(checked.id, { checked: true })
                await this.getModule(checked.id)
                this.moduleList.forEach((item, index) => {
                    this.$set(this.formData.modules, index, {
                        count: 0,
                        name: item.bk_module_name,
                        id: item.bk_module_id,
                        isReuse: false,
                        reuse: '',
                        selectMethod: 0,
                        customIpList: '',
                        muteMethod: 0,
                        muteModules: [],
                        hostFilterList: []
                    })
                })
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
                        list = list.concat(this.getDisabledNodes(item.children))
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
            // 清除互斥属性后，所有模板默认的互斥方法置为不互斥
            onMuteAttributeClear () {
                this.formData.modules.forEach(item => {
                    item.muteMethod = 0
                })
            },
            // 设置筛选和排除条件
            updateCondition (conditions, moduleData) {
                moduleData.hostFilterList = conditions
            },
            // 点击确定，校验表单，提交数据
            async onConfigConfirm () {
                if (this.pending.host) {
                    return
                }

                try {
                    const isValid = await this.validateConfigForm()
                    if (isValid) {
                        this.getHostsAndSave()
                    }
                } catch (error) {
                    console.error(error)
                }
            },
            async validateConfigForm () {
                // 检查模块复用是否有循环引用，a->b,b->c,c->a
                let cycleCiting = false
                let cycled = []
                const passedModule = {}
                this.formData.modules.some(md => {
                    if (md.selectMethod === 2) {
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
                    return false
                }
                return this.$refs.setForm.validate().then(async result => {
                    if (!result) {
                        return false
                    }

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

                    if (!tabValid) {
                        errorHandler({ message: gettext('参数错误，请检查模块表单项') }, this)
                    } else {
                        return true
                    }
                })
            },
            // 保存资源筛选面板的表单数据，向父级同步
            async getHostsAndSave () {
                try {
                    this.pending.host = true
                    const fields = []
                    
                    this.formData.modules.forEach(md => { // 取出所有模块的筛选、排除条件字段
                        md.hostFilterList.forEach(item => {
                            if (item.field !== '' && !fields.includes(item.field)) {
                                fields.push(item.field)
                            }
                        })
                    })
                    if (this.formData.muteAttribute && !fields.includes(this.formData.muteAttribute)) {
                        fields.push(this.formData.muteAttribute)
                    }
                    if (this.formData.shareEqually && !fields.includes(this.formData.shareEqually)) {
                        fields.push(this.formData.shareEqually)
                    }
                    const topo = this.formData.resource.map(item => {
                        const [bk_obj_id, bk_inst_id] = item.id.split('_')
                        return {
                            bk_obj_id,
                            bk_inst_id
                        }
                    })
                    const hostData = await this.getHostInCC({ // 加载所有主机列表
                        url: this.urls['cc_search_host'],
                        fields,
                        topo
                    })
                    const moduleHosts = this.filterModuleHost(hostData.data)
                    const configData = this.getConfigData()
                    this.$emit('update', configData, moduleHosts)
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
                const hosts = [] // 模块实际的主机数据，去重、按照实际数量配置截取
                const reuseOthers = this.formData.modules.filter(item => item.selectMethod === 2)
                const usedHosts = []
                const fullMdHosts = this.getFullModuleHosts(data) // 所有满足各模块的主机数据
                for (let i = 0; i < this.formData.clusterCount; i++) {
                    const moduleHosts = {}
                    fullMdHosts.forEach(item => {
                        const md = this.formData.modules.find(m => m.id === item.id)
                        const mutedHostAttrs = this.getModuleMutedHostAttrs(md.id, moduleHosts, data) // 当前模块被之前遍历的模块指定为互斥模块的模块，所包含的主机互斥属性的值
                        moduleHosts[md.name] = []

                        if (md.count > 0) {
                            item.list.some(h => {
                                if (moduleHosts[md.name].length === md.count) {
                                    return true
                                }
                                if (!usedHosts.includes(h.bk_host_innerip) && !mutedHostAttrs.includes(h[this.formData.muteAttribute])) {
                                    moduleHosts[md.name].push(h.bk_host_innerip)
                                    usedHosts.push(h.bk_host_innerip)
                                }
                            })
                        }
                    })
                    reuseOthers.forEach(md => { // 复用其他模块主机数据，主机数量取本模块设置的值
                        let citedModule = this.formData.modules.find(item => item.id === md.reuse)
                        const citePath = [md]
                        while (!moduleHosts[citedModule.name]) {
                            citePath.unshift(Object.assign({}, citedModule))
                            citedModule = this.formData.modules.find(item => item.id === citedModule.reuse)
                        }
                        citePath.forEach(item => {
                            const cModule = this.formData.modules.find(cm => cm.id === item.reuse)
                            moduleHosts[item.name] = moduleHosts[cModule.name].slice(0, item.count)
                        })
                    })
                    hosts.push(moduleHosts)
                }

                return hosts
            },
            getFullModuleHosts (data) {
                const fullMdHosts = []
                this.formData.modules.forEach(md => {
                    const { id, selectMethod, customIpList, muteMethod, muteModules, hostFilterList } = md
                    const validFilters = hostFilterList.filter(item => item.type === 'filter' && item.filed !== '' && item.value.length > 0)
                    const validExclude = hostFilterList.filter(item => item.type === 'exclude' && item.filed !== '' && item.value.length > 0)
                    let list = []

                    if (selectMethod !== 2) { // 复用其他模块，则暂时不计算该模块的主机
                        if (selectMethod === 1) { // 模块手动填写 ip
                            const ipArr = customIpList.split(/[\,|\n|\uff0c]/) // 按照中英文逗号、换行符分割
                            ipArr.forEach(ipItem => {
                                const ipStr = ipItem.trim()
                                const matchedData = data.find(item => item.bk_host_innerip === ipItem)
                                if (ipStr && matchedData) {
                                    list.push(matchedData)
                                }
                            })
                            fullMdHosts.push({
                                id,
                                list,
                                percent: data.length > 0 ? list.length / data.length : 0
                            })
                        } else { // 默认筛选方式，则计算本模块数据
                            const innerMuteAttr = [] // 模块内互斥，已使用的属性的值

                            if (hostFilterList.length === 0) { // 筛选条件和排序条件为空，按照设置的主机数截取
                                list = data
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
                                        if (muteMethod === 1) { // 模块内互斥
                                            if (!innerMuteAttr.includes(item[this.formData.muteAttribute])) {
                                                innerMuteAttr.push(item[this.formData.muteAttribute])
                                                list.push(item)
                                            }
                                        } else {
                                            list.push(item)
                                        }
                                    }
                                })
                            }
                            const shareEquallyList = this.formData.shareEqually ? this.shareEquallyAttrs(list, this.formData.shareEqually) : list
                            fullMdHosts.push({
                                id,
                                muteModules,
                                list: shareEquallyList,
                                percent: data.length > 0 ? list.length / data.length : 0
                            })
                        }
                    }
                })
                return fullMdHosts.sort((a, b) => b.percent - a.percent)
            },
            /**
             * 将主机列表按照属性均摊排序重组
             *
             * @param {Array} list 主机列表
             * @param {String} attr 均摊属性
             *
             * @return {Array} 排序后的主机列表
             */
            shareEquallyAttrs (list, attr) {
                const mergedList = []
                const attrsValObj = {}
                list.forEach(item => {
                    const val = item[attr]
                    if (val in attrsValObj) {
                        attrsValObj[val].push(item)
                    } else {
                        attrsValObj[val] = [item]
                    }
                })
                const valArrs = Object.values(attrsValObj)
                const maxLenArr = valArrs.reduce((acc, crt) => {
                    return acc.length - crt.length > 0 ? acc : crt
                }, [])
                for (let i = 0; i < maxLenArr.length; i++) {
                    valArrs.forEach(groupItem => {
                        if (groupItem.length >= i + 1) {
                            mergedList.push(groupItem[i])
                        }
                    })
                }
                return mergedList
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
            /**
             * 获取目标模块，已经被其他互斥模块引用的主机互斥属性
             * @param {Number} id 模块 id
             * @param {Array} prevModulesHost 已被遍历的模块使用的主机
             * @param {Array} hosts 全量主机数据
             */
            getModuleMutedHostAttrs (id, prevModulesHost, hosts) {
                const mutedHostAttrs = []
                Object.keys(prevModulesHost).keys(mid => {
                    const moduleItem = this.formData.modules.find(item => item.id === mid)
                    if (moduleItem.muteMethod === 2 && moduleItem.muteModule.includes(id)) {
                        prevModulesHost.forEach(ip => {
                            const hostItem = hosts.find(item => item.bk_host_innerip === ip)
                            if (!mutedHostAttrs.includes(hostItem[this.formData.muteAttribute])) {
                                mutedHostAttrs.push(hostItem[this.formData.muteAttribute])
                            }
                        })
                    }
                })
                return mutedHostAttrs
            },
            // 将本地表单编辑数据格式转换为接口所需数据格式
            getConfigData () {
                const { clusterCount, modules, resource, set, muteAttribute, shareEqually } = this.formData
                const moduleDetail = []
                modules.forEach(md => { // 取出所有模块的筛选、排除条件字段，并模块详情数据转换为接口保存格式
                    const { id, name, count, selectMethod, reuse, customIpList, muteMethod, muteModules, hostFilterList } = md
                    const filterList = []
                    hostFilterList.forEach(item => {
                        if (item.field !== '' && item.value.length > 0) {
                            filterList.push({
                                type_val: item.type === 'exclude' ? 1 : 0,
                                name: item.field,
                                value: item.value
                            })
                        }
                    })
                    moduleDetail.push({
                        id,
                        name,
                        host_count: count,
                        reuse_module: reuse,
                        select_method: selectMethod,
                        custom_ip_list: customIpList.split(/[\,|\n|\uff0c]/).join('\n'),
                        mute_method: muteMethod,
                        mute_modules: muteModules,
                        host_filter_list: filterList
                    })
                })
                return {
                    set_count: clusterCount,
                    set_template_id: set[0].id,
                    set_template_name: set[0].label,
                    host_resources: resource,
                    mute_attribute: muteAttribute,
                    shareEqually: shareEqually,
                    module_detail: moduleDetail
                }
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
            .bk-radio-group /deep/ .bk-form-radio {
                margin-right: 30px;
                font-size: 12px;
            }
        }
        .mute-module-tip {
            font-size: 12px;
            color: #ffb400;
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
</style>
