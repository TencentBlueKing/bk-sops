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
        :is-show="true"
        :width="800"
        :title="$t('流程模板数据')"
        :quick-close="!hasAdminPerm"
        :before-close="closeTab">
        <div class="pipeline-tree-wrap" slot="content">
            <div class="code-wrapper">
                <code-editor
                    :value="template"
                    :options="{ readOnly: !hasAdminPerm, language: 'json' }"
                    @input="onDataChange">
                </code-editor>
                <div class="error-tips" v-if="errorMessage" :title="errorMessage">
                    <i class="common-icon-info"></i>
                    <div class="message">{{ errorMessage }}</div>
                </div>
            </div>
            <div class="btn-wrap">
                <template v-if="hasAdminPerm">
                    <bk-button class="save-btn" theme="primary" @click="onConfirm">{{ $t('保存') }}</bk-button>
                    <bk-button theme="default" @click="closeTab">{{ $t('取消') }}</bk-button>
                </template>
                <bk-button v-else theme="primary" @click="closeTab">{{ $t('关闭') }}</bk-button>
            </div>
        </div>
    </bk-sideslider>
</template>

<script>
    import CodeEditor from '@/components/common/CodeEditor.vue'
    import { mapState, mapGetters } from 'vuex'
    import validatePipeline from '@/utils/validatePipeline.js'
    export default {
        name: 'TabPipelineTreeEdit',
        components: {
            CodeEditor
        },
        props: ['isShow'],
        data () {
            return {
                template: this.transPipelineTreeStr(),
                errorMessage: ''
            }
        },
        computed: {
            ...mapState({
                hasAdminPerm: state => state.hasAdminPerm
            })
        },
        methods: {
            ...mapGetters('template/', [
                'getLocalTemplateData'
            ]),
            transPipelineTreeStr () {
                const templateData = this.getLocalTemplateData()
                return JSON.stringify(templateData, null, 4)
            },
            onDataChange (value) {
                if (value !== this.template) {
                    this.template = value
                }
            },
            onConfirm () {
                let pipelineData = {}
                try {
                    pipelineData = JSON.parse(this.template)
                    this.errorMessage = ''
                } catch (error) {
                    this.errorMessage = error
                }
                if (!this.errorMessage) {
                    const validateResult = validatePipeline.isPipelineDataValid(pipelineData)
                    if (!validateResult.result) {
                        this.errorMessage = validateResult.message
                        return
                    }
                    this.$emit('modifyTemplateData', pipelineData)
                    this.closeTab()
                }
            },
            closeTab () {
                this.$emit('closeTab')
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';
    .pipeline-tree-wrap {
        height: calc(100vh - 60px);
    }
    .code-wrapper {
        position: relative;
        padding: 20px;
        height: calc(100% - 49px);
    }
    .error-tips {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        position: absolute;
        bottom: -50px;
        left: 0;
        width: 654px;
        height: 38px;
        color: #ea3636;
        font-size: 12px;
        .common-icon-info {
            margin-right: 6px;
            font-size: 16px;
        }
        .message {
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
    }
    .btn-wrap {
        padding: 8px 20px;
        border-top: 1px solid #cacedb;
    }
</style>
