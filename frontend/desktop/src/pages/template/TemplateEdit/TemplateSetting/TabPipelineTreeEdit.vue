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
    <div class="pipeline-tree-wrap">
        <bk-sideslider
            ext-cls="common-template-setting-sideslider pipeline-tree-edit"
            :width="840"
            :is-show="isShow"
            :before-close="onBeforeClose"
            :quick-close="true">
            <div slot="header">
                <span>{{$t('流程模板数据')}}</span>
            </div>
            <div style="height: 100%" slot="content">
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
                    <bk-button class="save-btn" theme="primary" @click="onConfirm">{{ $t('保存') }}</bk-button>
                </div>
            </div>
        </bk-sideslider>
    </div>
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
                template: '',
                errorMessage: ''
            }
        },
        computed: {
            ...mapState({
                hasAdminPerm: state => state.hasAdminPerm
            })
        },
        watch: {
            isShow (val) {
                if (val) {
                    this.template = this.transPipelineTreeStr()
                }
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
                    this.$emit('confirm', pipelineData)
                }
            },
            onBeforeClose () {
                this.$emit('onColseTab', 'templateDataEditTab')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.pipeline-tree-edit {
    .code-wrapper {
        position: relative;
        margin: 20px 20px;
        height: calc(100% - 94px);
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
    .save-btn {
        position: absolute;
        left: 0;
        bottom: -44px;
    }
}
</style>
