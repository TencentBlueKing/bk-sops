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
    <div class="tag-radio">
        <div v-if="formMode">
            <el-radio-group v-model="checkedValue">
                <div class="radio-item" v-for="item in items" :key="item.name">
                    <el-radio :label="item.value" :disabled="!editable || disabled">{{item.name}}</el-radio>
                </div>
            </el-radio-group>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{viewValue}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import i18n from '@/config/i18n/index.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        items: {
            type: Array,
            required: true,
            default () {
                return [
                    {
                        name: i18n.t('选项1'),
                        value: 'value1'
                    },
                    {
                        name: i18n.t('选项2'),
                        value: 'value2'
                    },
                    {
                        name: i18n.t('选项3'),
                        value: 'value3'
                    }
                ]
            },
            desc: "array like [{name: '', value: ''}, {name: '', value: ''}]"
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'disable radio'
        },
        value: {
            type: [String, Boolean],
            required: false,
            default: ''
        }
    }
    export default {
        name: 'TagRadio',
        mixins: [getFormMixins(attrs)],
        computed: {
            checkedValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            },
            viewValue () {
                if (this.checkedValue === '') {
                    return '--'
                }

                let label = this.checkedValue
                this.items.some(item => {
                    if (item.value === this.checkedValue) {
                        label = item.name
                        return true
                    }
                })
                return label
            }
        }
    }
</script>
<style lang="scss" scoped>
    .radio-item {
        display: inline-block;
        ::v-deep .el-radio__label {
            display: inline-block;
            padding-right: 10px;
            min-width: 80px;
        }
        ::v-deep .el-radio {
            height: 32px;
            line-height: 32px;
            &.is-checked .el-radio__label {
                color: #606266;
            }
        }
    }
</style>
