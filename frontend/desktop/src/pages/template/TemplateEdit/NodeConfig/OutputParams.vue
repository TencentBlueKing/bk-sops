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
    <div class="output-params">
        <bk-table :data="list" :col-border="false" :row-class-name="getRowClassName">
            <bk-table-column :label="$t('名称')" :width="180" prop="name">
                <div class="params-name" slot-scope="props">
                    <span class="name" v-bk-overflow-tips>{{ props.row.name }}</span>
                    <i
                        v-if="props.row.description"
                        v-bk-tooltips="props.row.description"
                        class="common-icon-tooltips">
                    </i>
                </div>
            </bk-table-column>
            <bk-table-column label="KEY" class-name="param-key">
                <div slot-scope="props" class="param-key-wrap">
                    <div
                        v-bk-tooltips="{
                            content: props.row.key,
                            disabled: props.row.hooked ? !props.row.isTooLong : true
                        }"
                        class="variable-key"
                        :class="{ 'is-too-long': props.row.isTooLong }">
                        <template v-if="props.row.isTooLong">
                            <span class="prev-span">{{ props.row.key.slice(0, -6) }}</span>
                            <span class="next-span">{{ props.row.key.slice(-6) }}</span>
                        </template>
                        <template v-else>
                            {{ props.row.key }}
                        </template>
                    </div>
                    <template v-if="props.row.hooked">
                        <bk-select
                            v-model="props.row.assignmentType"
                            :clearable="false"
                            :disabled="isViewMode"
                            class="assignment-select">
                            <bk-option id="direct" :name="$t('直接赋值给')"></bk-option>
                            <!-- <bk-option id="splice" :name="$t('拼接赋值给')"></bk-option> -->
                        </bk-select>
                        <bk-select
                            v-model="props.row.variableValue"
                            :clearable="false"
                            :placeholder="$t('请选择变量')"
                            :search-placeholder="$t('请输入变量名/key')"
                            :class="['variable-select', { 'is-unselect': props.row.isUnselect }]"
                            ext-popover-cls="variable-select-popover"
                            searchable
                            :disabled="isViewMode"
                            @toggle="onValSelectToggle($event, props.row)">
                            <bk-option
                                v-for="variable in variableList"
                                :key="variable.key"
                                :id="variable.key"
                                :name="variable.name + '（' + variable.key + '）'">
                            </bk-option>
                            <div slot="extension" class="variable-popover-extension" @click="$emit('openVariablePanel', defaultOpts, props.row.key)">
                                <i class="bk-icon icon-plus-circle"></i>
                                <span>{{ $t('新建变量') }}</span>
                            </div>
                        </bk-select>
                        <i
                            v-if="props.row.isUnselect"
                            v-bk-tooltips="$t('请选择变量')"
                            class="bk-icon icon-exclamation-circle-shape">
                        </i>
                    </template>
                    <div
                        class="hook-icon-wrap"
                        :class="{ actived: props.row.hooked, disabled: isViewMode || !hook }"
                        v-bk-tooltips="{
                            content: props.row.hooked ? $t('取消赋值给变量') : $t('赋值给变量'),
                            placement: 'bottom',
                            zIndex: 3000,
                            extCls: 'variable-hook-tips',
                            arrow: false,
                            theme: 'light'
                        }"
                        @click="onHookChange(props)">
                        <i class="common-icon-var"></i>
                        <i class="bk-icon icon-angle-up-fill"></i>
                    </div>
                </div>
            </bk-table-column>
        </bk-table>
        <bk-dialog
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :render-directive="'if'"
            :header-position="'left'"
            :title="$t('新建变量')"
            :auto-close="false"
            :value="isShow"
            width="600"
            @confirm="onConfirm"
            @cancel="onCancel">
            <div class="variable-dialog">
                <bk-alert
                    style="margin-bottom: 14px;"
                    type="warning"
                    :title="$t('已存在相同KEY的变量，请新建变量')">
                </bk-alert>
                <bk-form
                    ref="form"
                    :model="formData"
                    :rules="rules">
                    <template>
                        <bk-form-item :label="$t('变量名称')" property="name" :required="true">
                            <bk-input name="variableName" v-model="formData.name"></bk-input>
                        </bk-form-item>
                        <bk-form-item :label="$t('变量KEY')" property="key" :required="true">
                            <bk-input name="variableKey" v-model="formData.key"></bk-input>
                        </bk-form-item>
                    </template>
                </bk-form>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'
    export default {
        name: 'OutputParams',
        props: {
            params: Array,
            hook: {
                type: Boolean,
                default: true
            },
            constants: Object,
            thirdPartyCode: String,
            isSubflow: Boolean,
            isViewMode: Boolean,
            nodeId: String,
            version: String, // 标准插件版本或子流程版本
            hookKey: String
        },
        data () {
            const list = this.getOutputsList(this.params)
            const $this = this
            const len = Object.keys(this.constants).length
            const defaultOpts = {
                name: '',
                key: '',
                desc: '',
                custom_type: '',
                source_info: {},
                source_tag: '',
                value: '',
                show_type: 'hide',
                source_type: 'component_outputs',
                validation: '',
                index: len,
                version: '',
                plugin_code: ''
            }
            return {
                list,
                isShow: false,
                formData: {},
                selectIndex: '',
                rules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                            message: i18n.t('变量名称长度不能超过') + STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('变量名称不能包含') + INVALID_NAME_CHAR + i18n.t('非法字符'),
                            trigger: 'blur'
                        }
                    ],
                    key: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH,
                            message: i18n.t('变量KEY值长度不能超过') + STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            // 合法变量key正则，eg:${fsdf_f32sd},fsdf_f32sd
                            regex: /(^\${(?!_env_|_system\.)[a-zA-Z_]\w*}$)|(^(?!_env_|_system\.)[a-zA-Z_]\w*$)/,
                            message: i18n.t('变量KEY由英文字母、数字、下划线组成，不允许使用系统变量及业务环境变量命名规则，且不能以数字开头'),
                            trigger: 'blur'
                        },
                        {
                            validator (val) {
                                const value = /^\$\{\w+\}$/.test(val) ? val : `\${${val}}`
                                if (value in $this.constants) {
                                    return false
                                }
                                return true
                            },
                            message: i18n.t('变量KEY值已存在'),
                            trigger: 'blur'
                        }
                    ]
                },
                unhookingVarIndex: 0, // 正被取消勾选的表单下标
                defaultOpts
            }
        },
        computed: {
            variableList () {
                return Object.values(this.constants).filter(item => item.source_type === 'component_outputs')
            }
        },
        watch: {
            params (val) {
                this.list = this.getOutputsList(val)
            }
        },
        methods: {
            getOutputsList () {
                const list = []
                const varKeys = Object.keys(this.constants)
                this.params.forEach(param => {
                    let variableValue = ''
                    let isHooked = varKeys.some(item => {
                        const varItem = this.constants[item]
                        if (varItem.source_type === 'component_outputs') {
                            const sourceInfo = varItem.source_info[this.nodeId]
                            if (sourceInfo && sourceInfo.includes(param.key)) {
                                variableValue = item
                                return true
                            }
                        }
                    })
                    if (this.hookKey === param.key) {
                        isHooked = true
                        const varValues = Object.values(this.constants)
                        variableValue = varValues.sort((a, b) => b.index - a.index)[0].key
                    }
                    list.push({
                        key: param.key,
                        name: param.name,
                        description: param.schema?.description,
                        version: param.version,
                        status: param.status,
                        hooked: isHooked || param.key === this.hookKey,
                        isTooLong: false,
                        isUnselect: false,
                        assignmentType: param.assignmentType || 'direct',
                        variableValue
                    })
                })
                return list
            },
            getRowClassName ({ row }) {
                return row.status || ''
            },
            onValSelectToggle (val, row) {
                if (val) {
                    row.isUnselect = false
                } else if (!row.variableValue) {
                    row.isUnselect = true
                }
            },
            /**
             * 输出参数勾选切换
             */
            onHookChange (props) {
                if (this.isViewMode) return
                const { $index, row } = props
                const index = $index
                this.unhookingVarIndex = index
                if (!row.hooked) {
                    row.hooked = true
                    // 判断key值是否超出最大宽度
                    const varKeyDom = document.querySelectorAll('.variable-key')[index]
                    const width = varKeyDom.offsetWidth || 0
                    row.isTooLong = width > 198
                } else {
                    row.hooked = false
                    row.isUnselect = false
                }
            },
            // 变量勾选/取消勾选后，需重新对form进行赋值
            setFormData () {
                const index = this.unhookingVarIndex
                this.list[index].key = this.params[index].key
                this.list[index].name = this.params[index].name
                this.list[index].hooked = false
                this.list[index].isTooLong = false
            },
            onConfirm ($event) {
                this.$refs.form.validate().then(result => {
                    if (result) {
                        const { name, key } = this.formData
                        this.isShow = false
                        const selectInfo = this.list[this.selectIndex]
                        const version = this.isSubflow ? selectInfo.version : this.version
                        let setKey = ''
                        if ((/^\$\{((?!\{).)*\}$/).test(key)) {
                            selectInfo.key = key
                            setKey = key
                        } else {
                            selectInfo.key = `\$\{${key}\}`
                            setKey = `\$\{${key}\}`
                        }
                        const config = {
                            name: name,
                            key: setKey,
                            source_info: {
                                [this.nodeId]: [this.params[this.selectIndex].key]
                            },
                            version,
                            plugin_code: this.isSubflow ? selectInfo.plugin_code : (this.thirdPartyCode || '')
                        }
                        this.createVariable(config)
                    }
                })
            },
            onCancel () {
                this.isShow = false
                this.list[this.selectIndex].hooked = false
            },
            createVariable (variableOpts) {
                const variable = Object.assign({}, this.defaultOpts, variableOpts)
                this.$emit('hookChange', 'create', variable)
            },
            validate () {
                let result = true
                this.list.forEach(item => {
                    if (item.hooked && !item.variableValue) {
                        item.isUnselect = true
                        result = false
                    }
                })
                return result
            }
        }
    }
</script>
<style lang="scss">
    .tippy-popper.variable-hook-tips {
        .tippy-tooltip {
            color: #63656e;
            padding: 10px 13px;
            border: 1px solid #dcdee5;
            box-shadow: 0 2px 6px 0 rgba(0,0,0,0.10);
            border-radius: 2px;
        }
        .tippy-content {
            line-height: 20px;
        }
    }
    .variable-select-popover {
        .bk-select-extension {
            background: #fafbfd;
            border-radius: 0 0 2px 2px;
            &:hover {
                background: #f0f1f5;
            }
        }
        .variable-popover-extension {
            height: 40px;
            line-height: 40px;
            text-align: center;
            cursor: pointer;
        }
    }
</style>
<style lang="scss" scoped>
    .output-params {
        .params-name {
            display: flex;
            align-items: center;
            .name {
                white-space: nowrap;
                text-overflow: ellipsis;
                overflow: hidden;
            }
            .common-icon-tooltips {
                flex-shrink: 0;
                margin-left: 3px;
                font-size: 14px;
            }
        }
        .param-key-wrap {
            display: flex;
            align-items: center;
            .variable-key {
                display: flex;
                overflow: hidden;
                .prev-span{
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                .next-span{
                    white-space: nowrap;
                }
                &.is-too-long {
                    max-width: 198px;
                }
            }
            .bk-select {
                margin-left: 8px;
            }
            .assignment-select {
                width: 96px;
                /deep/.bk-select-name {
                    padding-right: 23px;
                }
            }
            .variable-select {
                width: 240px;
                min-width: 180px;
                &.is-unselect {
                    border-color: #ff5656;
                }
            }
            >.icon-exclamation-circle-shape {
                position: relative;
                left: -19px;
                font-size: 14px;
                color: #ea3636;
                background: #fff;
                cursor: pointer;
            }
        }
    }
    .variable-dialog {
        padding: 30px;
        .new-var-notice {
            margin-bottom: 10px;
            font-size: 14px;
            color: #ea3636;
        }
        .bk-form:not(.bk-form-vertical) {
            /deep/ .bk-form-content {
                margin-right: 30px;
            }
        }
    }
    .bk-table {
        /deep/ .bk-table-row {
            &.deleted {
                background: #fff5f4;
            }
            &.added {
                background: rgba(220,255,226,0.30);
            }
            .param-key .cell {
                padding-right: 74px;
            }
        }
    }
    .hook-icon-wrap {
        position: absolute;
        right: 16px;
        top: 5px;
        width: 50px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #979ba5;
        background: #f0f1f5;
        cursor: pointer;
        border-radius: 2px;
        .common-icon-var {
            font-size: 16px;
        }
        .icon-angle-up-fill {
            font-size: 12px;
            color: #c4c6cc;
            margin-left: 6px;
        }
        &.disabled {
            color: #c4c6cc;
            cursor: not-allowed;
        }
        &:hover,
        &.actived {
            color: #3a84ff;
            background: #e1ecff;
        }
    }
</style>
