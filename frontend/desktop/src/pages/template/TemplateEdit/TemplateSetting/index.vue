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
            :common="common"
            @templateDataChanged="$emit('templateDataChanged')"
            @onCitedNodeClick="$emit('onCitedNodeClick', $event)"
            @closeTab="closeTab">
        </TabGlobalVariables>
        <TabTemplateConfig
            v-if="activeTab === 'templateConfigTab'"
            ref="templateConfigTab"
            :common="common"
            :is-template-config-valid="isTemplateConfigValid"
            :project-info-loading="projectInfoLoading"
            @handlerFormChange="handlerFormChange"
            @onBeforeClose="onBeforeClose"
            @templateDataChanged="$emit('templateDataChanged')"
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
            @modifyTemplateData="$emit('modifyTemplateData', $event)"
            @closeTab="closeTab">
        </TabPipelineTreeEdit>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :show-footer="false"
            :value="isShowDialog"
            @cancel="isShowDialog = false">
            <div class="template-setting-dialog-content">
                <div class="leave-tips">{{ $t('保存已修改的基础信息吗？') }}</div>
                <div class="action-wrapper">
                    <bk-button theme="primary" @click="onConfirmClick">{{ $t('保存') }}</bk-button>
                    <bk-button theme="default" @click="onCancelClick">{{ $t('不保存') }}</bk-button>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import TabGlobalVariables from './TabGlobalVariables/index.vue'
    import TabTemplateConfig from './TabTemplateConfig.vue'
    import TabTemplateSnapshoot from './TabTemplateSnapshoot.vue'
    import TabPipelineTreeEdit from './TabPipelineTreeEdit.vue'

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
            isTemplateConfigValid: Boolean,
            activeTab: String,
            snapshoots: Array,
            common: [String, Number]
        },
        data () {
            return {
                isFormChange: false,
                isShowDialog: false
            }
        },
        methods: {
            // 关闭面板
            closeTab () {
                this.$emit('update:activeTab', '')
            },
            handlerFormChange () {
                this.isFormChange = true
            },
            onBeforeClose () {
                if (this.isFormChange) {
                    this.isShowDialog = this.isFormChange
                } else {
                    this.closeTab()
                }
            },
            onConfirmClick () {
                this.$refs.templateConfigTab.onConfirm()
                this.isShowDialog = false
                this.isFormChange = false
            },
            onCancelClick () {
                this.closeTab()
                this.isShowDialog = false
                this.isFormChange = false
            }
        }
    }
</script>
<style lang="scss">
    .template-setting-dialog-content {
        padding: 40px 0;
        text-align: center;
        .leave-tips {
            font-size: 24px;
            margin-bottom: 20px;
        }
        .action-wrapper .bk-button {
            margin-right: 6px;
        }
    }
</style>
