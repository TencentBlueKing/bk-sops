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
        :width="800"
        :is-show="isShow"
        :quick-close="isReadonly"
        :before-close="onBeforeClose">
        <div slot="header">
            <span>{{ $t('分支条件') }}</span>
        </div>
        <div class="condition-form" slot="content">
            <div class="form-wrap">
                <div class="form-item">
                    <label class="label">
                        {{ $t('分支名称') }}
                        <span class="required">*</span>
                    </label>
                    <bk-input
                        :readonly="isReadonly"
                        v-model.trim="conditionName"
                        v-validate="conditionRule"
                        name="conditionName">
                    </bk-input>
                    <span v-show="veeErrors.has('conditionName')" class="common-error-tip error-msg">{{ veeErrors.first('conditionName') }}</span>
                </div>
                <div class="form-item">
                    <label class="label">
                        {{ $t('表达式')}}
                        <span class="required">*</span>
                        <i
                            class="common-icon-info expression-tips"
                            v-bk-tooltips="{
                                content: i18n.tips,
                                placement: 'right-end',
                                duration: 0,
                                width: 240
                            }">
                        </i>
                    </label>
                    <div class="code-wrapper">
                        <code-editor
                            v-validate="expressionRule"
                            name="expression"
                            :value="expression"
                            :options="{ language: 'python', readOnly: isReadonly }"
                            @input="onDataChange">
                        </code-editor>
                    </div>
                    <span v-show="veeErrors.has('expression')" class="common-error-tip error-msg">{{ veeErrors.first('expression') }}</span>
                </div>
            </div>
            <div class="btn-wrap">
                <bk-button v-if="!isReadonly" class="save-btn" theme="primary" @click="confirm">{{ $t('保存') }}</bk-button>
                <bk-button theme="default" @click="close">{{ isReadonly ? $t('关闭') : $t('取消') }}</bk-button>
            </div>
        </div>
    </bk-sideslider>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapMutations } from 'vuex'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import CodeEditor from '@/components/common/CodeEditor.vue'
    export default {
        name: 'conditionEdit',
        components: {
            CodeEditor
        },
        props: {
            isShow: Boolean,
            conditionData: Object,
            isReadonly: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const { name, value } = this.conditionData
            return {
                i18n: {
                    tips: i18n.t('支持 "==、!=、>、>=、<、<=、in、notin" 等二元操作符和 "and、or、True/true、False/false" 等关键字语法，还支持通过 "${key}" 方式引用全局变量。示例：${key1} >= 3 and "${key2}" == "Test"')
                },
                conditionName: name,
                expression: value,
                conditionRule: {
                    required: true,
                    max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                expressionRule: {
                    required: true
                }
            }
        },
        watch: {
            conditionData (val) {
                const { name, value } = val
                this.conditionName = name
                this.expression = value
            }
        },
        methods: {
            ...mapMutations('template/', [
                'setBranchCondition'
            ]),
            onDataChange (val) {
                this.expression = val
            },
            // 关闭配置面板
            onBeforeClose () {
                this.close()
                return true
            },
            confirm () {
                this.$validator.validateAll().then(result => {
                    if (result) {
                        const { id, nodeId, overlayId } = this.conditionData
                        const data = {
                            id,
                            nodeId,
                            overlayId,
                            value: this.expression.trim(),
                            name: this.conditionName
                        }
                        this.setBranchCondition(data)
                        this.$emit('updataCanvasCondition', data)
                        this.close()
                    }
                })
            },
            close () {
                this.$emit('update:isShow', false)
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .condition-form {
        height: calc(100vh - 60px);
        .form-wrap {
            padding: 20px 30px;
            height: calc(100% - 49px);
        }
        .form-item {
            margin-bottom: 20px;
            .label {
                display: block;
                position: relative;
                line-height: 36px;
                color: #313238;
                font-size: 14px;
                .required {
                    color: #ff2602;
                }
            }
            .code-wrapper {
                height: 300px;
            }
        }
        .expression-tips {
            margin-left: 6px;
            color:#c4c6cc;
            font-size: 16px;
            cursor: pointer;
            &:hover {
                color:#f4aa1a;
            }
            &.quote-info {
                margin-left: 0px;
            }
        }
        .btn-wrap {
            padding: 8px 20px;
            border-top: 1px solid #cacedb;
        }
    }
</style>
