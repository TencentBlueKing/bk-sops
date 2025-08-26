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
    <div class="condition-form">
        <div class="form-wrap">
            <div class="form-item">
                <label class="label">
                    {{ $t('分支类型') }}
                </label>
                <bk-radio-group v-model="branchType">
                    <bk-radio :value="'customize'" disabled>{{ $t('自定义分支') }}</bk-radio>
                    <bk-radio :value="'default'" disabled>
                        {{ $t('默认分支') }}
                        <i v-bk-tooltips="defaultTipsConfig" class="common-icon-info"></i>
                    </bk-radio>
                </bk-radio-group>
            </div>
            <div class="form-item" v-if="branchType === 'customize'">
                <label class="label">
                    {{ $t('表达式')}}
                    <span class="required">*</span>
                </label>
                <div class="code-wrapper">
                    <div class="condition-tips">
                        <p>{{ $t('支持 "==、!=、>、>=、&lt;、&lt;=、in、notin" 等二元比较操作符') }}</p>
                        <p>{{ $t('支持 "and、or、True/true、False/false" 等关键字语法') }}</p>
                        <p>{{ $t('表达式更多细节请参考') }}
                            <bk-link theme="primary" href="https://boolrule.readthedocs.io/en/latest/expressions.html#basic-comparison-operators" target="_blank">
                                {{ 'boolrule' }}
                            </bk-link></p>
                        <br>
                        <p>{{ $t('支持使用全局变量，如') }}<code class="code">${key}</code>、<code class="code">${int(key)}</code></p>
                        <p>{{ $t('支持使用内置函数、datetime、re、hashlib、random、time、os.path模块处理全局变量') }}</p>
                        <br>
                        <p>{{ $t('示例：') }}</p>
                        <p>{{ $t('字符串比较：') }}<code class="code">"${key}" == "my string"</code></p>
                        <p>{{ $t('数值比较：') }}<code class="code">${int(key)} >= 3</code></p>
                        <p>{{ $t('包含：') }}<code class="code">${key} in (1,2,3)</code></p>
                    </div>
                    <full-code-editor
                        name="expression"
                        :value="expression"
                        :options="{ language: 'python', readOnly: true }">
                    </full-code-editor>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'

    export default {
        name: 'conditionEdit',
        components: {
            FullCodeEditor
        },
        props: {
            conditionData: Object
        },
        data () {
            return {
                defaultTipsConfig: {
                    width: 216,
                    content: i18n.t('所有分支均不匹配时执行，类似switch-case-default里面的default'),
                    placements: ['bottom-start']
                },
                expression: this.conditionData.value
            }
        },
        computed: {
            branchType () {
                return this.conditionData.conditionType === 'default' ? 'default' : 'customize'
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
                .condition-tips {
                    margin-bottom: 10px;
                    font-size: 12px;
                    color: #b8b8b8;
                    ::v-deep .bk-link {
                        vertical-align: initial;
                        .bk-link-text {
                            font-size: 12px;
                        }
                    }
                    .code {
                        background-color: #eff1f3;
                        color: #9e938a;
                        border-radius: 4px;
                        padding: 0 4px;
                        margin: 0 2px;
                        font: 0.85em/1.5 ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace;
                    }
                }
            }
            .bk-form-radio {
                margin-right: 48px;
                .common-icon-info {
                    color: #979ba5;
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
    }
    .code-wrapper .full-code-editor {
        height: 300px;
    }
</style>
