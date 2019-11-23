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
    <div class="search-result">
        <div class="search-input">
            <bk-input v-model="searchStr" right-icon="bk-icon icon-search" @change="onSearch"></bk-input>
        </div>
        <div class="result-wrapper" v-bkloading="{ isLoading: searchLoading, opacity: 1 }">
            <div class="result-title">
                <h3>{{ i18n.resultTitle }}</h3>
                <span>{{ i18n.find }}</span>{{ matchedList.length }}<span>{{ i18n.result }}</span>
            </div>
            <template v-if="matchedList.length">
                <div class="list-table template-list-table">
                    <bk-table
                        v-bkloading="{ isLoading: tplDataLoading, opacity: 1 }"
                        :data="tplData"
                        :pagination="tplPagination"
                        @sort-change="handleSortChange('tpl')"
                        @page-change="handlePageChange('tpl')">
                        <bk-table-column
                            v-for="col in tplListColumn"
                            :key="col.props"
                            :label="col.label"
                            :prop="col.prop"
                            :width="col.hasOwnProperty('width') ? col.width : 'auto'"
                            :sortable="col.sortable">
                            <template slot-scope="props">
                                <a
                                    v-if="col.prop === 'name'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.name"
                                    :href="`${site_url}template/edit/${props.row.project.cmdb_biz_id}/?template_id=${props.row.id}`">
                                    {{props.row.templateName}}
                                </a>
                                <template v-else-if="col.prop === 'projectName'">
                                    <span>{{ props.row.project.name }}</span>
                                </template>
                                <template v-else-if="col.prop === 'is_deleted'">
                                    <span>{{ props.row.is_deleted ? i18n.yes : i18n.no }}</span>
                                </template>
                                <template v-else-if="col.prop === 'operation'">
                                    <span v-if="props.row.is_deleted" @click="onRestoreTemplate(props.row)">{{ i18n.restore }}</span>
                                    <a
                                        v-else
                                        class="table-link"
                                        target="_blank"
                                        :href="`${site_url}template/edit/${props.row.project.cmdb_biz_id}/?template_id=${props.row.id}`">
                                        {{ i18n.edit }}
                                    </a>
                                </template>
                                <template v-else>{{ props.row[col.prop] }}</template>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </div>
                <div class="list-table task-list-table">
                    <bk-table
                        v-bkloading="{ isLoading: taskDataLoading, opacity: 1 }"
                        :data="taskData"
                        :pagination="taskPagination"
                        @sort-change="handleSortChange('task')"
                        @page-change="handlePageChange('task')">
                        <bk-table-column
                            v-for="col in taskListColumn"
                            :key="col.props"
                            :label="col.label"
                            :prop="col.prop"
                            :width="col.hasOwnProperty('width') ? col.width : 'auto'"
                            :sortable="col.sortable">
                            <template slot-scope="props">
                                <a
                                    v-if="col.prop === 'name'"
                                    class="table-link"
                                    target="_blank"
                                    :title="props.row.name"
                                    :href="`${site_url}taskflow/execute/${props.row.project.id}/?instance_id=${props.row.id}`">
                                    {{props.row.name}}
                                </a>
                                <template v-else-if="col.prop === 'projectName'">
                                    <span>{{ props.row.project.name }}</span>
                                </template>
                                <template v-else>{{ props.row[col.prop] }}</template>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </div>
            </template>
            <div class="no-data-matched" slot="empty"><NoData :message="i18n.empty" /></div>
        </div>
    </div>
</template>
<script>
    import { mapActions, mapState } from 'vuex'
    import tools from '@/utils/tools.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'

    const TEMPLATE_TABLE_COLUMN = [
        {
            label: gettext('ID'),
            prop: 'id',
            sortable: true,
            width: 90
        },
        {
            label: gettext('流程名称'),
            prop: 'name'
        },
        {
            label: gettext('项目'),
            prop: 'projectName'
        },
        {
            label: gettext('更新时间'),
            prop: 'edit_time'
        },
        {
            label: gettext('是否已删除'),
            prop: 'is_deleted',
            width: 100
        },
        {
            label: gettext('操作'),
            width: 100
        }
    ]

    const TASK_TABLE_COLUMN = [
        {
            label: gettext('ID'),
            prop: 'id',
            sortable: true,
            width: 90
        },
        {
            label: gettext('任务名称'),
            prop: 'name'
        },
        {
            label: gettext('项目'),
            prop: 'projectName'
        },
        {
            label: gettext('执行开始'),
            prop: 'start_time'
        },
        {
            label: gettext('执行结束'),
            prop: 'finish_time'
        },
        {
            label: gettext('创建人'),
            prop: 'creator_name',
            width: 100
        },
        {
            label: gettext('执行人'),
            prop: 'executor_name',
            width: 100
        },
        {
            label: gettext('创建方式'),
            prop: 'create_method',
            width: 100
        },
        {
            label: gettext('状态'),
            props: 'status',
            width: 100
        }
    ]

    export default {
        name: 'SearchResult',
        components: {
            NoData
        },
        props: {
            keyword: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                searchStr: this.keyword,
                searchLoading: true,
                tplListColumn: TEMPLATE_TABLE_COLUMN,
                taskListColumn: TASK_TABLE_COLUMN,
                tplDataLoading: false,
                taskDataLoading: false,
                matchedList: [],
                tplData: [],
                taskData: [],
                tplPagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [15],
                    'show-limit': false,
                    limit: 15
                },
                taskPagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [15],
                    'show-limit': false,
                    limit: 15
                },
                i18n: {
                    resultTitle: gettext('搜索结果'),
                    find: gettext('找到'),
                    result: gettext('条结果'),
                    empty: gettext('没有找到相关内容'),
                    yes: gettext('是'),
                    no: gettext('否'),
                    restore: gettext('恢复模板'),
                    edit: gettext('编辑')
                }
            }
        },
        computed: {
            ...mapState({
                site_url: state => state.site_url
            })
        },
        created () {
            this.onSearch = tools.debounce(this.searchHandler, 500)
            this.getSearchResult()
        },
        methods: {
            ...mapActions('admin/', [
                'search',
                'template',
                'task'
            ]),
            async getSearchResult () {
                try {
                    this.searchLoading = true
                    const res = await this.search({ keyword: this.searchStr })
                    if (res.result) {
                        this.matchedList = res.data.matched
                    } else {
                        errorHandler(res, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.searchLoading = false
                }
            },
            async getAdminTemplate () {
                try {
                    this.tplDataLoading = true
                    const params = {}
                    const res = await this.template(params)
                    this.tplData = res.objects
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.tplDataLoading = false
                }
            },
            async getAdminTask () {
                try {
                    this.taskDataLoading = true
                    const params = {}
                    const res = await this.task(params)
                    this.tplData = res.objects
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.taskDataLoading = false
                }
            },
            searchHandler () {
                this.getSearchResult()
            },
            onRestoreTemplate (tpl) {
                console.log(tpl)
            },
            handleSortChange () {},
            handlePageChange () {}
        }
    }
</script>
<style lang="scss" scoped>
    .search-result {
        margin: 0 60px;
    }
    .search-input {
         margin: 20px 0;
        width: 360px;
        color: #313238;
    }
    .result-title {
        font-size: 14px;
        color: #c4c6cc;
        & > h3 {
            margin: 0 12px 0 0;
            display: inline-block;
            color: #313238;
            font-size: 14px;
        }
    }
    .list-table {
        margin-top: 20px;
    }
    .no-data-matched {
        padding: 30px 0;
        .no-data-wrapper {
            padding: 50px 0;
        }
    }
</style>
