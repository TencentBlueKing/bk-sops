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
                        {{ $t('分支类型') }}
                        <span class="required">*</span>
                    </label>
                    <bk-radio-group v-model="branchType">
                        <bk-radio :value="'customize'" :disabled="isReadonly">{{ $t('自定义分支') }}</bk-radio>
                        <bk-radio :value="'default'" :disabled="isReadonly || hasDefaultBranch">
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
                            <p>{{ $t('字符串比较：') }}<code class="code">${key} == "my string"</code></p>
                            <p>{{ $t('数值比较：') }}<code class="code">${int(key)} >= 3</code></p>
                            <p>{{ $t('包含：') }}<code class="code">${key} in (1,2,3)</code></p>
                        </div>
                        <full-code-editor
                            v-validate="expressionRule"
                            name="expression"
                            :value="expression"
                            :options="{ language: 'python', readOnly: isReadonly }"
                            @input="onDataChange">
                        </full-code-editor>
                    </div>
                    <span v-show="veeErrors.has('expression')" class="common-error-tip error-msg">{{ veeErrors.first('expression') }}</span>
                </div>
            </div>
            <div class="btn-wrap">
                <bk-button v-if="!isReadonly" class="save-btn" theme="primary" @click="confirm">{{ $t('确定') }}</bk-button>
                <bk-button theme="default" @click="close(false)">{{ isReadonly ? $t('关闭') : $t('取消') }}</bk-button>
            </div>
        </div>
    </bk-sideslider>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapMutations } from 'vuex'
    import { NAME_REG } from '@/constants/index.js'
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'

    export default {
        name: 'conditionEdit',
        components: {
            FullCodeEditor
        },
        props: {
            isShow: Boolean,
            gateways: Object,
            conditionData: Object,
            backToVariablePanel: Boolean,
            isReadonly: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const { name, value, id, nodeId } = this.conditionData
            const gwConfig = this.gateways[nodeId]
            const defaultCondition = gwConfig && gwConfig.default_condition // 默认分支配置
            const isDefaultBranch = defaultCondition && defaultCondition.flow_id === id // 当前分支是否为默认分支
            const branchType = isDefaultBranch ? 'default' : 'customize'
            let hasDefaultBranch = false
            if (defaultCondition && defaultCondition.flow_id !== id) {
                hasDefaultBranch = true
            }
            return {
                branchType, // 当前分支类型
                hasDefaultBranch, // 是否存在默认分支(不包含当前分支)
                defaultTipsConfig: {
                    width: 216,
                    content: i18n.t('所有分支均不匹配时执行，类似switch-case-default里面的default'),
                    placements: ['bottom-start']
                },
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
            },
            branchType: {
                handler (val) {
                    if (val === 'default') {
                        this.conditionName = i18n.t('默认')
                    } else {
                        this.conditionName = this.conditionData.name
                    }
                }
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
                        const { id, nodeId, tag, overlayId, loc } = this.conditionData
                        const data = {
                            id,
                            nodeId,
                            overlayId,
                            loc,
                            value: this.branchType === 'default' ? undefined : this.expression.trim(),
                            name: this.conditionName
                        }
                        if (this.branchType === 'default') {
                            data.default_condition = {
                                name: this.conditionName,
                                tag,
                                flow_id: id
                            }
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
                .condition-tips {
                    margin-bottom: 10px;
                    font-size: 12px;
                    color: #b8b8b8;
                    /deep/.bk-link {
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
                        font: 0.85em/1.8 ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace;
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
        .btn-wrap {
            position: relative;
            padding: 8px 20px;
            border-top: 1px solid #cacedb;
            background: #fff;
        }
    }
    .code-wrapper .full-code-editor {
        height: 300px;
    }
</style>
