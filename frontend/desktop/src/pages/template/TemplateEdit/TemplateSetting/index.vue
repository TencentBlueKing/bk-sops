/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="setting-panel">
        <TabOperationFlow
            v-if="activeTab === 'operationFlowTab'"
            @closeTab="closeTab">
        </TabOperationFlow>
        <TabGlobalVariables
            v-if="activeTab === 'globalVariableTab'"
            :common="common"
            :is-view-mode="isViewMode"
            @viewClick="$emit('viewClick', $event)"
            @templateDataChanged="$emit('templateDataChanged')"
            @onCitedNodeClick="$emit('onCitedNodeClick', $event)"
            @closeTab="closeTab">
        </TabGlobalVariables>
        <TabTemplateConfig
            v-if="activeTab === 'templateConfigTab'"
            :common="common"
            :is-view-mode="isViewMode"
            :project-info-loading="projectInfoLoading"
            :template-label-loading="templateLabelLoading"
            :template-labels="templateLabels"
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
            :is-view-mode="isViewMode"
            @modifyTemplateData="$emit('modifyTemplateData', $event)"
            @closeTab="closeTab">
        </TabPipelineTreeEdit>
    </div>
</template>
<script>
    import TabGlobalVariables from './TabGlobalVariables/index.vue'
    import TabTemplateConfig from './TabTemplateConfig.vue'
    import TabTemplateSnapshoot from './TabTemplateSnapshoot.vue'
    import TabPipelineTreeEdit from './TabPipelineTreeEdit.vue'
    import TabOperationFlow from './TabOperationFlow.vue'

    export default {
        name: 'TemplateSetting',
        components: {
            TabGlobalVariables,
            TabTemplateConfig,
            TabTemplateSnapshoot,
            TabPipelineTreeEdit,
            TabOperationFlow
        },
        props: {
            isViewMode: Boolean,
            projectInfoLoading: Boolean,
            templateLabelLoading: Boolean,
            templateLabels: Array,
            activeTab: String,
            snapshoots: Array,
            common: [String, Number]
        },
        methods: {
            // 关闭面板
            closeTab () {
                this.$emit('update:activeTab', '')
            }
        }
    }
</script>
