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
    <div class="content-process-detail">
        <bk-tab :type="'card'" :active="active" @tab-change="onTabChange">
            <bk-tab-panel
                v-for="panel in panels"
                :key="panel.label"
                :name="panel.name"
                :label="panel.label">
                <div class="content-wrap-detail">
                    <div class="content-wrap-from">
                        <div
                            v-for="select in panel.selects"
                            :key="select.label"
                            class="content-wrap-select">
                            <label class="content-detail-label">{{select.label}}</label>
                            <bk-select
                                v-model="select.model"
                                class="bk-select-inline"
                                :popover-width="260"
                                :searchable="select.searchable"
                                :clearable="select.clearable"
                                :placeholder="select.placeholder"
                                @clear="select.onClear"
                                @selected="select.onSelected">
                                <bk-option
                                    v-for="option in select.options"
                                    :key="option[select.option.key]"
                                    :id="option[select.option.key]"
                                    :name="option[select.option.name]">
                                </bk-option>
                            </bk-select>
                        </div>
                    </div>
                    <data-table-pagination
                        :data="panel.data"
                        :total="panel.total"
                        :pagination="panel.pagination"
                        :columns="panel.columns"
                        :loading="panel.loading"
                        @handleSortChange="panel.handleSortChange"
                        @handleSizeChange="panel.handleSizeChange"
                        @handleIndexChange="panel.handleIndexChange">
                    </data-table-pagination>
                </div>
            </bk-tab-panel>
        </bk-tab>
    </div>
</template>
<script>
    import DataTablePagination from '@/components/common/dataTable/DataTablePagination.vue'

    export default {
        name: 'TablePanel',
        components: {
            DataTablePagination
        },
        props: ['tabpanels'],
        computed: {
            panels () {
                return this.tabpanels.panels
            },
            onTabChange () {
                return this.tabpanels.onTabChange
            },
            active () {
                return this.tabpanels.active
            }
        }
    }

</script>
<style lang="scss">
</style>
