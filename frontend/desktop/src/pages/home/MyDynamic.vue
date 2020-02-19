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
    <div class="my-dynamic">
        <h3 class="panel-title">
            <span class="panel-name">{{ i18n.title }}</span>
            <div class="create-method">
                <bk-select
                    class="bk-select-inline"
                    v-model="currentMethod"
                    :loading="isCreateMethosLoading"
                    :popover-width="260"
                    :clearable="false"
                    :placeholder="i18n.methodsPlaceholder"
                    @selected="onSelectMethod">
                    <bk-option
                        v-for="option in createMethods"
                        :key="option.value"
                        :id="option.value"
                        :name="option.name">
                    </bk-option>
                </bk-select>
            </div>
        </h3>
        <bk-table
            class="tab-data-table"
            v-bkloading="{ isLoading: isTableLoading, opacity: 1 }"
            :data="dynamicData"
            :pagination="pagination">
            <bk-table-column
                v-for="item in tableColumn"
                :key="item.prop"
                :label="item.label"
                :prop="item.prop"
                :width="item.hasOwnProperty('width') ? item.width : 'auto'"
                :sortable="item.sortable">
                <template slot-scope="props">
                    <template v-if="item.prop === 'status'">
                        <div class="ui-task-status">
                            <span :class="executeStatus[props.$index].cls"></span>
                            <span>{{ executeStatus[props.$index].text }}</span>
                        </div>
                    </template>
                    <template v-else-if="item.prop === 'name'">
                        <a
                            v-if="!hasPermission(['view'], props.row.auth_actions, taskOperations)"
                            v-cursor
                            class="text-permission-disable"
                            :title="props.row.name"
                            @click="onTaskPermissonCheck(['view'], props.row, $event)">
                            {{ props.row[item.prop] }}
                        </a>
                        <router-link
                            v-else
                            class="task-name"
                            :title="props.row.name"
                            :to="{
                                name: 'taskExecute',
                                params: { project_id: props.row.project.id },
                                query: { instance_id: props.row.id }
                            }">
                            {{ props.row[item.prop] }}
                        </router-link>
                    </template>
                    <template v-else-if="item.prop === 'project'">
                        {{ props.row[item.prop].name }}
                    </template>
                    <template v-else>
                        {{ props.row[item.prop] || '--' }}
                    </template>
                </template>
            </bk-table-column>
            <div class="empty-data" slot="empty"><no-data></no-data></div>
        </bk-table>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { mapState, mapActions } from 'vuex'
    import task from '@/mixins/task.js'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    const tableColumn = [
        {
            label: 'ID',
            prop: 'id',
            width: '100'
        },
        {
            label: gettext('任务名称'),
            prop: 'name',
            width: '300'
        },
        {
            label: gettext('项目'),
            prop: 'project'
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
            label: gettext('创建方式'),
            prop: 'create_method',
            width: '150'
        },
        {
            label: gettext('状态'),
            prop: 'status',
            width: '100'
        }
    ]
    export default {
        name: 'MyDynamic',
        components: {
            NoData
        },
        mixins: [permission, task],
        data () {
            return {
                i18n: {
                    title: gettext('我的动态'),
                    methodsPlaceholder: gettext('请选择')
                },
                createMethods: [{
                    name: gettext('所有创建方式'),
                    value: 'all'
                }],
                dynamicData: [],
                executeStatus: [],
                taskOperations: [],
                taskResource: {},
                pagination: {
                    current: 1,
                    count: 0,
                    'limit-list': [10],
                    'show-limit': false,
                    limit: 10
                },
                tableColumn: tableColumn,
                isTableLoading: false,
                isCreateMethosLoading: false,
                currentMethod: 'all'
            }
        },
        computed: {
            ...mapState({
                username: state => state.username
            })
        },
        async created () {
            await this.getCreateMethods()
            this.getTaskList()
        },
        methods: {
            ...mapActions('taskList/', [
                'loadTaskList'
            ]),
            ...mapActions('task/', [
                'loadCreateMethod'
            ]),
            async getTaskList () {
                this.isTableLoading = true
                try {
                    const data = {
                        limit: this.pagination.limit,
                        offset: 0,
                        pipeline_instance__is_started: true,
                        creator_or_executor: this.username,
                        create_method: this.currentMethod === 'all' ? undefined : this.currentMethod
                    }
                    const res = await this.loadTaskList(data)
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', res.objects)
                    
                    this.dynamicData = res.objects
                    this.dynamicData.forEach(m => {
                        const item = this.createMethods.find(method => method.value === m.create_method)
                        if (item) {
                            m.create_method = item.name
                        }
                    })
                    this.taskOperations = res.meta.auth_operations
                    this.taskResource = res.meta.auth_resource
                    this.isTableLoading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getCreateMethods () {
                try {
                    this.isCreateMethosLoading = true
                    const res = await this.loadCreateMethod()
                    this.createMethods = [...this.createMethods, ...res.data]
                    this.isCreateMethosLoading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onSelectMethod (val) {
                this.currentMethod = val
                this.getTaskList()
            },
            onTaskPermissonCheck (required, task, event) {
                this.applyForPermission(required, task, this.taskOperations, this.taskResource)
                event.preventDefault()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/task.scss';
.my-dynamic {
    margin-top: 20px;
    padding: 20px 24px 28px 24px;
    background: #ffffff;
    .panel-title {
        margin-top: 0;
        margin-bottom: 20px;
        .panel-name {
            color: #313238;
            font-size: 16px;
            font-weight: 600;
        }
        .create-method {
            float: right;
            font-size: 14px;
            color: #313238;
            font-weight: normal;
        }
    }
    .ui-task-status {
        @include ui-task-status;
    }
    .task-name {
        color: #3c96ff;
    }
}
</style>
