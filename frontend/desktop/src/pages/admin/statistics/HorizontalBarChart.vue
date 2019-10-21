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
        <div class="chart-content" v-bkloading="{ isLoading: dataLoading, opacity: 1 }">
            <template v-if="dataLoading || dataList.length > 0">
                <div
                    v-for="(item, index) in dataList"
                    class="data-item"
                    :key="index">
                    <span class="data-label" :style="{ width: `${labelWidth}px` }">{{ item.name }}</span>
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
</template>
<script>
    import NoData from '@/components/common/base/NoData.vue'

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
                selectedValue: ''
            }
        },
        computed: {
            totalNumber () {
                return this.dataList.reduce((acc, cur) => acc + cur.value, 0)
            }
        },
        methods: {
            getBlockStyle (val) {
                if (this.totalNumber === 0 || val === 0) {
                    return {
                        width: '3px',
                        background: '#c0c4cc'
                    }
                }
                return {
                    width: val / this.totalNumber * 100 + '%'
                }
            },
            onOptionClick (selector, id) {
                this.$emit('onFilterClick', id, selector)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .horizontal-bar-chart {
        position: relative;
        padding: 20px 20px 0;
        height: 340px;
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
    .chart-content {
        margin-top: 28px;
        height: 245px;
        overflow-y: auto;
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
</style>
