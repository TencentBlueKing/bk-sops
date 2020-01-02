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
    <div class="cache-form">
        <bk-button
            theme="default"
            size="small"
            class="delete-btn"
            @click="onDeleteCache">
            {{i18n.delete}}
        </bk-button>
        <table class="form-table">
            <tbody>
                <tr>
                    <th>
                        <div class="form-label required">
                            <label>{{i18n.name}}</label>
                        </div>
                    </th>
                    <td class="value">
                        <div class="form-content">
                            <input
                                type="text"
                                class="cache-name"
                                name="cacheName"
                                :disabled="isEditing"
                                :class="{ 'error-border': errors.first('cacheName') }"
                                v-model="name"
                                v-validate="nameRule"
                                @blur="updateValue">
                            <i class="common-icon-info common-error-tip" v-bk-tooltips.top=" errors.first('cacheName')"></i>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>
                        <div class="form-label required">
                            <label>{{i18n.type}}</label>
                        </div>
                    </th>
                    <td class="value">
                        <div class="form-content">
                            <bk-select
                                v-model="type"
                                class="bk-select-inline"
                                :popover-width="260"
                                :disabled="isEditing"
                                :searchable="true"
                                @selected="onTypeSelect">
                                <bk-option
                                    v-for="(option, index) in list"
                                    :key="index"
                                    :id="option.id"
                                    :name="option.name">
                                </bk-option>
                            </bk-select>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>
                        <div class="form-label">
                            <label>{{i18n.desc}}</label>
                        </div>
                    </th>
                    <td class="value">
                        <div class="form-content">
                            <textarea
                                rows="4"
                                class="cache-desc"
                                v-model="desc"
                                @blur="updateValue">
                            </textarea>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>
                        <div class="form-label">
                            <label>{{i18n.detail}}</label>
                        </div>
                    </th>
                    <td class="value">
                        <table class="detail-table">
                            <tbody>
                                <tr v-for="field in detailFields" :key="field.id">
                                    <th>{{field.name}}</th>
                                    <td class="td-with-input"
                                        :class="{ 'error-border': errors.first('detailValue' + field.id) }">
                                        <input
                                            type="text"
                                            class="table-input"
                                            :name="'detailValue' + field.id"
                                            :placeholder="field.placeholder"
                                            v-model="details[field.id]"
                                            v-validate="valueRule "
                                            @blur="updateValue">
                                        <i class="common-icon-info common-error-tip" v-bk-tooltips.top="i18n.required"></i>
                                        <span
                                            class="common-error-tip error-msg">
                                            {{ i18n.required }}
                                        </span>
                                    </td>

                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { SOURCE_TYPE } from '@/constants/manage.js'
    import { PACKAGE_NAME_REG, STRING_LENGTH } from '@/constants/index.js'

    export default {
        name: 'CacheForm',
        props: {
            value: {
                type: Object,
                default () {
                    return {
                        id: undefined,
                        name: '',
                        type: 's3',
                        desc: '',
                        details: {
                            access_key: '',
                            bucket: '',
                            secret_key: '',
                            service_address: ''
                        }
                    }
                }
            }
        },
        data () {
            const list = this.getCacheTypeList()
            const { id, name, type, desc, details } = this.value
            const [detailFields] = this.getCacheKeys('s3')

            return {
                id,
                name,
                type,
                desc,
                details,
                detailFields,
                list,
                cacheValid: false,
                // 名称校验规则
                nameRule: {
                    required: true,
                    max: STRING_LENGTH.SOURCE_NAME_MAX_LENGTH,
                    regex: PACKAGE_NAME_REG
                },
                valueRule: {
                    required: true
                },
                i18n: {
                    delete: gettext('删除'),
                    name: gettext('名称'),
                    type: gettext('类型'),
                    desc: gettext('描述'),
                    detail: gettext('详细信息'),
                    placeholder: gettext('请输入'),
                    required: gettext('必填项')
                }
            }
        },
        computed: {
            isEditing () {
                return typeof this.value.id === 'number'
            }
        },
        methods: {
            getCacheTypeList () {
                return SOURCE_TYPE.filter(item => item.type !== 'git').map(item => {
                    return {
                        id: item.type,
                        name: item.name
                    }
                })
            },
            getCacheKeys (type) {
                const detailFields = []
                const detailValues = {}

                const source = SOURCE_TYPE.find(item => item.type === type)
                for (const key in source.keys) {
                    detailFields.push({
                        id: key,
                        name: source.keys[key].name,
                        placeholder: source.keys[key].placeholder
                    })
                    detailValues[key] = ''
                }

                return [detailFields, detailValues]
            },
            validate () {
                return this.$validator.validateAll().then(result => {
                    return result
                })
            },
            updateValue () {
                const { id, name, type, desc, details } = this
                const data = {
                    id,
                    name,
                    type,
                    desc,
                    details
                }
                this.$emit('updateCache', data)
            },
            onTypeSelect (type) {
                this.type = type
                const keys = this.getCacheKeys(type)
                this.detailFields = keys[0]
                this.details = keys[1]
                this.updateValue()
            },
            onDeleteCache () {
                this.$emit('deleteCache')
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/input-error.scss';
    /deep/ .bk-select {
        background-color: #ffffff;
        &.is-disabled {
            background-color: #fafafa;
        }
    }
    .cache-form {
        position: relative;
        margin-bottom: 30px;
        padding: 20px;
        background: #f0f1f5;
        border-radius: 2px;
        .form-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            th, td {
                padding: 9px;
            }
            th {
                position: relative;
                width: 16%;
                color: #313238;
                font-weight: 400;
            }
            .form-label {
                padding-right: 20%;
                text-align: right;
                label {
                    position: relative;
                }
                &.required {
                    label:after {
                        content: '*';
                        position: absolute;
                        top: 1px;
                        right: -10px;
                        color: #F00;
                        font-family: "SimSun";
                    }
                }

            }
            .form-content {
                position: relative;
                width: 40%;
            }
            .cache-name {
                padding: 0 10px;
                width: 100%;
                height: 32px;
                line-height: 32px;
                border: 1px solid #c3cdd7;
                border-radius: 2px;
                color: #63656e;
                outline: none;
                &:hover {
                    border-color: #3c96ff;
                }
                &:active {
                    border-color: #3c96ff;
                }
                &[disabled="disabled"] {
                    color: #aaa;
                    cursor: not-allowed;
                    background: #fafafa;
                    &:hover {
                        border-color: #c3cdd7;
                    }
                }
                @include common-input-error;
            }
            .cache-desc {
                display: inline-block;
                padding: 10px;
                width: 100%;
                border: 1px solid #c3cdd7;
                border-radius: 2px;
                color: #63656e;
                outline: none;
                resize: vertical;
                min-height: 102px;
                max-height: 140px;
                &:hover {
                    border-color: #3c96ff;
                }
                &:active {
                    border-color: #3c96ff;
                }
            }
        }
        .detail-table {
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            font-size: 12px;
            th,td {
                position: relative;
                padding: 10px 20px;
                border: 1px solid #dde4eb;
            }
            th {
                width: 30%;
                font-weight: 700;
                text-align: center;
            }
            .td-with-input {
                &:hover {
                    border-style: double;
                    border-color: #3c96ff;
                }
                @include common-input-error;
            }
        }
        .table-input {
            width: 100%;
            color: #333333;
            border: none;
            outline: none;
        }
        .delete-btn {
            position: absolute;
            top: 22px;
            right: 20px;
            padding: 0;
            background: transparent;
            font-size: 12px;
            border: none;
            color: #3a84ff;
        }
    }
</style>
