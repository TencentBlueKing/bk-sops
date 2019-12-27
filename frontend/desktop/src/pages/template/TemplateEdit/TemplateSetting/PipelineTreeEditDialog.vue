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
    <bk-dialog
        width="800"
        ext-cls="common-dialog"
        :theme="'primary'"
        :title="i18n.title"
        :mask-close="false"
        :auto-close="false"
        :header-position="'left'"
        :value="isShow"
        @value-change="toggleDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="code-wrapper">
            <code-editor
                :value="template"
                :options="{ readOnly: !hasAdminPerm, language: 'json' }"
                @changeContent="onDataChange">
            </code-editor>
            <div class="error-tips" v-if="errorMessage" :title="errorMessage">
                <div class="message">{{ errorMessage }}</div>
            </div>
        </div>
        <template v-slot:footer>
            <bk-button v-if="!hasAdminPerm" theme="default" @click="onCancel">{{ i18n.close }}</bk-button>
            <template v-else>
                <bk-button theme="primary" @click="onConfirm">{{ i18n.confirm }}</bk-button>
                <bk-button theme="default" @click="onCancel">{{ i18n.cancel }}</bk-button>
            </template>
        </template>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import CodeEditor from '@/components/common/CodeEditor.vue'
    import { mapState, mapGetters } from 'vuex'
    import validatePipeline from '@/utils/validatePipeline.js'

    export default {
        name: 'PipelineTreeEditDialog',
        components: {
            CodeEditor
        },
        props: {
            isShow: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                template: '',
                errorMessage: '',
                i18n: {
                    title: gettext('流程模板数据'),
                    close: gettext('关闭'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消')
                }
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
            toggleDialogShow () {
                if (this.isShow) {
                    this.template = this.transPipelineTreeStr()
                }
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
            onCancel () {
                this.$emit('cancel')
                this.errorMessage = ''
                this.template = this.transPipelineTreeStr()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .code-wrapper {
        position: relative;
        padding: 10px 20px;
        height: 400px;
    }
    .error-tips {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        position: absolute;
        bottom: -50px;
        left: 20px;
        width: 560px;
        height: 38px;
        color: #ea3636;
        font-size: 12px;
        .message {
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
    }
</style>
