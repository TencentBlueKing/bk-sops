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
        <header>
            <span class="title">{{ i18n.title }}</span>
            <div class="btns">
                <bk-button theme="primary" @click="onConfigConfirm">{{ i18n.confirm }}</bk-button>
                <bk-button
                    theme="default"
                    @click="$emit('update:showFilter', false)">
                    {{ i18n.cancel }}
                </bk-button>
            </div>
        </header>
        <section>
            <bk-form :model="formData">
                <bk-form-item :label="i18n.cluster" :required="true" property="cluster">
                    <bk-input v-model="formData.clusterCount" type="number" :min="0"></bk-input>
                </bk-form-item>
                <bk-form-item :label="i18n.set" :required="true" property="set">
                    <bk-select
                        ref="setSelect"
                        :value="formData.set.id"
                        :clearable="false"
                        ext-popover-cls="common-bk-select-hide-option">
                        <template v-if="formData.set.id">
                            <bk-option
                                v-for="item in [formData.set]"
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
                            :check-on-click-node="true"
                            @check="onSetSelect">
                        </el-tree>
                    </bk-select>
                </bk-form-item>
                <bk-form-item :label="i18n.resource" :required="true" property="resource">
                    <bk-select
                        multiple
                        ext-popover-cls="common-bk-select-hide-option"
                        :value="formData.resource|filterResourceId"
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
                            :data="resourceList"
                            :check-on-click-node="true"
                            @check="onResourceSelect">
                        </el-tree>
                    </bk-select>
                </bk-form-item>
            </bk-form>
            <div class="module-wrapper" v-bkloading="{ isLoading: pending.module, opacity: 1 }">
                <bk-tab v-if="moduleList.length > 0" class="module-tabs" :active.sync="activeTab">
                    <bk-tab-panel
                        v-for="(moduleItem, moduleIndex) in moduleList"
                        :key="moduleItem.name"
                        :name="moduleItem.bk_module_id"
                        :label="moduleItem.bk_module_name">
                        <bk-form :model="formData.modules[moduleIndex]">
                            <bk-form-item :label="i18n.resourceNum" :required="true" property="count">
                                <bk-input v-model="formData.modules[moduleIndex].count" type="number" :min="0"></bk-input>
                            </bk-form-item>
                            <bk-form-item :label="i18n.reuse" property="isReuse">
                                <bk-switcher
                                    v-model="formData.modules[moduleIndex].isReuse"
                                    theme="primary"
                                    size="small"
                                    @change="onChangeReuse($event, formData.modules[moduleIndex])">
                                </bk-switcher>
                            </bk-form-item>
                            <bk-form-item :label="i18n.reuseModule" property="reuse" v-if="formData.modules[moduleIndex].isReuse">
                                <bk-select v-model="formData.modules[moduleIndex].reuse">
                                    <bk-option
                                        v-for="item in canReusedModules"
                                        :key="item.bk_module_id"
                                        :name="item.bk_module_name"
                                        :id="item.bk_module_id">
                                    </bk-option>
                                </bk-select>
                            </bk-form-item>
                            <div class="condition-wrapper" v-else>
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
                <no-data class="module-empty" v-else></no-data>
            </div>
        </section>
    </div>
</template>
<script >
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    import SelectCondition from '../IpSelector/SelectCondition.vue'

    export default {
        name: 'ResourceFilter',
        filters: {
            filterResourceId (data) {
                return data.map(item => item.id)
            }
        },
        components: {
            SelectCondition,
            NoData
        },
        props: {
            config: {
                type: Object
            }
        },
        data () {
            return {
                formData: {
                    clusterCount: 0,
                    set: {},
                    resource: [],
                    modules: []
                },
                setList: [], // 集群模板 tree
                resourceList: [], // 主机资源所属 tree
                moduleList: [], // 集群下模块列表
                activeTab: '',
                conditions: [],
                pending: {
                    set: false,
                    resource: false,
                    module: false,
                    condition: false
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
            canReusedModules (id) {
                return this.moduleList.filter((item, index) => {
                    if (
                        item.bk_module_id === this.activeTab
                        || this.formData.modules[index].reuse === this.activeTab
                    ) {
                        return false
                    }
                    return true
                })
            }
        },
        mounted () {
            this.getSetTopo()
            this.getResource()
            this.getCondition()
        },
        methods: {
            ...mapActions([
                'getCCSearchTopoSet',
                'getCCSearchTopoResource',
                'getCCSearchModule',
                'getCCSearchObjAttrHost'
            ]),
            async getSetTopo () {
                try {
                    this.pending.set = true
                    const resp = await this.getCCSearchTopoSet()
                    if (resp.result) {
                        this.setList = resp.data
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
                    const resp = await this.getCCSearchTopoResource()
                    if (resp.result) {
                        this.resourceList = resp.data
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.resource = false
                }
            },
            async getModule () {
                try {
                    this.pending.set = true
                    const resp = await this.getCCSearchModule()
                    if (resp.result) {
                        this.moduleList = resp.data.info
                        resp.data.info.forEach((item, index) => {
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
                    const resp = await this.getCCSearchObjAttrHost()
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
            onSetSelect (checked) {
                this.formData.set = checked
                this.$refs.setTree.setCheckedNodes([checked])
                this.$refs.setSelect.close()
                this.getModule({
                    bk_set_id: checked.id
                })
            },
            // 清空所选主机资源
            onResourceClear () {
                this.$refs.resourceTree.setCheckedNodes([])
            },
            onResourceSelect (checked, data) {
                this.formData.resource = data.checkedNodes
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
            onConfigConfirm () {
                // @todo 校验
                const { clusterCount, modules, resource, set } = this.formData
                const hostResources = resource.map(item => {
                    return {
                        bk_module_id: item.id,
                        bk_module_name: item.name
                    }
                })
                const moduleDetail = modules.map(item => {
                    const { count, name, reuse, filters, excludes } = item
                    return {
                        name,
                        filters,
                        excludes,
                        host_count: count,
                        reuse_module: reuse
                    }
                })
                const config = {
                    set_count: clusterCount,
                    set_template_id: set.id,
                    host_resources: hostResources,
                    module_detail: moduleDetail
                }
                this.$emit('update', config)
                this.$emit('update:showFilter', false)
            }
        }
    }
</script>
<style lang="scss" scoped>
    header {
        margin: 20px 0;
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
    section {
        padding: 20px;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        .module-wrapper {
            margin-top: 20px;
            min-height: 450px;
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
