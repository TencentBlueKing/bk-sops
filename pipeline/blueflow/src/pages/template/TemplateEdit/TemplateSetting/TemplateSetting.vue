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
    <div class="setting-area-wrap">
        <div :class="['setting-tab-wrap', {'vertical-fold': !showPanel}]">
            <div class="setting-panel-tab" @click="onTemplateSettingShow('globalVariableTab')">
                <div :class="['setting-menu-icon', {'activeTab': activeTab === 'globalVariableTab'}]">
                    <i class="common-icon-square-code" :title="i18n.globalVariable"></i>
                </div>
            </div>
            <div class="setting-panel-tab" @click="onTemplateSettingShow('templateConfigTab')">
                <div :class="['setting-menu-icon', {'activeTab': activeTab === 'templateConfigTab'}]">
                    <i class="common-icon-square-attribute" :title="i18n.basicInformation"></i>
                </div>
            </div>
            <div class="setting-panel-tab" @click="onTemplateSettingShow('localDraftTab')">
                <div :class="['setting-menu-icon', {'activeTab': activeTab === 'localDraftTab'}]">
                    <i class="common-icon-clock-reload" :title="i18n.localCache"></i>
                </div>
            </div>
        </div>
        <transition name="slideRight">
            <div class="setting-panel" v-show="showPanel">
                <div class="panel-content">
                    <TabGlobalVariables
                        v-show="activeTab === 'globalVariableTab'"
                        ref="globalVariable"
                        class="panel-item"
                        :isVariableEditing="isVariableEditing"
                        @changeVariableEditing="onVariableEditingChange"
                        @variableDataChanged="onVariableDataChange"
                        @onDeleteConstant="onDeleteConstant">
                    </TabGlobalVariables>
                    <TabTemplateConfig
                        class="panel-item"
                        v-show="activeTab === 'templateConfigTab'"
                        :isTemplateConfigValid="isTemplateConfigValid"
                        :businessInfoLoading="businessInfoLoading"
                        @onSelectCategory="onSelectCategory">
                    </TabTemplateConfig>
                    <TabLocalDraft
                        class="panel-item"
                        v-show="activeTab === 'localDraftTab'"
                        :draftArray="draftArray"
                        @onDeleteDraft="onDeleteDraft"
                        @onReplaceTemplate="onReplaceTemplate"
                        @onNewDraft="onNewDraft"
                        @hideConfigPanel="hideConfigPanel">
                    </TabLocalDraft>
                </div>
            </div>
        </transition>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations } from 'vuex'
import tools from '@/utils/tools.js'
import TabGlobalVariables from './TabGlobalVariables.vue'
import TabTemplateConfig from './TabTemplateConfig.vue'
import TabLocalDraft from './TabLocalDraft.vue'

export default {
    name: 'TemplateSetting',
    components: {
        TabGlobalVariables,
        TabTemplateConfig,
        TabLocalDraft
    },
    props: ['businessInfoLoading', 'isTemplateConfigValid', 'isSettingPanelShow', 'draftArray'],
    data () {
        return {
            i18n: {
                globalVariable: gettext('全局变量'),
                basicInformation: gettext('基础信息'),
                localCache: gettext('本地缓存')
            },
            showPanel: true,
            isVariableEditing: false,
            activeTab: 'globalVariableTab'
        }
    },
    computed: {
        ...mapState({
            'businessBaseInfo': state => state.template.businessBaseInfo,
            'outputs': state => state.template.outputs,
            'constants': state => state.template.constants,
            'timeout': state => state.template.time_out
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
        }
    },
    watch: {
        isSettingPanelShow (val) {
            this.showPanel = val
        }
    },
    methods: {
        ...mapMutations ('template/', [
            'editVariable',
            'deleteVariable',
            'setOutputs',
            'setReceiversGroup',
            'setNotifyType',
            'setOvertime',
            'setCategory'
        ]),
        togglePanel (val) {
            this.$emit('toggleSettingPanel', val)
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
        onDeleteConstant (key) {
            this.$emit('onDeleteConstant', key)
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
        hideConfigPanel () {
            this.$emit('hideConfigPanel')
        },
        updateLocalTemplateData () {
            this.$emit('updateLocalTemplateData')
        },
        onVariableEditingChange (val) {
            this.isVariableEditing = val
        },
        onTemplateSettingShow (val) {
            if (this.activeTab === val) {
                this.activeTab = undefined
                this.togglePanel(false)
            } else {
                this.activeTab = val
                this.togglePanel(true)
            }
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.setting-area-wrap {
    position: absolute;
    top: 60px;
    right: 0px;
    height: calc(100% - 50px);
    z-index: 4;
}
.setting-tab-wrap {
    position: absolute;
    top: 0px;
    right: 0px;
    padding: 15px 0;
    width: 56px;
    height: 100%;
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    border-bottom: 1px solid $commonBorderColor;
    z-index: 1;
    transition: height 0.3s ease-in;
    &.vertical-fold {
        height: 217px;
    }
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
            &.activeTab {
                background: #525f77;
                color: #ffffff;
            }
        }
    }
}
.setting-panel {
    position: absolute;
    top: 0px;
    right: 56px;
    width: 420px;
    height: 100%;
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    transition: right 0.5s ease-in-out;
}
.panel-content {
    height: 100%;
    border: none;
}
.panel-item {
    height: 100%;
}
</style>
