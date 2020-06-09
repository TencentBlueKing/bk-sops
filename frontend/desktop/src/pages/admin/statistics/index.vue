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
    <div class="page-statistics" v-bkloading="{ isLoading: permissionLoading, opacity: 0 }">
        <template v-if="hasViewPerm">
            <base-title
                type="router"
                :title="$t('运营数据')"
                :tab-list="routers">
                <template v-slot:expand>
                    <div class="date-picker">
                        <bk-form form-type="inline">
                            <bk-form-item :label="$t('时间范围')">
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
        </template>
    </div>
</template>
<script>
    import moment from 'moment'
    import { mapActions, mapState } from 'vuex'
    import bus from '@/utils/bus.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import i18n from '@/config/i18n/index.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'

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
            BaseTitle
        },
        data () {
            const format = 'YYYY-MM-DD'
            const defaultDateRange = [moment().subtract(1, 'month').format(format), moment().format(format)]
            return {
                permissionLoading: true,
                hasViewPerm: false,
                routers: ROUTERS,
                dateRange: defaultDateRange.slice(0)
            }
        },
        computed: {
            ...mapState({
                permissionMeta: state => state.permissionMeta,
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
        async created () {
            await this.queryViewPerm()
            this.getCategorys()
        },
        methods: {
            ...mapActions([
                'queryUserPermission',
                'getCategorys'
            ]),
            // 查询用户是否有运营数据查看权限
            async queryViewPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'statistics_view'
                    })
                    if (res.data.is_allow) {
                        this.permissionLoading = false
                        this.hasViewPerm = true
                    } else {
                        this.showPermissionApplyPage()
                    }
                } catch (error) {
                    errorHandler(error, this)
                }
            },
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
