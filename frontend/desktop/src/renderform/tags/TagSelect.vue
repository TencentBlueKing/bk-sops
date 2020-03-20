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
    <div class="tag-select">
        <div v-if="formMode">
            <el-select
                v-model="seletedValue"
                v-loading="loading"
                clearable
                filterable
                :disabled="!editable || disabled"
                :remote="remote"
                :multiple-limit="multiple_limit"
                :multiple="multiple"
                :no-data-text="empty_text"
                :placeholder="placeholder">
                <template v-if="!hasGroup">
                    <el-option
                        v-for="item in items"
                        v-loading="loading"
                        :key="item.text"
                        :label="item.text"
                        :value="item.value">
                    </el-option>
                </template>
                <template v-else>
                    <el-option-group
                        v-for="group in items"
                        :key="group.text"
                        :label="group.text">
                        <el-option
                            v-for="item in group.options"
                            v-loading="loading"
                            :key="item.text"
                            :label="item.text"
                            :value="item.value">
                        </el-option>
                    </el-option-group>
                </template>
            </el-select>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{viewValue}}</span>
    </div>
</template>
<script>
    import '../utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        value: {
            type: [String, Array, Boolean, Number],
            required: false,
            default: '',
            desc: gettext('下拉框的选中值，可输入 String、Boolean、Number 类型的值，若为多选请输入包含上述类型的数组格式数据')
        },
        items: {
            type: Array,
            required: false,
            default () {
                return [
                    {
                        text: gettext('选项1'),
                        value: 'value1'
                    },
                    {
                        text: gettext('选项2'),
                        value: 'value2'
                    },
                    {
                        text: gettext('选项3'),
                        value: 'value3'
                    }
                ]
            },
            desc: "array like [{text: '', value: ''}, {text: '', value: ''}]"
        },
        multiple: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'set multiple selected items'
        },
        multiple_limit: {
            type: Number,
            required: false,
            default: 0,
            desc: 'limit of selected items when multiple is true'
        },
        remote: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'use remote data or not'
        },
        remote_url: {
            type: String,
            required: false,
            default: '',
            desc: 'remote url when remote is true'
        },
        remote_data_init: {
            type: Function,
            required: false,
            default: function (data) {
                return data
            },
            desc: 'how to process data after getting remote data'
        },
        hasGroup: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'whether the options in group'
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'selector is disabled'
        },
        placeholder: {
            type: String,
            required: false,
            default: '',
            desc: 'placeholder'
        },
        empty_text: {
            type: String,
            required: false,
            default: gettext('无数据'),
            desc: 'tips when data is empty'
        }
    }
    export default {
        name: 'TagSelect',
        mixins: [getFormMixins(attrs)],
        data () {
            return {
                loading: false,
                loading_text: gettext('加载中')
            }
        },
        computed: {
            seletedValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            },
            viewValue () {
                if (Array.isArray(this.seletedValue)) { // 多选
                    if (!this.seletedValue.length) {
                        return '--'
                    }
                    if (this.items.length) {
                        return this.seletedValue.map(val => {
                            return this.filterLabel(val)
                        }).join(',')
                    } else {
                        return this.value.join(',')
                    }
                } else { // 单选
                    if (this.seletedValue === 'undefined') {
                        return '--'
                    }
                    if (this.items.length) {
                        return this.filterLabel(this.seletedValue)
                    } else {
                        return this.value
                    }
                }
            }
        },
        mounted () {
            this.remoteMethod()
        },
        methods: {
            filterLabel (val) {
                let label = val
                this.items.some(item => {
                    if (item.value === val) {
                        label = item.text
                        return true
                    }
                })
                return label
            },
            _set_value (value) {
                this.updateForm(value)
            },
            _get_value () {
                return this.value
            },
            set_loading (loading) {
                this.loading = loading
            },
            remoteMethod () {
                const self = this
                const remote_url = typeof this.remote_url === 'function' ? this.remote_url() : this.remote_url
                if (!remote_url) return

                // 请求远程数据
                this.loading = true
                $.ajax({
                    url: remote_url,
                    method: 'GET',
                    success: function (res) {
                        const data = self.remote_data_init(res) || []

                        self.items = data
                        self.loading = false
                    },
                    error: function (resp) {
                        self.placeholder = gettext('请求数据失败')
                        self.loading = false
                    }
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
    .el-select {
        width: 100%;
        /deep/ .el-input__inner {
            padding-left: 10px;
            height: 32px;
            line-height: 32px;
            font-size: 12px;
        }
    }
</style>
