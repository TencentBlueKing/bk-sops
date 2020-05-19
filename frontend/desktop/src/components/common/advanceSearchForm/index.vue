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
    <div class="advance-search-wrapper">
        <div class="operation-area clearfix">
            <div class="operation-btn">
                <slot name="operation"></slot>
            </div>
            <advance-search
                v-if="isShowSearch"
                @input="onSearchInput"
                @onShow="onAdvanceOpen"
                :is-advance-open.sync="isAdvanceOpen"
                :value="searchConfig.value"
                :input-placeholader="searchConfig.placeholder">
                <template slot="extend">
                    <slot name="search-extend"></slot>
                </template>
            </advance-search>
        </div>
        <div class="advanced-search-form" v-if="isAdvanceOpen">
            <bk-form form-type="inline" :model="formData">
                <bk-form-item
                    v-for="item in searchForm"
                    :key="item.key"
                    :property="item.key"
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
                                v-for="option in item.list"
                                :key="option.value"
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
                            v-model.trim="formData[item.key]"
                            :placeholder="item.placeholder">
                        </bk-input>
                    </template>
                </bk-form-item>
                <bk-form-item class="query-button">
                    <bk-button class="query-primary" theme="primary" @click.prevent="submit">{{$t('搜索')}}</bk-button>
                    <bk-button class="query-cancel" @click.prevent="onResetForm">{{$t('清空')}}</bk-button>
                </bk-form-item>
            </bk-form>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import AdvanceSearch from './AdvanceSearch.vue'
    export default {
        name: 'AdvanceSearchForm',
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
                    placeholder: i18n.t('请输入'),
                    value: ''
                })
            },
            searchForm: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                isAdvanceOpen: false,
                searchValue: '',
                formData: {}
            }
        },
        created () {
            this.searchForm.forEach(m => {
                this.$set(this.formData, m.key, '')
            })
        },
        methods: {
            onSearchInput (val) {
                this.$emit('onSearchInput', val)
            },
            onAdvanceOpen (val) {
                this.isAdvanceOpen = val === undefined ? !this.isAdvanceOpen : val
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
                Object.keys(this.formData).forEach(key => {
                    this.$set(this.formData, key, '')
                })
                this.$emit('submit', this.formData)
            }
        }
    }
</script>

<style lang='scss' scoped>
@import '@/scss/config.scss';
.advance-search-wrapper {
    width: 100%;
    .operation-area {
        margin: 20px 0;
        .operation-btn {
            float: left;
        }
    }
    .advanced-search-form {
        margin-bottom: 20px;
        padding: 0px 30px 20px;
        background: #ffffff;
        border: 1px solid #dde4eb;
        border-radius: 2px;
        /deep/ .bk-form-item {
            float: left;
            height: 32px;
            margin-top: 20px !important;
            margin-left: 8px;
            .bk-label {
                min-width: 160px !important;
            }
        }
        .query-button {
            margin-left: 168px;
            .query-cancel {
                margin-left: 5px;
            }
        }
    }
}
</style>
