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
    <div class="tag-cascader">
        <div v-if="formMode">
            <el-cascader
                v-model="seletedValue"
                :options="items"
                :disabled="!editable || disabled"
                :props="{
                    multiple,
                    lazy,
                    lazyLoad: lazyload.bind(this)
                }"
                :filterable="filterable">
            </el-cascader>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{viewValue}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        items: {
            type: Array,
            required: true,
            default () {
                return [
                    {
                        label: gettext('一级分组1'),
                        value: 'group1',
                        children: [
                            {
                                label: gettext('二级分组1'),
                                value: 'subgroup1',
                                children: [
                                    {
                                        label: gettext('三级分组1'),
                                        value: 'sub1'
                                    },
                                    {
                                        label: gettext('三级分组2'),
                                        value: 'sub2'
                                    }
                                ]
                            },
                            {
                                label: gettext('二级分组2'),
                                value: 'subgroup2',
                                children: [
                                    {
                                        label: gettext('三级分组3'),
                                        value: 'sub3'
                                    },
                                    {
                                        label: gettext('三级分组4'),
                                        value: 'sub4'
                                    },
                                    {
                                        label: gettext('三级分组5'),
                                        value: 'sub5'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        label: gettext('一级分组2'),
                        value: 'group2',
                        children: [
                            {
                                label: gettext('二级分组3'),
                                value: 'subgroup3',
                                children: [
                                    {
                                        label: gettext('三级分组6'),
                                        value: 'sub6'
                                    },
                                    {
                                        label: gettext('三级分组7'),
                                        value: 'sub7'
                                    }
                                ]
                            },
                            {
                                label: gettext('二级分组4'),
                                value: 'subgroup4',
                                children: [
                                    {
                                        label: gettext('三级分组8'),
                                        value: 'sub8'
                                    },
                                    {
                                        label: gettext('三级分组9'),
                                        value: 'sub9'
                                    },
                                    {
                                        label: gettext('三级分组10'),
                                        value: 'sub10'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            desc: "array like [{label: '', value: '', children: [...]}, {label: '', value: '', children: [...]}]"
        },
        value: {
            type: [Array, String],
            required: false,
            default () {
                return []
            },
            desc: gettext('级联选择器的选中值')
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: gettext('禁用选择器')
        },
        multiple: {
            type: Boolean,
            required: false,
            default: true,
            desc: gettext('设置是否可多选')
        },
        filterable: {
            type: Boolean,
            required: false,
            default: true,
            desc: gettext('设置是否可搜索')
        },
        placeholder: {
            type: String,
            required: false,
            default: gettext('请输入'),
            desc: 'placeholder'
        },
        lazy: {
            type: Boolean,
            required: false,
            default: true,
            desc: gettext('是否开启远程加载')
        },
        lazyLoad: {
            type: Function,
            required: false,
            default: function (node, resolve) {
                setTimeout(() => {
                    resolve([])
                }, 500)
            },
            desc: gettext('远程加载方法, 文档参考element-ui cascader组件lazyload说明')
        }
    }

    export default {
        name: 'TagCascader',
        mixins: [getFormMixins(attrs)],
        data () {
            return {}
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
                if (this.multiple) {
                    return this.value.map(value => {
                        return this.transValToText(value)
                    }).join('，')
                } else {
                    return this.transValToText(this.value)
                }
            }
        },
        methods: {
            transValToText (value) {
                let options = this.items.slice(0)
                return value.map(val => {
                    const item = options.find(item => item.value === val)
                    if (item) {
                        if (item.children) {
                            options = item.children.slice(0)
                        }
                        return item.label
                    }
                    return ''
                }).join('/')
            }
        }
    }
</script>
<style lang="scss" scoped>
    /deep/ .el-cascader {
        width: 100%;
        line-height: 32px;
        .el-cascader__search-input,
        .el-input__inner {
            font-size: 12px;
        }
    }
</style>
