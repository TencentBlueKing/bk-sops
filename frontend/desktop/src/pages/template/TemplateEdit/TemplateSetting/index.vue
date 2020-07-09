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
    <bk-sideslider
        :is-show="activeTab !== ''"
        :width="800"
        ext-cls="setting-slider"
        :before-close="beforeClose">
        <div class="setting-header" slot="header">
            <span>{{ tabDetail.title }}</span>
            <template v-if="tabDetail.id === 'globalVariableTab'">
                <i
                    class="common-icon-info"
                    v-bk-tooltips="{
                        allowHtml: true,
                        content: '#var-desc',
                        placement: 'bottom-end',
                        duration: 0,
                        width: 400
                    }">
                </i>
                <div id="var-desc">
                    <div class="tips-item">
                        <h4>{{ $t('属性：') }}</h4>
                        <p>
                            {{ $t('"来源/是否显示"格式，来源是输入类型') }}
                            <i class="common-icon-show-left" style="color: #219f42"></i>
                            {{ $t('表示变量来自用户添加的变量或者标准插件/子流程节点输入参数引用的变量，来源是输出类型') }}
                            <i class="common-icon-hide-right" style="color: #de9524"></i>
                            {{ $t('表示变量来自标准插件/子流程节点输出参数引用的变量；是否显示表示该变量在新建任务填写参数时是否展示给用户，') }}
                            <i class="common-icon-eye-show" style="color: #219f42;vertical-align: middle;"></i>
                            {{ $t('表示显示，') }}
                            <i class="common-icon-eye-hide" style="color: #de9524;vertical-align: middle;"></i>
                            {{ $t('表示隐藏，输出类型的变量一定是隐藏的。') }}
                        </p>
                    </div>
                    <div class="tips-item">
                        <h4>{{ $t('输出：') }}</h4>
                        <p>{{ $t('表示该变量会作为该流程模板的输出参数，在被其他流程模板当做子流程节点时可以引用。') }}</p>
                    </div>
                </div>
            </template>
            <i
                v-if="tabDetail.id === 'tplSnapshootTab'"
                class="common-icon-info"
                v-bk-tooltips="{
                    content: tabDetail.desc,
                    placement: 'bottom-end',
                    duration: 0,
                    width: 400
                }">
            </i>
        </div>
        <div class="setting-panel" slot="content">
            <TabGlobalVariables
                v-if="activeTab === 'globalVariableTab'"
                :is-fixed-var-menu.sync="isFixedVarMenu"
                :is-variable-editing="isVariableEditing"
                :variable-type-list="variableTypeList"
                @changeVariableEditing="onVariableEditingChange"
                @variableDataChanged="onVariableDataChange"
                @onCitedNodeClick="onCitedNodeClick">
            </TabGlobalVariables>
            <TabTemplateConfig
                v-if="activeTab === 'templateConfigTab'"
                :is-template-config-valid="isTemplateConfigValid"
                :project-info-loading="projectInfoLoading"
                @onSelectCategory="onSelectCategory">
            </TabTemplateConfig>
            <TabTemplateSnapshoot
                v-if="activeTab === 'tplSnapshootTab'"
                :is-show="activeTab === 'tplSnapshootTab'"
                :snapshoots="snapshoots"
                @createSnapshoot="$emit('createSnapshoot')"
                @useSnapshoot="$emit('useSnapshoot', arguments)"
                @updateSnapshoot="$emit('updateSnapshoot', $event)">
            </TabTemplateSnapshoot>
            <TabPipelineTreeEdit
                v-if="activeTab === 'templateDataEditTab'"
                @confirm="onDataModify"
                @close="closeTab">
            </TabPipelineTreeEdit>
        </div>
    </bk-sideslider>
</template>
<script>
    import { mapState, mapMutations } from 'vuex'
    import TabGlobalVariables from './TabGlobalVariables/index.vue'
    import TabTemplateConfig from './TabTemplateConfig.vue'
    import TabTemplateSnapshoot from './TabTemplateSnapshoot.vue'
    import TabPipelineTreeEdit from './TabPipelineTreeEdit.vue'
    import SETTING_TABS from '../SettingTabs.js'

    export default {
        name: 'TemplateSetting',
        components: {
            TabGlobalVariables,
            TabTemplateConfig,
            TabTemplateSnapshoot,
            TabPipelineTreeEdit
        },
        props: {
            projectInfoLoading: Boolean,
            businessInfoLoading: Boolean,
            isGlobalVariableUpdate: Boolean,
            isTemplateConfigValid: Boolean,
            isNodeConfigPanelShow: Boolean,
            variableTypeList: Array,
            isFixedVarMenu: Boolean,
            activeTab: String,
            snapshoots: Array
        },
        data () {
            return {
                showPanel: true,
                isVariableEditing: false,
                isPipelineTreeDialogShow: false,
                settingTabs: SETTING_TABS
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'outputs': state => state.template.outputs,
                'constants': state => state.template.constants,
                'timeout': state => state.template.time_out
            }),
            tabDetail () {
                if (this.activeTab) {
                    return SETTING_TABS.find(item => item.id === this.activeTab)
                }
                return {}
            },
            variableData () {
                if (this.theKeyOfEditing) {
                    return this.constants[this.theKeyOfEditing]
                } else {
                    return {
                        custom_type: 'input',
                        desc: '',
                        key: '',
                        name: '',
                        show_type: 'show',
                        source_info: {},
                        source_tag: '',
                        source_type: 'custom',
                        validation: '^.+$',
                        validator: [],
                        value: ''
                    }
                }
            }
        },
        methods: {
            ...mapMutations('template/', [
                'editVariable',
                'deleteVariable',
                'setOutputs',
                'setReceiversGroup',
                'setNotifyType',
                'setOvertime',
                'setCategory'
            ]),
            onVariableDataChange () {
                this.$emit('variableDataChanged')
            },
            onSelectCategory (value) {
                this.$emit('onSelectCategory', value)
            },
            onCitedNodeClick (nodeId) {
                this.$emit('onCitedNodeClick', nodeId)
            },
            onVariableEditingChange (val) {
                this.isVariableEditing = val
            },
            onDataModify (data) {
                this.isPipelineTreeDialogShow = false
                this.$emit('modifyTemplateData', data)
                this.closeTab()
            },
            beforeClose () {
                this.closeTab()
                return true
            },
            // 关闭面板
            closeTab () {
                this.$emit('update:activeTab', '')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .setting-header {
        display: flex;
        align-items: center;
        .common-icon-info {
            margin-left: 10px;
            font-size: 16px;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
    }
    #var-desc {
        .tips-item {
            & > h4 {
                margin: 0;
            }
            &:not(:last-child) {
                margin-bottom: 10px;
            }
        }
    }
    .setting-panel {
        height: calc(100vh - 60px);
    }
</style>
