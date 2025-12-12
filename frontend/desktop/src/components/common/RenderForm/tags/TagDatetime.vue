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
    <div class="tag-datetime">
        <div v-if="formMode" class="tag-datetime-select-form">
            <el-date-picker
                v-model="dateValue"
                popper-class="tag-component-popper"
                :type="type"
                :format="format"
                :value-format="format"
                :disabled="!editable || disabled"
                :placeholder="placeholder">
            </el-date-picker>
            <span class="time-zone" v-if="type !== 'date'">{{ locTimeZone }}</span>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{(value === 'undefined' || value === '') ? '--' : value}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import i18n from '@/config/i18n/index.js'
    import moment from 'moment-timezone'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        placeholder: {
            type: String,
            required: false,
            default: i18n.t('请选择日期时间'),
            desc: 'placeholder'
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: i18n.t('禁用选择器')
        },
        type: {
            type: String,
            required: false,
            default: 'datetime',
            desc: i18n.t('日期选择器显示类型')
        },
        format: {
            type: String,
            required: false,
            default: 'yyyy-MM-dd HH:mm:ss',
            desc: i18n.t('选中的时间以及展示的值')
        },
        value: {
            type: String,
            required: false,
            default: i18n.t('选中的时间')
        }
    }
    export default {
        name: 'TagDatetime',
        mixins: [getFormMixins(attrs)],
        computed: {
            dateValue: {
                get () {
                    return this.value
                },
                set (val) {
                    const formatTime = moment(val).tz(window.TIMEZONE || moment.tz.guess()).format('YYYY-MM-DD HH:mm:ssZZ')
                    this.updateForm(formatTime)
                }
            },
            locTimeZone () {
                // 使用全局变量 window.TIMEZONE，如果没有则使用浏览器本地时区
                if (window.TIMEZONE) {
                    try {
                        const offset = moment().tz(window.TIMEZONE).format('ZZ')
                        return offset
                    } catch (e) {
                        console.warn(e)
                        return new Date().toTimeString().slice(12, 17)
                    }
                }
                return new Date().toTimeString().slice(12, 17)
            }
        }
    }
</script>
<style lang="scss" scoped>
.tag-datetime {
    ::v-deep .el-date-editor {
        width: 100%;
        &.el-input {
            .el-input__inner {
                padding: 0 30px;
            }
        }
    }
    .tag-datetime-select-form{
        .time-zone {
            position: relative;
            font-size: 12px;
            margin: 0 8px 0 -68px;
            color: #979ba5;
        }
    }
}
</style>
