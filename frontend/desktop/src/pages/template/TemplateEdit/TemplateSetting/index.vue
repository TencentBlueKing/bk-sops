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
    <div class="setting-area-wrap">
        <div class="setting-tab-wrap">
            <template v-for="tab in settingTabs">
                <div
                    :key="tab.id"
                    class="setting-panel-tab"
                    @click="onTemplateSettingShow(tab.id)">
                    <div :class="['setting-menu-icon', {
                        'active-tab': activeTab === tab.id,
                        'update': tab.id === 'globalVariableTab' && isGlobalVariableUpdate
                    }]">
                        <i :class="tab.icon" :title="tab.ti"></i>
                    </div>
                </div>
            </template>
        </div>
        <div class="setting-panel">
            <div class="panel-content">
                <TabGlobalVariables
                    :is-show="activeTab === 'globalVariableTab'"
                    ref="globalVariable"
                    :class="['panel-item', { 'active-tab': activeTab === 'globalVariableTab' }]"
                    :is-fixed-var-menu.sync="isFixedVarMenu"
                    :is-variable-editing="isVariableEditing"
                    :variable-type-list="variableTypeList"
                    @changeVariableEditing="onVariableEditingChange"
                    @variableDataChanged="onVariableDataChange"
                    @onCitedNodeClick="onCitedNodeClick"
                    @onClickVarPin="onClickVarPin"
                    @onColseTab="onColseTab">
                </TabGlobalVariables>
                <TabTemplateConfig
                    :class="['panel-item', { 'active-tab': activeTab === 'templateConfigTab' }]"
                    :is-show="activeTab === 'templateConfigTab'"
                    :is-template-config-valid="isTemplateConfigValid"
                    :project-info-loading="projectInfoLoading"
                    @onSelectCategory="onSelectCategory"
                    @onColseTab="onColseTab">
                </TabTemplateConfig>
                <TabLocalDraft
                    :class="['panel-item', { 'active-tab': activeTab === 'localDraftTab' }]"
                    :is-show="activeTab === 'localDraftTab'"
                    :draft-array="draftArray"
                    @onColseTab="onColseTab"
                    @onDeleteDraft="onDeleteDraft"
                    @onReplaceTemplate="onReplaceTemplate"
                    @onNewDraft="onNewDraft"
                    @updateDraft="updateDraft"
                    @hideConfigPanel="hideConfigPanel"
                    @updateLocalTemplateData="updateLocalTemplateData">
                </TabLocalDraft>
                <TabPipelineTreeEdit
                    :class="['panel-item', { 'active-tab': activeTab === 'templateDataEditTab' }]"
                    :is-show="activeTab === 'templateDataEditTab'"
                    @confirm="onDataModify"
                    @onColseTab="onColseTab">
                </TabPipelineTreeEdit>
            </div>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations } from 'vuex'
    import TabGlobalVariables from './TabGlobalVariables/index.vue'
    import TabTemplateConfig from './TabTemplateConfig.vue'
    import TabLocalDraft from './TabLocalDraft.vue'
    import TabPipelineTreeEdit from './TabPipelineTreeEdit.vue'

    const SETTING_TABS = [
        {
            id: 'globalVariableTab',
            icon: 'common-icon-square-code',
            title: i18n.t('全局变量')
        },
        {
            id: 'templateConfigTab',
            icon: 'common-icon-square-attribute',
            title: i18n.t('基础信息')
        },
        {
            id: 'localDraftTab',
            icon: 'common-icon-clock-reload',
            title: i18n.t('本地快照')
        },
        {
            id: 'templateDataEditTab',
            icon: 'common-icon-paper',
            title: i18n.t('模板数据')
        }
    ]

    export default {
        name: 'TemplateSetting',
        components: {
            TabGlobalVariables,
            TabTemplateConfig,
            TabLocalDraft,
            TabPipelineTreeEdit
        },
        props: [
            'projectInfoLoading',
            'businessInfoLoading',
            'isGlobalVariableUpdate',
            'isTemplateConfigValid',
            'isNodeConfigPanelShow',
            'isSettingPanelShow',
            'draftArray',
            'variableTypeList',
            'isClickDraft',
            'isFixedVarMenu'
        ],
        data () {
            return {
                showPanel: true,
                isVariableEditing: false,
                isPipelineTreeDialogShow: false,
                activeTab: 'globalVariableTab'
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'outputs': state => state.template.outputs,
                'constants': state => state.template.constants,
                'timeout': state => state.template.time_out,
                'hasAdminPerm': state => state.hasAdminPerm
            }),
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
            },
            settingTabs () {
                return this.hasAdminPerm ? SETTING_TABS.slice(0) : SETTING_TABS.slice(0, -1)
            }
        },
        watch: {
            isSettingPanelShow (val) {
                if (val) {
                    document.body.addEventListener('click', this.handleSettingPanelShow, false)
                } else {
                    this.activeTab = undefined
                    document.body.removeEventListener('click', this.handleSettingPanelShow, false)
                }
            }
        },
        mounted () {
            document.body.addEventListener('click', this.handleSettingPanelShow, false)
        },
        beforeDestroy () {
            document.body.removeEventListener('click', this.handleSettingPanelShow, false)
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
            togglePanel (val) {
                this.$emit('toggleSettingPanel', val, this.activeTab)
            },
            // 变量编辑是否展开
            isEditPanelOpen () {
                return this.isVariableEditing
            },
            // 变量保存
            saveVariable () {
                return this.$refs.globalVariable.saveVariable()
            },
            // 激活表单不合法的tab项
            setErrorTab (tab) {
                this.activeTab = tab
                this.togglePanel(true)
            },
            onVariableDataChange () {
                this.$emit('variableDataChanged')
            },
            onSelectCategory (value) {
                this.$emit('onSelectCategory', value)
            },
            onDeleteDraft (key) {
                this.$emit('onDeleteDraft', key)
            },
            onReplaceTemplate (data) {
                this.$emit('onReplaceTemplate', data)
            },
            onNewDraft (name) {
                this.$emit('onNewDraft', name)
            },
            updateDraft (key, data) {
                this.$emit('updateDraft', key, data)
            },
            hideConfigPanel () {
                this.$emit('hideConfigPanel')
            },
            updateLocalTemplateData () {
                this.$emit('updateLocalTemplateData')
            },
            onCitedNodeClick (nodeId) {
                this.$emit('onCitedNodeClick', nodeId)
            },
            onClickVarPin (val) {
                this.$emit('fixedVarMenuChange', val)
            },
            onVariableEditingChange (val) {
                this.isVariableEditing = val
            },
            onTemplateSettingShow (val) {
                if (this.activeTab === val) {
                    this.togglePanel(false)
                } else {
                    this.activeTab = val
                    this.togglePanel(true)
                }
                this.$emit('fixedVarMenuChange', false)
                this.$emit('globalVariableUpdate', false)
            },
            onDataModify (data) {
                this.isPipelineTreeDialogShow = false
                this.$emit('modifyTemplateData', data)
            },
            // 关闭面板
            onColseTab (tabName) {
                this.activeTab = undefined
                this.togglePanel(false)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.setting-area-wrap {
    float: right;
    height: 100%;
}
.setting-tab-wrap {
    position: absolute;
    right: 0;
    top: 0;
    padding: 15px 0;
    width: 56px;
    height: 100%;
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    border-bottom: 1px solid $commonBorderColor;
    z-index: 2551;
    .setting-panel-tab {
        padding: 15px 11px;
        color: #546a9e;
        cursor: pointer;
        &:hover {
            color: #3480ff;
        }
        .setting-menu-icon {
            position: relative;
            width: 32px;
            height: 32px;
            line-height: 32px;
            text-align: center;
            border-radius: 2px;
            &.active-tab {
                background: #525f77;
                color: #ffffff;
            }
            &.update:after {
                content: '';
                position: absolute;
                top: -6px;
                right: -6px;
                height: 8px;
                width: 8px;
                border-radius: 50%;
                background: #ff5757;
            }
        }
    }
}
.setting-panel {
    position: absolute;
    top: 0px;
    right: 56px;
    width: auto;
    height: 100%;
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
}
.panel-content {
    height: 100%;
    border: none;
}
.panel-item {
    height: 100%;
}
</style>
