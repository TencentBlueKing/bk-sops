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
            @templateDataChanged="$emit('templateDataChanged')"
            @onCitedNodeClick="$emit('onCitedNodeClick', $event)"
            @closeTab="closeTab">
        </TabGlobalVariables>
        <TabTemplateConfig
            v-if="activeTab === 'templateConfigTab'"
            :is-template-config-valid="isTemplateConfigValid"
            :project-info-loading="projectInfoLoading"
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
            @confirm="onDataModify"
            @closeTab="closeTab">
        </TabPipelineTreeEdit>
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
            snapshoots: Array
        },
        methods: {
            // 关闭面板
            closeTab () {
                this.$emit('update:activeTab', '')
            }
        }
    }
</script>
