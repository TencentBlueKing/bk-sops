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
    <div class="cache-edit">
        <div class="cache-content">
            <h3 class="edit-title">step2.{{ i18n.setting + i18n.cache }}</h3>
            <div class="cache-setting">
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
                                        v-model="name"
                                        v-validate="nameRule"
                                        @blur="updateValue">
                                    <span
                                        v-show="errors.has('cacheName')"
                                        class="common-error-tip error-msg">
                                        {{ errors.first('cacheName') }}
                                    </span>
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
                                    <bk-selector
                                        :list="list"
                                        :selected="type"
                                        :disabled="isEditing"
                                        @item-selected="onTypeSelect">
                                    </bk-selector>
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
                                            <td>
                                                <input
                                                    type="text"
                                                    class="table-input"
                                                    :placeholder="i18n.placeholder"
                                                    v-model="details[field.id]"
                                                    @blur="updateValue">
                                            </td>
                                            
                                        </tr>
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="operate-area">
            <router-link to="/admin/manage/source_edit/package_edit/" class="bk-button bk-default">{{ i18n.prevStep }}</router-link>
            <bk-button
                type="success"
                class="save-btn"
                :loading="pending"
                @click="onSaveSetting">
                {{ i18n.save }}
            </bk-button>
            <router-link to="/admin/manage/source_manage/" class="bk-button bk-default">{{ i18n.cancel }}</router-link>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { SOURCE_TYPE } from '@/constants/manage.js'
    import { VAR_REG, STRING_LENGTH } from '@/constants/index.js'

    export default {
        name: 'CacheEdit',
        props: {
            cacheList: {
                type: Array,
                default () {
                    return [{
                        name: '',
                        type: 'git',
                        desc: '',
                        details: {
                            access_key: '',
                            bucket: '',
                            secret_key: '',
                            service_address: ''
                        }
                    }]
                }
            },
            pending: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const list = this.getCacheTypeList()
            const { name, type, desc, details, detailFields } = this.getCacheDataFromProps()
            
            return {
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
                    regex: VAR_REG
                },
                i18n: {
                    setting: gettext('配置'),
                    cache: gettext('本地缓存'),
                    prevStep: gettext('上一步'),
                    save: gettext('完成'),
                    cancel: gettext('取消'),
                    name: gettext('名称'),
                    type: gettext('类型'),
                    desc: gettext('描述'),
                    detail: gettext('详细信息'),
                    placeholder: gettext('请输入')
                }
            }
        },
        computed: {
            isEditing () {
                return this.cacheList.length > 0 && typeof this.cacheList[0].id === 'number'
            }
        },
        watch: {
            cacheList: {
                handler (value) {
                    const { name, type, desc, details, detailFields } = this.getCacheDataFromProps()
                    this.name = name
                    this.type = type
                    this.desc = desc
                    this.details = details
                    this.detailFields = detailFields
                },
                deep: true
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
            getCacheDataFromProps () {
                const cache = this.cacheList.length > 0 ? this.cacheList[0] : [{}]
                const {
                    name = '',
                    type = 's3',
                    desc = '',
                    details = {
                        access_key: '',
                        bucket: '',
                        secret_key: '',
                        service_address: ''
                    }
                } = cache
                const [detailFields] = this.getCacheKeys(type)

                return { name, type, desc, details, detailFields }
            },
            getCacheKeys (type) {
                const detailFields = []
                const detailValues = {}

                const source = SOURCE_TYPE.find(item => item.type === type)
                for (const key in source.keys) {
                    detailFields.push({
                        id: key,
                        name: source.keys[key]
                    })
                    detailValues[key] = ''
                }
                
                return [detailFields, detailValues]
            },
            updateValue () {
                const data = [{
                    name: this.name,
                    type: this.type,
                    desc: this.desc,
                    details: this.details
                }]
                this.$emit('updateList', 'cacheList', data)
            },
            onTypeSelect (type) {
                this.type = type
                const keys = this.getCacheKeys(type)
                this.detailFields = keys[0]
                this.details = keys[1]
                this.updateValue()
            },
            onSaveSetting () {
                this.$validator.validateAll().then(result => {
                    if (result) {
                        this.$emit('saveSetting')
                    }
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
    .cache-edit {
        height: calc(100% - 60px);
        background: #ffffff;
    }
    .cache-content {
        padding: 30px 60px 60px;
        min-height: 100%;
    }
    .edit-title {
        margin: 0 0 30px;
        font-size: 20px;
    }
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
            padding: 10px 20px;
            border: 1px solid #dde4eb;
        }
        th {
            width: 30%;
            font-weight: 700;
            text-align: center;
        }
    }
    .table-input {
        width: 100%;
        color: #63656e;
        border: none;
        outline: none;
    }
    .operate-area {
        margin-top: -60px;
        padding: 0 60px;
        height: 60px;
        line-height: 60px;
        border-top: 1px solid #cacedb;
        .bk-button {
            height: 32px;
            line-height: 32px;
            &:not(:last-child) {
                margin-right: 6px;
            }
        }
        .save-btn {
            width: 140px;
        }
    }
    .common-error-tip {
        position: absolute;
        bottom: -15px;
        left: 0;
        font-size: 12px;
        white-space: nowrap;
    }
</style>
