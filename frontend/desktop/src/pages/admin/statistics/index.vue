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
        <div class="header-wrapper">
            <div class="nav-content clearfix">
                <div class="nav-title">
                    <h3>{{i18n.operationData}}</h3>
                </div>
                <div class="data-dimension">
                    <router-link
                        v-for="dms in dataDimension"
                        :key="dms.name"
                        :class="['dms-item', { 'active': $route.name === dms.name }]"
                        :to="dms.path">
                        {{dms.text}}
                    </router-link>
                </div>
                <div class="nav-date-range">
                    <label class="content-detail-label">{{i18n.timeLimit}}</label>
                    <bk-date-picker
                        v-model="timeRange"
                        :clearable="false"
                        type="daterange"
                        placement="top-end"
                        @change="onChangeTimeRange">
                    </bk-date-picker>
                </div>
            </div>
        </div>
        <div class="statistics-content">
            <div class="content-wrapper" v-if="reloadComponent">
                <router-view :time-range="timeRange"></router-view>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import moment from 'moment-timezone'
    const DATA_DIMENSION = [
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
        data () {
            return {
                dataDimension: DATA_DIMENSION,
                i18n: {
                    operationData: gettext('运营数据'),
                    timeLimit: gettext('时间范围')
                },
                path: this.$router.currentRoute.path,
                reloadComponent: true,
                timeRange: ['', '']
            }
        },
        watch: {
            '$route' (to, from) {
                this.reloadComponent = false
                this.path = this.$router.currentRoute.path
                this.reloadComponent = true
            }
        },
        created () {
            this.getTimeRange()
        },
        methods: {
            onGotoPath (path) {
                this.$router.push(path)
            },
            onChangeTimeRange (value) {
                this.timeRange = value
            },
            getTimeRange () {
                const date = new Date()
                this.timeRange[1] = moment(date).format('YYYY-MM-DD HH:mm:ss')
                date.setTime(date.getTime() - 3600 * 1000 * 24 * 30)
                this.timeRange[0] = moment(date).format('YYYY-MM-DD HH:mm:ss')
            }
        }
    }
</script>
<style lang="scss">
@import "@/scss/config.scss";
@import "@/scss/datastatistics/datastatistics.scss";
.page-statistics {
    .header-wrapper {
        margin-bottom: 20px;
        padding: 0px 60px 0 60px;
        min-width: 1320px;
    }
    .nav-content {
        border-bottom: 1px solid #dde4eb;
        .nav-title {
            float: left;
            margin-right: 20px;
            padding: 20px 0;
            h3 {
                margin: 0;
                padding: 0 25px 0 12px;
                border-right: 1px solid #c4c6cc;
                border-left: 2px solid #a3c5fd;
                height: 20px;
                line-height: 20px;
                font-size: 14px;
                font-weight: bold;
                color: #313238;
            }
        }
        .data-dimension {
            float: left;
            .dms-item {
                display: inline-block;
                margin-right: 34px;
                height: 60px;
                line-height: 60px;
                font-size: 14px;
                color: #63656E;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
                &.active {
                    color: #3a84ff;
                    border-bottom: 2px solid #3a84ff;
                }
            }
        }
        .nav-date-range {
            font-size: 14px;
            float: right;
            margin: 15px 0 0 0;
            .bk-date-picker {
                width: 201px;
                margin-left: 20px;
            }
        }
    }
    .statistics-content {
        padding: 0 60px;
        .template-router {
            color: #3a84ff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    }
}
</style>
