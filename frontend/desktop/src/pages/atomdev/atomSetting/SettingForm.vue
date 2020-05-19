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
    <div class="setting-form">
        <i v-if="showClose" class="delete-icon common-icon-close" @click="$emit('delete')"></i>
        <bk-form :model="formValue" ref="settingForm">
            <bk-form-item
                v-for="(item, index) in setting"
                :key="index"
                :label="item.name"
                :label-width="item.props && item.props.hasOwnProperty('labelWidth') ? labelWidth : 120"
                :required="item.required"
                :rules="rules[item.name]"
                :property="item.name">
                <component
                    v-if="item.comp !== 'bk-select'"
                    :is="item.comp"
                    v-bind="item.props"
                    v-model="formValue[item.name]"
                    @change="onFormChange($event, item.name)">
                </component>
                <bk-select
                    v-else
                    v-bind="item.props"
                    v-model="formValue[item.name]"
                    style="background: #ffffff"
                    @change="onFormChange($event, item.name)">
                    <bk-option
                        v-for="option in item.props.list"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                    </bk-option>
                </bk-select>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import tools from '@/utils/tools.js'

    export default {
        name: 'SettingForm',
        props: {
            setting: {
                type: Array,
                default () {
                    return []
                }
            },
            value: {
                type: Object,
                default () {
                    return {}
                }
            },
            rules: {
                type: Object,
                default () {
                    return {}
                }
            },
            showClose: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                formValue: tools.deepClone(this.value)
            }
        },
        watch: {
            value (val) {
                this.formValue = tools.deepClone(val)
            }
        },
        methods: {
            validate () {
                return this.$refs.settingForm.validate()
            },
            onFormChange (val, name) {
                this.formValue[name] = val
                this.$emit('change', tools.deepClone(this.formValue))
            }
        }
    }
</script>
<style lang="scss" scoped>
    .setting-form {
        position: relative;
        &:hover {
            .delete-icon {
                display: inline-block;
            }
        }
    }
    .delete-icon {
        display: none;
        position: absolute;
        top: 8px;
        right: 8px;
        font-size: 12px;
        color: #3a84ff;
        cursor: pointer;
    }
</style>
