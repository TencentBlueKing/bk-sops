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
    <div class="template-container">
        <skeleton :loading="firstLoading" loader="templateList">
            <div class="list-wrapper">
                <div class="search-wrapper mb20">
                    <bk-button
                        class="my-create-btn"
                        data-test-id="process_form_myCreateProcess"
                        @click="handleMyCreateFilter">
                        {{$t('我创建的')}}
                    </bk-button>
                    <search-select
                        ref="searchSelect"
                        id="commonTplList"
                        :placeholder="$t('ID/流程名/创建人/更新人')"
                        v-model="searchSelectValue"
                        :search-list="searchList"
                        @change="handleSearchValueChange">
                    </search-select>
                </div>
                <div class="template-table-content" data-test-id="commonProcess_table_processList">
                    <bk-table
                        ref="templateTable"
                        class="template-table"
                        :data="templateList"
                        :pagination="pagination"
                        :size="setting.size"
                        :max-height="tableMaxHeight"
                        :default-sort="getDefaultSortConfig"
                        v-bkloading="{ isLoading: !firstLoading && listLoading, opacity: 1, zIndex: 100 }"
                        @sort-change="handleSortChange"
                        @page-change="onPageChange"
                        @page-limit-change="onPageLimitChange">
                        <bk-table-column
                            v-for="item in setting.selectedFields"
                            :key="item.id"
                            :label="item.label"
                            :prop="item.key || item.id"
                            :width="item.width"
                            :min-width="item.min_width"
                            :class-name="item.id.replace(/_/g, '-')"
                            show-overflow-tooltip
                            :render-header="renderTableHeader"
                            :sort-orders="['descending', 'ascending', null]"
                            :sortable="sortableCols.find(col => col.value === (item.key || item.id)) ? 'custom' : false">
                            <template slot-scope="{ row }">
                                <!--流程名称-->
                                <div v-if="item.id === 'name'" class="name-column">
                                    <a
                                        v-cursor="{ active: !hasPermission(['common_flow_view'], row.auth_actions) }"
                                        href="javascript:void(0);"
                                        class="common-icon-favorite icon-favorite"
                                        :class="{
                                            'is-active': row.is_collected,
                                            'disable': collectingId === row.id,
                                            'text-permission-disable': !hasPermission(['common_flow_view'], row.auth_actions)
                                        }"
                                        @click="onCollectTemplate(row)">
                                    </a>
                                    <a
                                        v-if="!hasPermission(['common_flow_view'], row.auth_actions)"
                                        v-cursor
                                        class="text-permission-disable"
                                        @click="onTemplatePermissionCheck(['common_flow_view'], row)">
                                        {{row.name}}
                                    </a>
                                    <a
                                        v-else
                                        class="template-name"
                                        :title="row.name"
                                        @click.prevent="getJumpUrl('view', row.id)">
                                        {{row.name}}
                                    </a>
                                </div>
                                <template v-else-if="['creator_name', 'editor_name'].includes(item.id)">
                                    <UserDisplayName :name="row[item.id]" />
                                </template>
                                <!-- 其他 -->
                                <template v-else>
                                    <span :title="row[item.id]">{{ row[item.id] || '--' }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" width="190" class="operation-cell" :fixed="templateList.length ? 'right' : false" :resizable="false">
                            <template slot-scope="props">
                                <div class="template-operation" :template-name="props.row.name">
                                    <template>
                                        <a
                                            v-cursor="{ active: !props.row.auth_actions.includes('common_flow_create_task') }"
                                            class="template-operate-btn"
                                            :class="{
                                                'text-permission-disable': !props.row.auth_actions.includes('common_flow_create_task')
                                            }"
                                            @click.prevent="handleCreateTaskClick(props.row)">
                                            {{$t('新建任务')}}
                                        </a>
                                        <router-link class="template-operate-btn" :to="getExecuteHistoryUrl(props.row.id)">{{ $t('执行历史') }}</router-link>
                                    </template>
                                </div>
                            </template>
                        </bk-table-column>
                        <bk-table-column type="setting">
                            <table-setting-content
                                :fields="setting.fieldList"
                                :selected="setting.selectedFields"
                                :size="setting.size"
                                :sortable-cols="sortableCols"
                                :order="ordering"
                                @setting-change="handleSettingChange">
                            </table-setting-content>
                        </bk-table-column>
                        <div class="empty-data" slot="empty">
                            <NoData
                                :type="searchSelectValue.length ? 'search-empty' : 'empty'"
                                :message="searchSelectValue.length ? $t('搜索结果为空') : ''"
                                @searchClear="searchSelectValue = []">
                            </NoData>
                        </div>
                    </bk-table>
                </div>
            </div>
        </skeleton>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import toolsUtils from '@/utils/tools.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    import TableRenderHeader from '@/components/common/TableRenderHeader.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import TableSettingContent from '@/components/common/TableSettingContent.vue'
    import UserDisplayName from '@/components/common/Individualization/UserDisplayName.vue'
    import permission from '@/mixins/permission.js'
    // moment用于时区使用
    import moment from 'moment-timezone'
    import CancelRequest from '@/api/cancelRequest.js'

    const SEARCH_LIST = [
        {
            id: 'template_id',
            name: 'ID'
        },
        {
            id: 'flowName',
            name: i18n.t('流程名'),
            isDefaultOption: true
        },
        {
            id: 'creator',
            name: i18n.t('创建人'),
            isUser: true
        },
        {
            id: 'editor',
            name: i18n.t('更新人'),
            isUser: true
        }
    ]

    const TABLE_FIELDS = [
        {
            id: 'id',
            label: i18n.t('ID'),
            width: 80
        },
        {
            id: 'name',
            label: i18n.t('流程名称'),
            disabled: true,
            min_width: 400
        },
        {
            key: 'pipeline_template__create_time',
            id: 'create_time',
            label: i18n.t('创建时间'),
            width: 200
        },
        {
            key: 'pipeline_template__edit_time',
            id: 'edit_time',
            label: i18n.t('更新时间'),
            width: 200
        },
        {
            key: 'category',
            id: 'category_name',
            label: i18n.t('分类'),
            min_width: 180
        },
        {
            id: 'creator_name',
            label: i18n.t('创建人'),
            width: 160
        },
        {
            id: 'editor_name',
            label: i18n.t('更新人'),
            width: 160
        }
    ]
    export default {
        name: 'TemplateCommonList',
        components: {
            Skeleton,
            SearchSelect,
            NoData,
            UserDisplayName,
            TableSettingContent
        },
        mixins: [permission],
        project_id: [String, Number],
        data () {
            const {
                page = 1,
                limit = 15,
                create_time = '',
                edit_time = '',
                creator = '',
                editor = '',
                flowName = '',
                template_id = ''
            } = this.$route.query
            const searchList = [
                ...SEARCH_LIST,
                { id: 'create_time', name: i18n.t('创建时间'), type: 'dateRange' },
                { id: 'edit_time', name: i18n.t('更新时间'), type: 'dateRange' }
            ]
            const searchSelectValue = searchList.reduce((acc, cur) => {
                const values_text = this.$route.query[cur.id]
                if (values_text) {
                    let values = []
                    if (!cur.children) {
                        values = cur.type === 'dateRange' ? values_text.split(',') : [values_text]
                        acc.push({ ...cur, values })
                    } else if (cur.children.length) {
                        const ids = values_text.split(',')
                        values = cur.children.filter(item => ids.includes(String(item.id)))
                        acc.push({ ...cur, values })
                    }
                }
                return acc
            }, [])
            // 获取操作列表
            return {
                firstLoading: true,
                listLoading: false,
                projectInfoLoading: true, // 模板分类信息 loading
                templateList: [],
                sortableCols: [],
                isSelectProjectShow: false,
                templateCategoryList: [],
                editEndTime: undefined,
                requestData: {
                    creator,
                    editor,
                    create_time: create_time ? create_time.split(',') : ['', ''],
                    edit_time: edit_time ? edit_time.split(',') : ['', ''],
                    flowName,
                    template_id
                },
                totalPage: 1,
                pagination: {
                    current: Number(page),
                    count: 0,
                    limit: Number(limit),
                    'limit-list': [15, 30, 50, 100]
                },
                collectingId: '', // 正在被收藏/取消收藏的模板id
                hasCreateCommonTplPerm: false, // 创建公共流程权限
                permissionLoading: false,
                hasCreateTaskPerm: true,
                selectedProject: {},
                selectedTpl: {},
                ordering: this.$store.state.project.config.task_template_ordering, // 排序参数
                tableFields: TABLE_FIELDS,
                defaultSelected: ['id', 'name', 'label', 'edit_time', 'creator_name', 'editor_name'],
                setting: {
                    fieldList: TABLE_FIELDS,
                    selectedFields: TABLE_FIELDS.slice(0),
                    size: 'small'
                },
                isInit: true, // 避免default-sort在初始化时去触发table的sort-change事件
                categoryTips: i18n.t('模板分类即将下线，建议使用标签'),
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue,
                tableMaxHeight: window.innerHeight - 186
            }
        },
        computed: {
            ...mapState({
                'username': state => state.username,
                'site_url': state => state.site_url,
                'v1_import_flag': state => state.v1_import_flag,
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone,
                'authActions': state => state.authActions,
                'projectName': state => state.projectName,
                'project_id': state => state.project_id
            }),
            // 获取默认排序配置
            getDefaultSortConfig () {
                const { ordering } = this
                if (ordering) {
                    if (/^-/.test(this.ordering)) {
                        return { prop: ordering.replace(/^-/, ''), order: 'descending' }
                    }
                    return { prop: ordering, order: 'ascending' }
                }
                return {}
            }
        },
        watch: {
            page (val, oldVal) {
                if (val !== oldVal) {
                    this.pagination.current = Number(val) || 1
                    this.getTemplateList()
                }
            }
        },
        async created () {
            this.getFields()
            const res = await this.getUserProjectConfigOptions({ id: this.project_id, params: { configs: 'task_template_ordering' } })
            this.sortableCols = res.data.task_template_ordering
            await this.getTemplateList()
            this.firstLoading = false
        },
        methods: {
            ...mapActions([
                'queryUserPermission',
                'addToCollectList',
                'deleteCollect'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions('project/', [
                'getUserProjectConfigOptions',
                'setUserProjectConfig'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            async queryCreateCommonTplPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'common_flow_create'
                    })
                    this.hasCreateCommonTplPerm = res.data.is_allow
                } catch (e) {
                    console.log(e)
                }
            },
            async getTemplateList () {
                this.listLoading = true
                try {
                    const data = this.getQueryData()
                    const source = new CancelRequest()
                    data.cancelToken = source.token
                    const templateListData = await this.loadTemplateList(data)
                    this.templateList = templateListData.results
                    this.pagination.count = templateListData.count
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.listLoading = false
                    this.isInit = false
                }
            },
            getQueryData () {
                const { creator, create_time, edit_time, flowName, template_id, editor } = this.requestData
                const tplIds = template_id?.split('|').map(item => item.trim()).join(',') || undefined
                const data = {
                    limit: this.pagination.limit,
                    offset: (this.pagination.current - 1) * this.pagination.limit,
                    common: '1',
                    pipeline_template__name__icontains: flowName || undefined,
                    pipeline_template__creator: creator || undefined,
                    pipeline_template__editor: editor || undefined,
                    project__id: this.project_id,
                    new: true,
                    id__in: tplIds
                }
                const keys = ['edit_time', '-edit_time', 'create_time', '-create_time']
                if (keys.includes(this.ordering)) {
                    const symbol = /^-/.test(this.ordering) ? '-' : ''
                    const orderVal = this.ordering.replace(/^-/, '')
                    data['order_by'] = `${symbol}pipeline_template__${orderVal}`
                } else {
                    data['order_by'] = this.ordering
                }
                if (create_time && create_time[0] && create_time[1]) {
                    data['pipeline_template__create_time__gte'] = moment(create_time[0]).format('YYYY-MM-DD HH:mm:ss')
                    data['pipeline_template__create_time__lte'] = moment(create_time[1]).format('YYYY-MM-DD HH:mm:ss')
                }
                if (edit_time && edit_time[0] && edit_time[1]) {
                    data['pipeline_template__edit_time__gte'] = moment(edit_time[0]).format('YYYY-MM-DD HH:mm:ss')
                    data['pipeline_template__edit_time__lte'] = moment(edit_time[1]).format('YYYY-MM-DD HH:mm:ss')
                }
                return data
            },
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('templateCommonList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.defaultSelected
                    if (!fieldList || !size) {
                        localStorage.removeItem('templateCommonList')
                    }
                } else {
                    selectedFields = this.defaultSelected
                }
                this.setting.selectedFields = this.tableFields.slice(0).filter(m => selectedFields.includes(m.id))
            },
            checkCreatePermission () {
                if (!this.hasCreateCommonTplPerm) {
                    this.applyForPermission(['common_flow_create'])
                } else {
                    this.$router.push({
                        name: 'commonTemplatePanel',
                        params: { type: 'new' }
                    })
                }
            },
            // 我创建的
            handleMyCreateFilter () {
                const creatorInfo = this.searchSelectValue.find(item => item.id === 'creator')
                let info = {}
                if (creatorInfo) {
                    creatorInfo.values = [this.username]
                    info = creatorInfo
                } else {
                    const form = this.searchList.find(item => item.id === 'creator')
                    info = { ...form, values: [this.username] }
                    this.searchSelectValue.push(info)
                }
                // 添加搜索记录
                const searchDom = this.$refs.searchSelect
                searchDom && searchDom.addSearchRecord(info)
            },
            handleSearchValueChange (data) {
                data = data.reduce((acc, cur) => {
                    if (cur.type === 'dateRange') {
                        acc[cur.id] = cur.values
                    } else if (cur.multiable) {
                        acc[cur.id] = cur.values.map(item => item.id)
                    } else {
                        const value = cur.values[0]
                        acc[cur.id] = typeof value === 'string' ? value : value.id
                    }
                    return acc
                }, {})
                this.requestData = data
                this.pagination.current = 1
                this.updateUrl()
                this.getTemplateList()
            },
            handleSortChange ({ prop, order }) {
                if (this.isInit) return
                if (order === 'ascending') {
                    this.ordering = prop
                } else if (order === 'descending') {
                    this.ordering = '-' + prop
                } else {
                    this.ordering = ''
                }
                // 更新表格头（自定义排序后不会清空其他排序的状态）
                if (prop === 'pipeline_template__create_time') {
                    const tableDom = this.$refs.templateTable
                    const columns = tableDom ? tableDom.store.states.columns : []
                    columns.forEach(column => {
                        if (column.sortable && column.property !== prop) {
                            column.order = null
                        }
                    })
                }
                this.pagination.current = 1
                this.updateUrl()
                this.getTemplateList()
                if (this.ordering) {
                    this.setUserProjectConfig({ id: this.project_id, params: { task_template_ordering: this.ordering } })
                }
            },
            renderTableHeader (h, { column, $index }) {
                if (column.property === 'category') {
                    return h('span', {
                        'class': 'category-label'
                    }, [
                        h('p', {
                            'class': 'label-text',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [column.label]),
                        h('i', {
                            'class': 'common-icon-info table-header-tips',
                            directives: [{
                                name: 'bk-tooltips',
                                value: this.categoryTips
                            }]
                        })
                    ])
                } else if (['pipeline_template__create_time', 'pipeline_template__edit_time'].includes(column.property)) {
                    const id = this.setting.selectedFields[$index].id
                    const date = this.requestData[id]
                    return <TableRenderHeader
                        name={ column.label }
                        property={ column.property }
                        sortConfig={ this.getDefaultSortConfig }
                        dateValue={ date }
                        onSortChange={ data => this.handleSortChange(data) }
                        onDateChange={ data => this.handleDateTimeFilter(data, id) }>
                    </TableRenderHeader>
                } else {
                    return h('p', {
                        class: 'label-text',
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [
                        column.label
                    ])
                }
            },
            handleDateTimeFilter (date = [], id) {
                const index = this.searchSelectValue.findIndex(item => item.id === id)
                if (date.length) {
                    if (index > -1) {
                        this.searchSelectValue[index].values = date
                    } else {
                        const info = {
                            id,
                            type: 'dateRange',
                            name: id === 'create_time' ? i18n.t('创建时间') : i18n.t('更新时间'),
                            values: date
                        }
                        this.searchSelectValue.push(info)
                        // 添加搜索记录
                        const searchDom = this.$refs.searchSelect
                        searchDom && searchDom.addSearchRecord(info)
                    }
                } else if (index > -1) {
                    this.searchSelectValue.splice(index, 1)
                }
            },
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.getTemplateList()
            },
            onPageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getTemplateList()
            },
            // 表格功能选项
            handleSettingChange ({ fields, size, order }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('templateCommonList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
                if (order && order !== this.ordering) {
                    this.ordering = order
                    this.$refs.templateTable.clearSort()
                    this.$refs.templateTable.sort(/^-/.test(order) ? order.replace(/^-/, '') : order, /^-/.test(order) ? 'descending' : 'ascending')
                    this.setUserProjectConfig({ id: this.project_id, params: { task_template_ordering: order } })
                }
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { create_time, edit_time, creator, flowName, template_id, editor } = this.requestData
                const filterObj = {
                    limit,
                    creator,
                    editor,
                    page: current,
                    create_time: create_time && create_time.every(item => item) ? create_time.join(',') : '',
                    edit_time: edit_time && edit_time.every(item => item) ? edit_time.join(',') : '',
                    flowName,
                    template_id
                }
                const query = {}
                Object.keys(filterObj).forEach(key => {
                    const val = filterObj[key]
                    if (val || val === 0 || val === false) {
                        query[key] = val
                    }
                })
                this.$router.replace({ name: this.$route.name, query })
            },
            /**
             * 单个模板操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} template 模板数据对象
             */
            onTemplatePermissionCheck (required, template) {
                const curPermission = template.auth_actions.slice(0)
                const permissionData = {
                    common_flow: [{
                        id: template.id,
                        name: template.name
                    }]
                }
                this.applyForPermission(required, curPermission, permissionData)
            },
            /**
             * 获取模版操作的跳转链接
             * @param {string} name -类型
             * @param {Number} template_id -模版id(可选)
             */
            getJumpUrl (name, template_id) {
                const urlMap = {
                    'view': { name: 'projectCommonTemplatePanel', params: { type: 'view' } },
                    'edit': { name: 'projectCommonTemplatePanel', params: { type: 'edit' } },
                    'newTemplate': { name: 'projectCommonTemplatePanel', params: { type: 'new' } },
                    'newTask': { name: 'taskCreate', params: { project_id: this.project_id, step: 'selectnode' } },
                    'clone': { name: 'projectCommonTemplatePanel', params: { type: 'clone' } }
                }
                const url = urlMap[name]
                url.query = {
                    template_id,
                    common: '1'
                }
                this.$router.push(url)
            },
            getExecuteHistoryUrl (id) {
                return {
                    name: 'taskList',
                    params: { project_id: this.project_id },
                    query: { template_id: id, template_source: 'common' }
                }
            },
            // 添加/取消收藏模板
            async onCollectTemplate (template) {
                if (!this.hasPermission(['common_flow_view'], template.auth_actions)) {
                    this.onTemplatePermissionCheck(['common_flow_view'], template)
                    return
                }
                if (typeof this.collectingId === 'number') {
                    return
                }

                try {
                    this.collectingId = template.id
                    if (!template.is_collected) { // add
                        const res = await this.addToCollectList([{
                            extra_info: {
                                template_id: template.template_id,
                                name: template.name,
                                id: template.id
                            },
                            instance_id: template.id,
                            username: this.username,
                            category: 'common_flow'
                        }])
                        if (res.data.length) {
                            this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                        }
                        template.collection_id = res.data[0].id
                    } else { // cancel
                        await this.deleteCollect(template.collection_id)
                        this.$bkMessage({ message: i18n.t('取消收藏成功！'), theme: 'success' })
                        template.collection_id = 0
                    }
                    template.is_collected = template.is_collected ? 0 : 1
                } catch (e) {
                    console.log(e)
                } finally {
                    this.collectingId = ''
                }
            },

            // 点击创建任务
            handleCreateTaskClick (tpl) {
                if (!tpl.auth_actions.includes('common_flow_create_task')) {
                    const resourceData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }],
                        common_flow: [{
                            id: tpl.template_id,
                            name: tpl.name
                        }]
                    }
                    const authActions = [...this.authActions, ...tpl.auth_actions]
                    this.applyForPermission(['common_flow_create_task'], authActions, resourceData)
                    return
                }
                this.$router.push({
                    name: 'taskCreate',
                    query: { template_id: tpl.id, common: '1' },
                    params: { project_id: this.project_id, step: 'selectnode' }
                })
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.template-container {
    padding: 20px 24px;
    height: 100%;
    overflow: auto;
    @include scrollbar;
}
.search-wrapper {
    position: relative;
    display: flex;
    justify-content: flex-end;
    .my-create-btn {
        position: relative;
        right: 495px;
    }
}
a {
    cursor: pointer;
}
.dialog-content {
    padding: 30px;
    word-break: break-all;
}
.export-tpl-btn,
.import-tpl-btn {
    position: relative;
    display: flex;
    align-items: center;
    padding: 0 4px 0 20px;
    height: 32px;
    line-height: 32px;
    min-width: 88px;
    text-align: center;
    font-size: 14px;
    background: #ffffff;
    border: 1px solid #c4c6cc;
    border-radius: 3px;
    cursor: pointer;
    .bk-icon {
        font-size: 24px;
        transition: ease-in-out 0.4s;
    }
}
.bk-dropdown-menu{
    &:hover {
        .export-tpl-btn,
        .import-tpl-btn {
            border-color: #979ba5;
            .bk-icon {
                transform: rotate(180deg);
            }
        }
    }
    ::v-deep .bk-dropdown-content {
        z-index: 1;
    }
}
.batch-operation-list,
.import-option-list {
    & > li {
        padding: 0 10px;
        height: 32px;
        line-height: 32px;
        font-size: 12px;
        text-align: left;
        white-space: nowrap;
        background: #ffffff;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
            background: #f4f6fa;
        }
        &.disabled {
            color: #cccccc;
            cursor: not-allowed;
        }
    }
}
.selected-tpl-num {
    display: flex;
    align-items: center;
    margin-left: 10px;
    font-size: 12px;
    line-height: 1;
    ::v-deep .bk-link-text {
        margin-left: 6px;
        font-size: 12px;
        line-height: 1;
    }
}
.template-table-content {
    background: #ffffff;
    .bk-table-row.hover-row {
        .icon-favorite {
            display: block;
        }
    }
    .icon-favorite {
        position: absolute;
        top: 14px;
        left: -9px;
        font-size: 14px;
        color: #c4c6cc;
        display: none;
        &.is-active {
            display: block;
            color: #ff9c01;
        }
    }
    a.template-name {
        color: $blueDefault;
    }
    .template-operation > .text-permission-disable {
        padding: 5px;
    }
    .template-operate-btn {
        padding: 5px;
        color: #3a84ff;
    }
    .drop-icon-ellipsis {
        font-size: 18px;
        vertical-align: -3px;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
            background: #dcdee5;
            border-radius: 50%;
        }
    }
    .subflow-has-update {
        color: $redDefault;
    }
    ::v-deep .select-all-cell {
        display: flex;
        align-items: center;
        &.full-selected {
            .bk-form-checkbox {
                .bk-checkbox {
                    background: #ffffff;
                    &:after {
                        border-color: #3a84ff;
                    }
                }
            }
        }
        .icon-angle-down {
            margin-left: 2px;
            font-size: 18px;
            color: #979ba5;
        }
    }
    ::v-deep .category-label {
        display: flex;
        align-items: center;
        .table-header-tips {
            flex-shrink: 0;
            margin-left: 4px;
            font-size: 14px;
            color: #c4c6cc;
            cursor: pointer;
        }
    }
    ::v-deep .edit-time,
    ::v-deep .create-time {
        .bk-table-caret-wrapper {
            display: none;
        }
    }
}
</style>
