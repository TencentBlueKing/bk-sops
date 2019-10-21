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
        <navi-header
            :routers="routers"
            :title="i18n.title"
            :show-date-picker="true"
            :date-range="defaultDateRange"
            @changeDateRange="changeDateRange">
        </navi-header>
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
    import NaviHeader from '../common/NaviHeader.vue'

    const ROUTERS = [
        {
            text: gettext('流程统计'),
            name: 'statisticsTemplate',
            path: '/admin/statistics/template/'
        },
        {
            text: gettext('任务统计'),
            name: 'statisticsInstance',
            path: '/admin/statistics/instance/'
        },
        {
            text: gettext('标准插件统计'),
            name: 'statisticsAtom',
            path: '/admin/statistics/atom/'
        },
        {
            text: gettext('轻应用统计'),
            name: 'statisticsAppmaker',
            path: '/admin/statistics/appmaker/'
        }
    ]
    export default {
        name: 'Statistics',
        components: {
            NaviHeader
        },
        data () {
            const format = 'YYYY-MM-DD'
            const defaultDateRange = [moment().subtract(1, 'month').format(format), moment().format(format)]
            return {
                routers: ROUTERS,
                defaultDateRange,
                dateRange: defaultDateRange.slice(0),
                i18n: {
                    title: gettext('运营数据')
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
            changeDateRange (dateRange) {
                this.dateRange = dateRange
            }
        }
    }
</script>
<style lang="scss" scoped>
    .page-statistics {
        min-width: 1320px;
        height: 100%;
        background: #f4f7fa;
        .header-wrapper {
            margin: 0 60px 0;
        }
        .statistics-content {
            padding: 20px 60px 60px;
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
