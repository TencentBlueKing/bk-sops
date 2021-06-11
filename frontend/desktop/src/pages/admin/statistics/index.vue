/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-statistics" v-bkloading="{ isLoading: hasStatisticsPerm === null, opacity: 0, zIndex: 100 }">
        <template v-if="hasViewPerm">
            <page-header :tab-list="routers">
                <template v-slot:expand>
                    <div class="date-picker">
                        <bk-form form-type="inline">
                            <bk-form-item :label="$t('时间范围')">
                                <bk-date-picker
                                    :value="dateRange"
                                    type="daterange"
                                    placement="top-end"
                                    :clearable="false"
                                    @change="onChangeDateRange">
                                </bk-date-picker>
                            </bk-form-item>
                        </bk-form>
                    </div>
                </template>
            </page-header>
            <div class="statistics-content">
                <router-view
                    :date-range="dateStamp"
                    :project-list="projectList"
                    :category-list="categoryList">
                </router-view>
            </div>
        </template>
    </div>
</template>
<script>
    import moment from 'moment'
    import { mapActions, mapState } from 'vuex'
    import bus from '@/utils/bus.js'
    import i18n from '@/config/i18n/index.js'
    import PageHeader from '@/components/layout/PageHeader.vue'

    const ROUTERS = [
        {
            name: i18n.t('流程统计'),
            routerName: 'statisticsTemplate'
        },
        {
            name: i18n.t('任务统计'),
            routerName: 'statisticsInstance'
        },
        {
            name: i18n.t('标准插件统计'),
            routerName: 'statisticsAtom'
        },
        {
            name: i18n.t('轻应用统计'),
            routerName: 'statisticsAppmaker'
        }
    ]
    export default {
        name: 'Statistics',
        components: {
            PageHeader
        },
        data () {
            const format = 'YYYY-MM-DD'
            const defaultDateRange = [moment().subtract(1, 'month').format(format), moment().format(format)]
            return {
                hasViewPerm: false,
                routers: ROUTERS,
                dateRange: defaultDateRange.slice(0),
                projectList: []
            }
        },
        computed: {
            ...mapState({
                hasStatisticsPerm: state => state.hasStatisticsPerm,
                permissionMeta: state => state.permissionMeta,
                categorys: state => state.categorys
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
        watch: {
            hasStatisticsPerm (val) {
                if (val !== null) {
                    if (val) {
                        this.hasViewPerm = true
                        this.getProjectList()
                        this.getCategorys()
                    } else {
                        this.showPermissionApplyPage()
                    }
                }
            }
        },
        mounted () {
            if (this.hasStatisticsPerm !== null) {
                if (this.hasStatisticsPerm === false) {
                    this.showPermissionApplyPage()
                } else {
                    this.hasViewPerm = true
                    this.getProjectList()
                    this.getCategorys()
                }
            }
        },
        methods: {
            ...mapActions([
                'getCategorys'
            ]),
            ...mapActions('project', [
                'loadUserProjectList'
            ]),
            /**
             * 切换到权限申请页
             */
            showPermissionApplyPage () {
                const action = 'statistics_view'
                const bksops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                const name = this.permissionMeta.actions.find(item => item.id === action).name
                const { id: systemId, name: systemName } = bksops
                const permissions = {
                    system_id: systemId,
                    system_name: systemName,
                    actions: [{
                        id: action,
                        name,
                        related_resource_types: []
                    }]
                }

                bus.$emit('togglePermissionApplyPage', true, 'other', permissions)
            },
            async getProjectList () {
                this.loading = true

                try {
                    const res = await this.loadUserProjectList({ limit: 0 })
                    this.projectList = res.objects
                } catch (e) {
                    console.log(e)
                } finally {
                    this.loading = false
                }
            },
            onChangeDateRange (dateRange) {
                this.dateRange = dateRange
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';

    .page-statistics {
        height: calc(100vh - 52px);
        background: #f4f7fa;
        .statistics-content {
            padding: 20px 24px;
            height: calc(100vh - 100px);
            overflow: auto;
            @include scrollbar;
        }
        .date-picker {
            margin-top: 8px;
            padding-right: 26px;
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
