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
                <bk-button theme="primary">{{ i18n.confirm }}</bk-button>
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
                    <bk-select ref="setSelect" :value="formData.set.id" ext-popover-cls="common-bk-select-hide-option">
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
                        :value="formData.resource|filterResourceId">
                        <template v-if="formData.resource.length > 0">
                            <bk-option
                                v-for="item in formData.resource"
                                :key="item.id"
                                :id="item.id"
                                :name="item.label">
                            </bk-option>
                        </template>
                        <el-tree
                            node-key="id"
                            v-model="formData.resouce"
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
            <bk-tab class="module-tabs">
                <bk-tab-panel
                    v-for="(moduleItem, moduleIndex) in moduleList"
                    :key="moduleItem.name"
                    :active.sync="activeTab">
                    <bk-form :model="formData.modules[moduleIndex]">
                        <bk-form-item :label="i18n.resourceNum" :required="true" property="count">
                            <bk-input v-model="formData.modules[moduleIndex].count" type="number" :min="0"></bk-input>
                        </bk-form-item>
                        <bk-form-item :label="i18n.reuse" property="isReuse">
                            <bk-switcher v-model="formData.modules[moduleIndex].isReuse"></bk-switcher>
                        </bk-form-item>
                        <bk-form-item :label="i18n.reuseModule" property="reuseModule">
                            <bk-select v-model="formData.modules[moduleIndex]">
                                <bk-option
                                    v-for="item in reuseModules"
                                    :key="item.name"
                                    :id="item.name">
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                    </bk-form>
                </bk-tab-panel>
            </bk-tab>
        </section>
    </div>
</template>
<script >
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'ResourceFilter',
        filters: {
            filterResourceId (data) {
                return data.map(item => item.id)
            }
        },
        data () {
            return {
                formData: {
                    clusterCount: '',
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
                    filter: gettext('主机筛选条件（同时满足）'),
                    exclude: gettext('主机排除条件（同时满足）')
                }
            }
        },
        computed: {
            reuseModules () {
                return this.moduleList
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
                        this.moduleList = resp.data
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
                        this.conditions = resp.data
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
            },
            onResourceSelect (checked, data) {
                this.formData.resource = data.checkedNodes
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
        .module-tabs {
            margin-top: 20px;
        }
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
