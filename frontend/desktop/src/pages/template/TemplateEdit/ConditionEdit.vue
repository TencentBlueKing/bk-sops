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
    <div class="condition-edit">
        <bk-sideslider
            :ext-cls="getSliderCls"
            :width="420"
            :is-show="isShow"
            :before-close="onBeforeClose"
            :quick-close="true">
            <div slot="header">
                <span>{{ $t('分支条件') }}</span>
            </div>
            <div class="condition-form" slot="content">
                <div class="form-item">
                    <label class="label">
                        {{ $t('分支名称') }}
                        <span class="required">*</span>
                    </label>
                    <bk-input
                        v-model.trim="conditionName"
                        v-validate="conditionRule"
                        name="conditionName"
                        :clearable="true">
                    </bk-input>
                    <span v-show="errors.has('conditionName')" class="common-error-tip error-msg">{{ errors.first('conditionName') }}</span>
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
                            :options="{ language: 'python' }"
                            @input="onDataChange">
                        </code-editor>
                    </div>
                    <span v-show="errors.has('expression')" class="common-error-tip error-msg">{{ errors.first('expression') }}</span>
                </div>
            </div>
        </bk-sideslider>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import CodeEditor from '@/components/common/CodeEditor.vue'
    export default {
        name: 'conditionEdit',
        components: {
            CodeEditor
        },
        props: {
            isSettingPanelShow: Boolean,
            isShowConditionEdit: Boolean,
            settingActiveTab: String,
            isShow: Boolean
        },
        data () {
            return {
                i18n: {
                    tips: i18n.t('支持 "==、!=、>、>=、<、<=、in、notin" 等二元操作符和 "and、or、True/true、False/false" 等关键字语法，还支持通过 "${key}" 方式引用全局变量。示例：`${key1} >= 3 and ${key2} == "Test"`')
                },
                conditionName: '',
                expression: '',
                conditionRule: {
                    required: true,
                    max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                expressionRule: {
                    required: true
                },
                conditionData: {}
            }
        },
        computed: {
            getSliderCls () { // 动态设置面板的 class
                let base = 'common-template-setting-sideslider'
                if (this.isSettingPanelShow) {
                    switch (this.settingActiveTab) {
                        case 'globalVariableTab':
                            base += ' position-right-var'
                            break
                        case 'templateConfigTab':
                            base += ' position-right-basic-info'
                            break
                        case 'tplSnapshootTab':
                            base += ' position-right-cache'
                            break
                        case 'templateDataEditTab':
                            base += ' position-right-template-data'
                    }
                }
                return base
            }
        },
        methods: {
            updateConditionData (data) {
                this.conditionData = data
                this.conditionName = data.name
                this.expression = data.value
            },
            getConditionData () {
                const { id, nodeId, overlayId } = this.conditionData
                return {
                    id,
                    nodeId,
                    overlayId,
                    value: this.expression,
                    name: this.conditionName
                }
            },
            closeConditionEdit () {
                const { id, nodeId, overlayId } = this.conditionData
                this.$emit('onCloseConditionEdit', {
                    id,
                    nodeId,
                    overlayId,
                    value: this.expression,
                    name: this.conditionName
                })
            },
            checkCurrentConditionData () {
                this.closeConditionEdit()
                return this.$validator.validateAll()
            },
            // 关闭配置面板
            onBeforeClose () {
                this.closeConditionEdit()
            },
            onDataChange (val) {
                if (val !== this.expression) {
                    this.expression = val.trim()
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.condition-edit {
    z-index: 5;
    transition: right 0.3s ease-in-out;
    .common-template-setting-sideslider {
        /deep/ .bk-sideslider-wrapper {
            transition: right .3s ease-in-out;
            right: 56px;
        }
        &.position-right-var {
            /deep/ .bk-sideslider-wrapper {
                right: 856px;
                border-right: 1px solid #dcdee5;
            }
        }
        &.position-right-basic-info{
            /deep/ .bk-sideslider-wrapper {
                right: 476px;
                border-right: 1px solid #dcdee5;
            }
        }
        &.position-right-cache {
            /deep/ .bk-sideslider-wrapper {
                right: 476px;
                border-right: 1px solid #dcdee5;
            }
        }
        &.position-right-template-data {
            /deep/ .bk-sideslider-wrapper {
                right: 896px;
                border-right: 1px solid #dcdee5;
            }
        }
    }
    .condition-form {
        .form-item {
            margin: 0 20px;
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
                height: 160px;
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
}
</style>
