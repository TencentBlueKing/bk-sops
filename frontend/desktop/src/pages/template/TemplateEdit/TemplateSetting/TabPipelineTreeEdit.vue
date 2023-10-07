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
    <bk-sideslider
        :is-show="true"
        :width="800"
        :title="$t('模板数据')"
        :quick-close="true"
        :before-close="closeTab">
        <div class="pipeline-tree-wrap" slot="content">
            <div class="code-wrapper">
                <full-code-editor
                    :value="template"
                    :options="{ readOnly: true, language: 'json' }">
                </full-code-editor>
            </div>
        </div>
    </bk-sideslider>
</template>

<script>
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'
    import { mapGetters } from 'vuex'
    export default {
        name: 'TabPipelineTreeEdit',
        components: {
            FullCodeEditor
        },
        data () {
            return {
                template: this.transPipelineTreeStr()
            }
        },
        methods: {
            ...mapGetters('template/', [
                'getLocalTemplateData'
            ]),
            transPipelineTreeStr () {
                const templateData = this.getLocalTemplateData()
                return JSON.stringify(templateData, null, 4)
            },
            closeTab () {
                this.$emit('closeTab')
            }
        }
    }
</script>

<style lang="scss" scoped>
    .pipeline-tree-wrap {
        height: calc(100vh - 60px);
    }
    .code-wrapper {
        position: relative;
        padding: 20px;
        height: calc(100% - 10px);
    }
</style>
