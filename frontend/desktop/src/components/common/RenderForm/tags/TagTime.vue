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
    <div class="tag-time">
        <div v-if="formMode">
            <el-time-picker
                v-model="timeValue"
                :is-range="isRange"
                :value-format="format"
                :start-placeholder="startPlaceholder"
                :end-placeholder="endPlaceholder"
                :disabled="!editable || disabled"
                :placeholder="placeholder">
            </el-time-picker>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{viewValue}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        placeholder: {
            type: String,
            required: false,
            default: gettext('请选择时间'),
            desc: 'placeholder'
        },
        startPlaceholder: {
            type: String,
            required: false,
            default: gettext('请选择开始时间'),
            desc: gettext('开始时间 placeholder')
        },
        endPlaceholder: {
            type: String,
            required: false,
            default: gettext('请选择结束时间'),
            desc: gettext('结束时间 placeholder')
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: gettext('禁用选择器')
        },
        isRange: {
            type: String,
            required: false,
            default: false,
            desc: gettext('是否为选择时间范围')
        },
        format: {
            type: String,
            required: false,
            default: 'HH:mm:ss',
            desc: gettext('选中的时间以及展示的值')
        },
        value: {
            type: [String, Array],
            required: false,
            default: gettext('选中的时间')
        }
    }
    export default {
        name: 'TagTime',
        mixins: [getFormMixins(attrs)],
        computed: {
            timeValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            },
            viewValue () {
                if (Array.isArray(this.timeValue)) { // 多选
                    if (!this.timeValue.length) {
                        return '--'
                    }
                    return this.timeValue.join('-')
                } else { // 单选
                    return this.timeValue || '--'
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
.tag-time {
    /deep/ .el-date-editor {
        width: 100%;
        .el-range-input {
            font-size: 12px;
        }
        &.el-input__inner {
            padding: 0 32px;
            height: 32px;
            line-height: 32px;
        }
        &.el-input {
            .el-input__inner {
                height: 32px;
                line-height: 32px;
            }
            .el-input__prefix .el-input__icon {
                line-height: 32px;
            }
        }
    }
}
</style>
