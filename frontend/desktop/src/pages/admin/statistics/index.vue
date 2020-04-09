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
    <div class="page-statistics">
        <base-title
            type="router"
            :title="i18n.title"
            :tab-list="routers">
            <template v-slot:expand>
                <div class="date-picker">
                    <bk-form form-type="inline">
                        <bk-form-item :label="i18n.dateRange">
                            <bk-date-picker
                                v-model="dateRange"
                                type="daterange"
                                placement="top-end"
                                :clearable="false"
                                @change="onChangeDateRange">
                            </bk-date-picker>
                        </bk-form-item>
                    </bk-form>
                </div>
            </template>
        </base-title>
        <div class="statistics-content">
            <router-view
                :date-range="dateStamp"
                :project-list="projectList"
                :category-list="categoryList">
            </router-view>
        </div>
    </div>
</template>
<script>
    import moment from 'moment'
    import { mapActions, mapState } from 'vuex'
    import '@/utils/i18n.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    const ROUTERS = [
        {
            name: gettext('流程统计'),
            routerName: 'statisticsTemplate'
        },
        {
            name: gettext('任务统计'),
            routerName: 'statisticsInstance'
        },
        {
            name: gettext('标准插件统计'),
            routerName: 'statisticsAtom'
        },
        {
            name: gettext('轻应用统计'),
            routerName: 'statisticsAppmaker'
        }
    ]
    export default {
        name: 'Statistics',
        components: {
            BaseTitle
        },
        data () {
            const format = 'YYYY-MM-DD'
            const defaultDateRange = [moment().subtract(1, 'month').format(format), moment().format(format)]
            return {
                routers: ROUTERS,
                dateRange: defaultDateRange.slice(0),
                i18n: {
                    title: gettext('运营数据'),
                    dateRange: gettext('时间范围')
                }
            }
        },
        computed: {
            ...mapState({
                categorys: state => state.categorys
            }),
            ...mapState('project', {
                projectList: state => state.projectList
            }),
            categoryList () {
                return this.categorys.map(item => {
                    return {
                        id: item.value,
                        name: item.name
                    }
                })
            },
            dateStamp () {
                return this.dateRange.map(item => moment(item).valueOf())
            }
        },
        created () {
            this.getCategorys()
        },
        methods: {
            ...mapActions([
                'getCategorys'
            ]),
            onChangeDateRange (dateRange) {
                this.dateRange = dateRange
            }
        }
    }
</script>
<style lang="scss" scoped>
    .page-statistics {
        padding: 0 60px;
        min-width: 1320px;
        height: 100%;
        background: #f4f7fa;
        .header-wrapper {
            margin: 0 60px 0;
        }
        .statistics-content {
            padding-top: 20px;
        }
        .date-picker {
            height: 60px;
            /deep/ .bk-form-content {
                float: none;
            }
            /deep/ .bk-label {
                height: 60px;
                line-height: 60px;
            }
        }
        /deep/ .statistics-select {
            width: 250px;
        }
        /deep/ .bar-chart-area {
            display: flex;
            justify-content: space-between;
            .horizontal-bar-chart {
                width: 49%;
            }
        }
        /deep/ .tab-content-area {
            margin-top: 20px;
            border-radius: 2px;
            box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.06);
            .bk-tab-section {
                background: #ffffff;
            }
            .tab-data-table {
                margin-top: 20px;
            }
            .table-link {
                color: #3a84ff;
            }
        }
    }
</style>
