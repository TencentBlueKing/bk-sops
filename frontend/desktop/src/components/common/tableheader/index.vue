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
    <div class="table-header">
        <div class="operation-area clearfix">
            <div class="operation-btn">
                <slot name="operation"></slot>
            </div>
            <div class="template-advanced-search">
                <advance-search
                    v-if="isShowSearch"
                    @input="onSearchInput"
                    @onShow="onAdvanceShow"
                    :input-placeholader="searchConfig.placeholder"
                >
                </advance-search>
            </div>
        </div>
        <div class="advanced-search-form" v-if="isAdvancedSerachShow">
            <bk-form form-type="inline">
                <bk-form-item
                    v-for="(item, index) in searchForm"
                    :key="index"
                    :label="item.label">
                    <template v-if="item.type === 'select'">
                        <bk-select
                            style="width: 260px;"
                            :placeholder="item.placeholder"
                            :loading="item.loading"
                            :clearable="true"
                            :searchable="true"
                            v-model="formData[item.key]"
                            @clear="onClearFormItem(item.key)"
                            @change="onChangeFormItem($event, item.key)">
                            <bk-option
                                v-for="(option, i) in item.list"
                                :key="i"
                                :id="option.value"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </template>
                    <template v-if="item.type === 'dateRange'">
                        <bk-date-picker
                            v-model="formData[item.key]"
                            :type="'daterange'"
                            :placeholder="item.placeholder"
                            @change="onChangeFormItem($event, item.key)">
                        </bk-date-picker>
                    </template>
                    <template v-if="item.type === 'input'">
                        <bk-input
                            style="width: 260px;"
                            class="search-input"
                            v-model="formData[item.key]"
                            :placeholder="item.placeholder">
                        </bk-input>
                    </template>
                </bk-form-item>
                <bk-form-item class="query-button">
                    <bk-button class="query-primary" theme="primary" @click.prevent="submit">{{i18n.query}}</bk-button>
                    <bk-button class="query-cancel" @click.prevent="onResetForm">{{i18n.reset}}</bk-button>
                </bk-form-item>
            </bk-form>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import AdvanceSearch from './AdvanceSearch.vue'
    export default {
        name: 'TableHeader',
        components: {
            AdvanceSearch
        },
        props: {
            isShowSearch: {
                type: Boolean,
                default: true
            },
            searchConfig: {
                type: Object,
                default: () => ({
                    placeholder: gettext('请输入')
                })
            },
            searchForm: {
                type: Array,
                default: () => ([
                    {
                        type: 'select',
                        label: '分类',
                        key: 'mySelect',
                        list: [
                            {
                                name: '1111',
                                list: '22'
                            }
                        ]
                    },
                    {
                        type: 'dateRange',
                        key: 'myDate',
                        label: '更新时间'
                    },
                    {
                        type: 'input',
                        key: 'myInput',
                        label: '创建人',
                        value: ''
                    }
                    
                ])
            }
        },
        data () {
            return {
                i18n: {
                    query: gettext('搜索'),
                    reset: gettext('清空')
                },
                isAdvancedSerachShow: true,
                searchValue: '',
                formData: {}
            }
        },
        created () {
            this.searchForm.forEach(m => {
                this.formData[m.key] = ''
            })
            console.log(this.formData, '进入')
        },
        methods: {
            onSearchInput (val) {
                this.$emit('onSearchInput', val)
            },
            onAdvanceShow () {
                this.isAdvancedSerachShow = !this.isAdvancedSerachShow
            },
            onButtonClick (emitName) {
                this.$emit(emitName)
            },
            onClearFormItem (key) {
                this.formData[key] = ''
            },
            onChangeFormItem (val, key) {
                this.formData[key] = val
            },
            submit () {
                this.$emit('submit', this.formData)
            },
            onResetForm () {
                this.isAdvancedSerachShow = false
                Object.keys(this.formData).forEach(key => {
                    this.$set(this.formData, key, '')
                })
                this.$nextTick(() => {
                    this.isAdvancedSerachShow = true
                    this.$emit('submit', this.formData)
                })
            }
        }
    }
</script>

<style lang='scss'>
@import '@/scss/config.scss';
.table-header {
    width: 100%;
    .operation-area {
        margin: 20px 0;
        .operation-btn {
            float: left;
        }
        .template-advanced-search {
            float: right;
            .base-search {
                margin: 0px;
            }
        }
    }
    .advanced-search-form {
        margin-bottom: 20px;
        padding: 0px 30px 20px;
        background: #ffffff;
        border: 1px solid #dde4eb;
        border-radius: 2px;
        /deep/.bk-form-item {
            margin: 20px 20px 0 0 !important;
            .bk-label {
                min-width: 100px !important;
            }
        }
        .query-button {
            padding-left: 24px;
            .query-cancel {
                margin-left: 5px;
            }
        }
    }
}
</style>
