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
    <div class="setting-panel">
        <TabGlobalVariables
            v-if="activeTab === 'globalVariableTab'"
            @variableDataChanged="onVariableDataChange"
            @onCitedNodeClick="onCitedNodeClick"
            @closeTab="closeTab">
        </TabGlobalVariables>
        <TabTemplateConfig
            v-if="activeTab === 'templateConfigTab'"
            :is-template-config-valid="isTemplateConfigValid"
            :project-info-loading="projectInfoLoading"
            @onSelectCategory="onSelectCategory"
            @closeTab="closeTab">
        </TabTemplateConfig>
        <TabTemplateSnapshoot
            v-if="activeTab === 'tplSnapshootTab'"
            :snapshoots="snapshoots"
            @createSnapshoot="$emit('createSnapshoot')"
            @useSnapshoot="$emit('useSnapshoot', arguments)"
            @updateSnapshoot="$emit('updateSnapshoot', $event)"
            @closeTab="closeTab">
        </TabTemplateSnapshoot>
        <TabPipelineTreeEdit
            v-if="activeTab === 'templateDataEditTab'"
            @confirm="onDataModify"
            @closeTab="closeTab">
        </TabPipelineTreeEdit>
    </div>
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
            activeTab: String,
            snapshoots: Array
        },
        data () {
            return {
                showPanel: true,
                isPipelineTreeDialogShow: false,
                settingTabs: SETTING_TABS
            }
        },
        computed: {
            ...mapState({
                'constants': state => state.template.constants
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
            onDataModify (data) {
                this.isPipelineTreeDialogShow = false
                this.$emit('modifyTemplateData', data)
                this.closeTab()
            },
            // 关闭面板
            closeTab () {
                this.$emit('update:activeTab', '')
            }
        }
    }
</script>
