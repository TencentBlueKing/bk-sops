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
        :is-show.sync="isReuseVarDialogShow"
        :quick-close="false"
        :ext-cls="'common-dialog'"
        :title="title"
        width="600"
        @confirm="onConfirm($event)"
        @cancel="onCancel">
        <div slot="content">
            <div class="reuse-variable-dialog">
                <div class="common-form-item" v-if="!reuseVariable.useNewKey">
                    <label>{{ i18n.reuse }}</label>
                    <div class="common-form-content">
                        <bk-selector
                            :list="reuseableVarList"
                            :selected.sync="selectedVar"
                            :disabled="isSelectDisabled"
                            @item-selected="onSelect">
                        </bk-selector>
                    </div>
                </div>
                <div class="common-form-item" v-if="!reuseVariable.useNewKey">
                    <label>{{ i18n.new }}</label>
                    <div class="common-form-content">
                        <div class="new_variable-checkbox">
                            <BaseCheckbox @checkCallback="onToggleCreateVar"/>
                        </div>
                    </div>
                </div>
                <div class="create-new-variable" v-show="isCreateVar">
                    <div class="common-form-item">
                        <label>{{ i18n.name }}</label>
                        <div class="common-form-content">
                            <BaseInput
                                name="variableName"
                                v-model="varName"
                                v-validate="variableNameRule"/>
                            <span v-show="errors.has('variableName')" class="common-error-tip error-msg">{{ errors.first('variableName') }}</span>
                        </div>
                    </div>
                    <div class="common-form-item clearfix">
                        <label>{{ i18n.key }}</label>
                        <div class="common-form-content">
                            <BaseInput
                                name="variableKey"
                                v-model="varKey"
                                v-validate="variableKeyRule"/>
                            <span v-show="errors.has('variableKey')" class="common-error-tip error-msg">{{ errors.first('variableKey') }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
import '@/utils/i18n.js'
import { mapState } from 'vuex'
import { Validator } from 'vee-validate'
import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
import BaseCheckbox from '@/components/common/base/BaseCheckbox.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
export default {
    name: 'ReuseVarDialog',
    components: {
        BaseCheckbox,
        BaseInput
    },
    props: ['isReuseVarDialogShow', 'reuseVariable', 'reuseableVarList'],
    data () {
        return {
            i18n: {
                reuse: gettext("复用变量"),
                new: gettext("新建变量"),
                name: gettext("变量名称"),
                key: gettext("变量KEY")
            },
            selectedVar: this.reuseVariable.useNewKey ? '' : this.reuseableVarList[0].id,
            isCreateVar: this.reuseVariable.useNewKey,
            varName: '',
            varKey: '',
            variableNameRule: {
                required: true,
                max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                regex: NAME_REG
            },
            variableKeyRule: {
                required: true,
                max: STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH,
                regex: /(^\${[a-zA-Z_]\w*}$)|(^[a-zA-Z_]\w*$)/, // 合法变量key正则，eg:${fsdf_f32sd},fsdf_f32sd
                keyRepeat: true
            },
            isOverride: false
        }
    },
    computed: {
        ...mapState({
            constants: state => state.template.constants
        }),
        isSelectDisabled () {
            return this.isCreateVar
        },
        title () {
            if (this.reuseVariable.useNewKey) {
                return gettext('变量KEY已存在，请创建新变量')
            }
            return gettext('是否复用变量')
        }
    },
    created () {
        const self = this
        this.validator = new Validator({})
        this.validator.extend('keyRepeat', (value) => {
            value = /^\$\{\w+\}$/.test(value) ? value : '${' + value + '}'
            if (value in this.constants) {
                return false
            }
            return true
        })
    },
    methods: {
        onSelect (id) {
            this.selectedVar = id
        },
        onToggleCreateVar (checked) {
            this.isCreateVar = checked
        },
        onConfirm ($event) {
            this.$nextTick(() => {
                this.$validator.validateAll().then((result) => {
                    if (!result && this.isCreateVar) return
                    let variableConfig
                    if (this.isCreateVar) { // 新变量
                        if (!/^\$\{[\w]*\}$/.test(this.varKey)) {
                            this.varKey = "${" + this.varKey + "}"
                        }
                        variableConfig = {
                            type: 'create',
                            name: this.varName,
                            key: this.reuseVariable.key,
                            varKey: this.varKey,
                            source_tag: this.reuseVariable.source_tag,
                            source_info: this.reuseVariable.source_info,
                            value: this.reuseVariable.value
                        }
                    } else { // 复用
                        variableConfig = {
                            type: 'reuse',
                            name: this.reuseVariable.name,
                            key: this.reuseVariable.key,
                            varKey: this.selectedVar,
                            source_tag: this.reuseVariable.source_tag,
                            source_info: this.reuseVariable.source_info,
                            value: this.reuseVariable.value
                        }
                    }
                    this.$emit('onConfirmReuseVar', variableConfig)
                })
            })
        },
        onCancel () {
            this.$emit('onCancelReuseVar', this.reuseVariable)
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.reuse-variable-dialog {
    .common-form-item {
        label {
            width: 100px;
            font-weight: normal;
        }
        .common-form-content {
            margin: 0 30px 0 120px;
        }
         .is-override-radio {
            margin-right: 14px;
            height: 36px;
            line-height: 36px;
            font-size: 14px;
            .radio-icon {
                position: relative;
                display: inline-block;
                width: 14px;
                height: 14px;
                border: 1px solid $commonBorderColor;
                border-radius: 50%;
                cursor: pointer;
            }
            .radio-label {
                padding-left: 4px;
                line-height: 1;
                cursor: pointer;
            }
            input[type="radio"] {
                display: none;
            }
            input[type="radio"]:checked + label {
                & > .radio-icon {
                    background: $blueDefault;
                    border: 1px solid $blueDefault;
                    &:after {
                        content: "";
                        position: absolute;
                        top: 4px;
                        left: 4px;
                        width: 4px;
                        height: 4px;
                        background: $whiteDefault;
                        border-radius: 50%;
                    }
                }
            }
            &.is-disabled {
                .radio-label {
                    color: $greyDisable;
                    cursor: not-allowed;
                }
                .radio-icon {
                    border-color: $greyDisable;
                }
                input[type="radio"]:checked + label {
                    & > .radio-icon {
                        background: $whiteDefault;
                        border-color: $greyDisable;
                        &::after {
                            background: $greyDisable;
                        }
                    }
                }
            }
        }
    }
    .new_variable-checkbox {
        height: 36px;
        line-height: 36px;
    }
}

</style>

