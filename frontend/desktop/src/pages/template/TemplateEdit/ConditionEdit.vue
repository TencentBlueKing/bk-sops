/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
        :quick-close="true"
        :before-close="onBeforeClose">
        <div slot="header">
            <div class="config-header">
                <i
                    v-if="backToVariablePanel"
                    class="bk-icon icon-arrows-left variable-back-icon"
                    @click="close(true)">
                </i>
                {{ $t('分支条件') }}
            </div>
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
                    </label>
                    <div class="code-wrapper">
                        <div class="condition-tips">
                            <p>{{ $t('支持 "==、!=、>、>=、&lt;、&lt;=、in、notin" 等二元操作符和 "and、or、True/true、False/false" 等关键字语法，还支持通过 ${key} 方式引用全局变量。')}}</p>
                            <p>{{ $t('示例：') }}</p>
                            <p>{{ $t('字符串比较：') }} "${key}" == "my string"</p>
                            <p>{{ $t('数值比较：') }} ${int(key)} >= 3</p>
                        </div>
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
    import { mapMutations } from 'vuex'
    import { NAME_REG } from '@/constants/index.js'
    import CodeEditor from '@/components/common/CodeEditor.vue'

    export default {
        name: 'conditionEdit',
        components: {
            CodeEditor
        },
        props: {
            isShow: Boolean,
            conditionData: Object,
            backToVariablePanel: Boolean,
            isReadonly: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const { name, value } = this.conditionData
            return {
                conditionName: name,
                expression: value,
                conditionRule: {
                    required: true,
                    max: 20,
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
                if (this.isReadonly) {
                    this.close()
                    return true
                }
                const { name, value } = this.conditionData
                if (this.conditionName === name && this.expression === value) {
                    this.close()
                    return true
                }
                this.$emit('onBeforeClose')
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
            close (openVariablePanel) {
                this.$emit('close', openVariablePanel)
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .config-header {
        display: flex;
        align-items: center;
        .variable-back-icon {
            font-size: 32px;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
    }
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
                .condition-tips {
                    margin-bottom: 10px;
                    font-size: 12px;
                    color: #b8b8b8;
                }
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
