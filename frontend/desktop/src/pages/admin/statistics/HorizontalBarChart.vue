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
    <div class="horizontal-bar-chart">
        <h3 class="chart-title">{{title}}</h3>
        <bk-form class="select-wrapper" form-type="inline">
            <bk-form-item>
                <bk-select
                    style="width: 120px"
                    :clearable="false"
                    v-model="selectedSortType">
                    <bk-option
                        v-for="option in sortList"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                        {{option.name}}
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item
                v-for="selector in selectorList"
                :key="selector.id">
                <bk-select
                    class="statistics-select"
                    :searchable="true"
                    :clearable="selector.clearable !== false"
                    :placeholder="selector.placeholder"
                    :disabled="selector.options.length === 0"
                    :value="selector.selected"
                    @change="onOptionClick(selector.id, $event)">
                    <bk-option
                        v-for="option in selector.options"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name">
                        {{option.name}}
                    </bk-option>
                </bk-select>
            </bk-form-item>
        </bk-form>
        <div class="content-wrapper" v-bkloading="{ isLoading: dataLoading, opacity: 1 }">
            <div class="chart-content">
                <template v-if="dataLoading || sortedData.length > 0">
                    <div
                        v-for="(item, index) in sortedData"
                        class="data-item"
                        :key="index">
                        <span class="data-label" :title="item.name" :style="{ width: `${labelWidth}px` }">{{ item.name }}</span>
                        <div class="data-bar" :style="{ width: `calc(100% - ${labelWidth + 100}px)` }">
                            <div class="block" :style="getBlockStyle(item.value)">
                                <span class="num">{{ item.value }}</span>
                            </div>
                        </div>
                    </div>
                </template>
                <no-data v-else></no-data>
            </div>
        </div>
        <div class="view-all-btn" v-if="!dataLoading && sortedData.length > 7" @click="onViewAllClick">{{ i18n.viewAll }}</div>
        <bk-dialog
            v-model="isDialogShow"
            :fullscreen="true"
            :title="title"
            header-position="left"
            :close-icon="false">
            <div class="dialog-content">
                <div
                    v-for="(item, index) in sortedData"
                    class="data-item"
                    :key="index">
                    <span class="data-label" :title="item.name" :style="{ width: `${labelWidth}px` }">{{ item.name }}</span>
                    <div class="data-bar" :style="{ width: `calc(100% - ${labelWidth + 100}px)` }">
                        <div class="block" :style="getBlockStyle(item.value)">
                            <span class="num">{{ item.value }}</span>
                        </div>
                    </div>
                </div>
            </div>
            <template v-slot:footer>
                <bk-button theme="default" @click="isDialogShow = false">{{ i18n.close }}</bk-button>
            </template>
        </bk-dialog>
    </div>
</template>
<script>
    import NoData from '@/components/common/base/NoData.vue'

    const SORT_LIST = [
        {
            id: 'descending',
            name: gettext('降序排列')
        },
        {
            id: 'ascending',
            name: gettext('升序排列')
        }
    ]

    export default {
        name: 'HorizontalBarChart',
        components: {
            NoData
        },
        props: {
            title: {
                type: String,
                default: ''
            },
            selectorList: {
                type: Array,
                default () {
                    return []
                }
            },
            dataLoading: {
                type: Boolean,
                default: false
            },
            dataList: {
                type: Array,
                default () {
                    return []
                }
            },
            labelWidth: {
                type: Number,
                default: 150
            }
        },
        data () {
            return {
                sortList: SORT_LIST,
                selectedSortType: SORT_LIST[0].id,
                selectedValue: '',
                isDialogShow: false,
                i18n: {
                    viewAll: gettext('查看全部'),
                    close: gettext('关闭')
                }
            }
        },
        computed: {
            totalNumber () {
                return this.dataList.reduce((acc, cur) => acc + cur.value, 0)
            },
            sortedData () {
                if (this.selectedSortType === 'descending') {
                    return this.dataList.sort((a, b) => b.value - a.value)
                }
                return this.dataList.sort((a, b) => a.value - b.value)
            }
        },
        methods: {
            getBlockStyle (val) {
                if (this.totalNumber === 0 || val === 0) {
                    return {
                        width: '1px',
                        background: '#c0c4cc'
                    }
                }
                return {
                    width: val / this.totalNumber * 100 + '%'
                }
            },
            onOptionClick (selector, id) {
                this.$emit('onFilterClick', id, selector)
            },
            onViewAllClick () {
                this.isDialogShow = true
            }
        }
    }
</script>
<style lang="scss" scoped>
    .horizontal-bar-chart {
        position: relative;
        padding: 20px;
        height: 360px;
        background: #ffffff;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.06);
        overflow: hidden;
    }
    .chart-title {
        margin: 0;
        font-size: 14px;
    }
    .select-wrapper {
        position: absolute;
        top: 14px;
        right: 20px;
    }
    .content-wrapper {
        margin-top: 28px;
        height: 245px;
    }
    .chart-content {
        height: 100%;
        overflow-y: auto;
        &.loading {
            overflow: hidden;
        }
    }
    .data-item {
        height: 34px;
        line-height: 34px;
        border-top: 1px dashed #dcdee5;
        &:last-child {
            border-bottom: 1px dashed #dcdee5;
        }
    }
    .data-label {
        display: inline-block;
        font-size: 14px;
        color: #737987;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .data-bar {
        display: inline-block;
        vertical-align: top;
        .block {
            position: relative;
            display: inline-block;
            background: #3a84ff;
            height: 12px;
        }
        .num {
            position: absolute;
            top: -10px;
            right: 0;
            padding-left: 10px;
            font-size: 12px;
            color: #63656e;
            transform: translateX(100%);
        }
    }
    .view-all-btn {
        position: absolute;
        right: 20px;
        bottom: 10px;
        font-size: 14px;
        color: #3a84ff;
        cursor: pointer;
    }
    .dialog-content {
        margin: 0 auto;
        padding: 30px;
        width: 1000px;
        height: 100%;
        overflow-y: auto;
    }
</style>
