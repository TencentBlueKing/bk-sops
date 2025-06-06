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
    <div class="horizontal-bar-chart">
        <h3 class="chart-title">{{title}}</h3>
        <bk-form v-if="showForm" class="select-wrapper" form-type="inline">
            <bk-form-item>
                <div class="sort-area">
                    <span>{{ selectedSortType === 'ascending' ? $t('升序') : $t('降序') }}</span>
                    <div class="icon-area" @click="handleSortClick">
                        <span
                            v-for="option in sortList"
                            :key="option.id"
                            :class="['bk-icon', option.clsName, { 'is-select': option.id === selectedSortType }]"
                            :id="option.id">
                        </span>
                    </div>
                </div>
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
                    v-model="selector.selected"
                    @clear="onOptionClick"
                    @selected="onOptionClick(selector.id, $event)">
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
        <div class="content-wrapper" v-bkloading="{ isLoading: dataLoading, opacity: 1, zIndex: 100 }">
            <div class="chart-content">
                <template v-if="dataLoading || sortedData.length > 0">
                    <div
                        v-for="(item, index) in sortedData"
                        class="data-item"
                        :key="index">
                        <span class="data-label" :title="item.name" :style="{ width: `${labelWidth}px` }">{{ item.name }}</span>
                        <div class="data-bar" :style="{ width: `calc(100% - ${labelWidth + 100}px)` }">
                            <div class="block" :style="getBlockStyle(item.value)">
                                <bk-popover ext-cls="task-method" v-if="showPopover" placement="top">
                                    <span
                                        v-for="val in item.create_method"
                                        :key="val.name"
                                        :style="{
                                            display: 'inline-block',
                                            width: getPercentage(val.value, item.value),
                                            height: '100%',
                                            background: item.isTemp ? val.color : creatMethods[val.name].color
                                        }">
                                    </span>
                                    <div slot="content">
                                        <p class="project-name">{{ item.name }}</p>
                                        <ul class="">
                                            <li
                                                class="task-method-item"
                                                v-for="val in item.create_method"
                                                :key="val.name">
                                                <span class="color-block" :style="{ background: item.isTemp ? val.color : creatMethods[val.name].color }"></span>
                                                <span :class="['content-wrap', { 'is-template': item.template_id }]">
                                                    <span class="task-name">{{ item.isTemp ? val.name : creatMethods[val.name].text }}</span>
                                                    <span class="template-id" v-if="item.template_id">
                                                        {{ 'ID: ' + item.template_id }}
                                                    </span>
                                                </span>
                                                <span class="task-num">{{ val.value }}</span>
                                                <span class="percentage" v-if="!item.template_id">{{ '(' + getPercentage(val.value, item.value) + ')' }}</span>
                                            </li>
                                        </ul>
                                    </div>
                                </bk-popover>
                                <span class="num">{{ item.value }}</span>
                            </div>
                        </div>
                    </div>
                </template>
                <NoData
                    v-else
                    :type="isSearch ? 'search-empty' : 'empty'"
                    :message="isSearch ? $t('搜索结果为空') : ''"
                    @searchClear="$emit('onClearChartFilter')">
                </NoData>
            </div>
        </div>
        <div v-if="bizUseageData.total" class="project-statistics">
            <span>{{ $t('总项目') }}</span>
            <span class="num">{{ bizUseageData.total || 0 }}</span>
            <span>{{ $t('正在使用项目') }}</span>
            <span class="num">{{ bizUseageData.count || 0 }}</span>
        </div>
        <div class="view-all-btn" v-if="!dataLoading && sortedData.length > 7" @click="onViewAllClick">{{ $t('查看全部') }}</div>
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
                    <span class="tip-title" :title="item.name" :style="{ width: `${labelWidth}px` }">{{ item.name }}</span>
                    <div class="data-bar" :style="{ width: `calc(100% - ${labelWidth + 100}px)` }">
                        <div class="block" :style="getBlockStyle(item.value)">
                            <span class="num">{{ item.value }}</span>
                        </div>
                    </div>
                </div>
            </div>
            <template v-slot:footer>
                <bk-button theme="default" @click="isDialogShow = false">{{ $t('关闭') }}</bk-button>
            </template>
        </bk-dialog>
    </div>
</template>
<script>
    import NoData from '@/components/common/base/NoData.vue'
    import { COLOR_BLOCK_LIST } from '@/constants/index.js'

    const SORT_LIST = [
        {
            id: 'ascending',
            clsName: 'icon-up-shape'
        },
        {
            id: 'descending',
            clsName: 'icon-down-shape'
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
            colorBlockList: {
                type: Array,
                default () {
                    return []
                }
            },
            bizUseageData: {
                type: Object,
                default () {
                    return {}
                }
            },
            labelWidth: {
                type: Number,
                default: 150
            },
            showPopover: {
                type: Boolean,
                default: false
            },
            showForm: {
                type: Boolean,
                default: true
            }
        },
        data () {
            const creatMethods = COLOR_BLOCK_LIST.reduce((acc, cur) => {
                const { value, color, text } = cur
                acc[value] = { color, text }
                return acc
            }, {})
            return {
                creatMethods,
                sortList: SORT_LIST,
                selectedSortType: 'descending',
                selectedValue: '',
                isDialogShow: false
            }
        },
        computed: {
            totalNumber () {
                return this.dataList.reduce((acc, cur) => Number(acc) + Number(cur.value), 0)
            },
            sortedData () {
                if (this.selectedSortType === 'descending') {
                    return this.dataList.sort((a, b) => b.value - a.value)
                }
                return this.dataList.sort((a, b) => a.value - b.value)
            },
            isSearch () {
                return this.selectorList.some(item => item.selected)
            }
        },
        methods: {
            handleSortClick () {
                this.selectedSortType = this.selectedSortType === 'ascending' ? 'descending' : 'ascending'
            },
            getBlockStyle (val) {
                if (this.totalNumber === 0 || val === 0) {
                    return {
                        width: '1px',
                        background: '#c0c4cc'
                    }
                }
                return {
                    width: val / this.totalNumber * 100 + '%',
                    'min-width': '2px'
                }
            },
            getPercentage (num, total) {
                return (Math.round(num / total * 10000) / 100.00 + '%')
            },
            onOptionClick (selector, id) {
                this.$emit('onFilterClick', id, selector)
            },
            onViewAllClick () {
                this.isDialogShow = true
            },
            handleSearchClear () {
                this.selectorList.forEach(item => {
                    item.selected = false
                })
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
        border-radius: 3px;
        box-shadow: 0px 2px 2px 0px rgba(0,0,0,0.15);
        overflow: hidden;
        margin-bottom: 20px;
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
    .sort-area {
        width: 77px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #63656e;
        font-size: 14px;
        border: 1px solid #c4c6cc;
        border-radius: 3px;
        .icon-area {
            display: flex;
            flex-direction: column;
            justify-content: center;
            font-size: 18px;
            transform: scale(.5);
            color: #979ba5;
            cursor: pointer;
            margin-left: 3px;
            .bk-icon {
                position: relative;
                &.icon-up-shape {
                    top: 5px;
                }
                &.icon-down-shape {
                    bottom: 3px;
                }
            }
            .is-select {
                color: #63656e;
            }
        }
    }
    .content-wrapper {
        margin-top: 28px;
        height: 280px;
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
        display: flex;
        align-items: center;
        border-top: 1px dashed #dcdee5;
        &:last-child {
            border-bottom: 1px dashed #dcdee5;
        }
        &:hover {
            background: #f5f7fa;
        }
    }
    .data-label {
        font-size: 14px;
        color: #737987;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .data-bar {
        display: flex;
        .block {
            position: relative;
            display: flex;
            background: #3a84ff;
            height: 12px;
            ::v-deep .bk-tooltip {
                width: 100%;
                .bk-tooltip-ref {
                    display: flex;
                    height: 100%;
                }
            }
        }
        .num {
            position: absolute;
            top: -2px;
            right: 0;
            padding-left: 10px;
            font-size: 12px;
            color: #63656e;
            transform: translateX(100%);
        }
    }
    .project-statistics {
        position: absolute;
        left: 20px;
        bottom: 10px;
        display: flex;
        align-items: center;
        font-size: 12px;
        color: #979ba5;
        .num {
            color: #63656e;
            margin: 0 17px 0 4px;
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
    }
</style>
