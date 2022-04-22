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
    <div class="template-container">
        <skeleton :loading="firstLoading" loader="templateList">
            <div class="list-wrapper">
                <advance-search-form
                    ref="advanceSearch"
                    id="commonTplList"
                    :open="isSearchFormOpen"
                    :search-form="searchForm"
                    :search-config="{ placeholder: $t('请输入流程名称') }"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                </advance-search-form>
                <div class="template-table-content" data-test-id="commonProcess_table_processList">
                    <bk-table
                        ref="templateTable"
                        class="template-table"
                        :data="templateList"
                        :pagination="pagination"
                        :size="setting.size"
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
                                <!-- 其他 -->
                                <template v-else>
                                    <span :title="row[item.id]">{{ row[item.id] || '--' }}</span>
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')" width="240" class="operation-cell">
                            <template slot-scope="props">
                                <div class="template-operation">
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
                        <div class="empty-data" slot="empty"><NoData :message="$t('无数据')" /></div>
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
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import TableSettingContent from '@/components/common/TableSettingContent.vue'
    import permission from '@/mixins/permission.js'
    // moment用于时区使用
    import moment from 'moment-timezone'

    const SEARCH_FORM = [
        {
            type: 'dateRange',
            key: 'queryTime',
            placeholder: i18n.t('选择日期时间范围'),
            label: i18n.t('更新时间'),
            value: []
        },
        {
            type: 'input',
            key: 'creator',
            label: i18n.t('创建人'),
            placeholder: i18n.t('请输入创建人'),
            value: ''
        },
        {
            type: 'select',
            label: i18n.t('分类'),
            key: 'category',
            loading: true,
            placeholder: i18n.t('请选择分类'),
            tips: i18n.t('模板分类即将下线，建议使用标签'),
            list: [],
            value: ''
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
            AdvanceSearchForm,
            NoData,
            TableSettingContent
        },
        mixins: [permission],
        project_id: [String, Number],
        data () {
            const {
                page = 1,
                limit = 15,
                category = '',
                queryTime = '',
                creator = '',
                keyword = ''
            } = this.$route.query
            const searchForm = SEARCH_FORM.map(item => {
                if (this.$route.query[item.key]) {
                    if (Array.isArray(item.value)) {
                        item.value = this.$route.query[item.key].split(',')
                    } else {
                        item.value = this.$route.query[item.key]
                    }
                }
                return item
            })
            const isSearchFormOpen = SEARCH_FORM.some(item => this.$route.query[item.key])
            // 获取操作列表
            return {
                firstLoading: true,
                listLoading: false,
                projectInfoLoading: true, // 模板分类信息 loading
                searchForm,
                isSearchFormOpen,
                templateList: [],
                sortableCols: [],
                isSelectProjectShow: false,
                templateCategoryList: [],
                category: undefined,
                editEndTime: undefined,
                requestData: {
                    category,
                    creator,
                    queryTime: queryTime ? queryTime.split(',') : ['', ''],
                    flowName: keyword
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
                categoryTips: i18n.t('模板分类即将下线，建议使用标签')
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
            this.getProjectBaseInfo()
            this.onSearchInput = toolsUtils.debounce(this.searchInputHandler, 500)
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
                const { creator, category, queryTime, flowName } = this.requestData
                const data = {
                    limit: this.pagination.limit,
                    offset: (this.pagination.current - 1) * this.pagination.limit,
                    common: '1',
                    pipeline_template__name__icontains: flowName || undefined,
                    pipeline_template__creator__contains: creator || undefined,
                    category: category || undefined,
                    project__id: this.project_id,
                    new: true
                }
                const keys = ['edit_time', '-edit_time', 'create_time', '-create_time']
                if (keys.includes(this.ordering)) {
                    const symbol = /^-/.test(this.ordering) ? '-' : ''
                    const orderVal = this.ordering.replace(/^-/, '')
                    data['order_by'] = `${symbol}pipeline_template__${orderVal}`
                } else {
                    data['order_by'] = this.ordering
                }
                if (queryTime[0] && queryTime[1]) {
                    data['pipeline_template__edit_time__gte'] = moment(queryTime[0]).format('YYYY-MM-DD')
                    data['pipeline_template__edit_time__lte'] = moment(queryTime[1]).add('1', 'd').format('YYYY-MM-DD')
                }
                return data
            },
            async getProjectBaseInfo () {
                this.projectInfoLoading = true
                this.categoryLoading = true
                try {
                    const res = await this.loadProjectBaseInfo()
                    this.setProjectBaseInfo(res.data)
                    this.templateCategoryList = res.data.task_categories
                    const form = this.searchForm.find(item => item.key === 'category')
                    form.list = this.templateCategoryList
                    form.loading = false
                } catch (e) {
                    console.log(e)
                } finally {
                    this.projectInfoLoading = false
                    this.categoryLoading = false
                }
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
            searchInputHandler (data) {
                this.requestData.flowName = data
                this.pagination.current = 1
                this.getTemplateList()
            },
            onSearchFormSubmit (data) {
                this.requestData = Object.assign({}, this.requestData, data)
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
                this.pagination.current = 1
                this.updateUrl()
                this.getTemplateList()
                if (this.ordering) {
                    this.setUserProjectConfig({ id: this.project_id, params: { task_template_ordering: this.ordering } })
                }
            },
            renderTableHeader (h, { column, $index }) {
                if (column.property !== 'category') {
                    return column.label
                }

                return h('span', {
                    'class': 'category-label'
                }, [
                    column.label,
                    h('i', {
                        'class': 'common-icon-info table-header-tips',
                        directives: [{
                            name: 'bk-tooltips',
                            value: this.categoryTips
                        }]
                    })
                ])
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
                const { category, queryTime, creator, flowName } = this.requestData
                const filterObj = {
                    limit,
                    category,
                    creator,
                    page: current,
                    queryTime: queryTime.every(item => item) ? queryTime.join(',') : '',
                    keyword: flowName
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
    /deep/.bk-dropdown-content {
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
    /deep/.bk-link-text {
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
        &:hover, &.is-active {
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
    .empty-data {
        padding: 120px 0;
    }
    .subflow-has-update {
        color: $redDefault;
    }
    /deep/.select-all-cell {
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
    /deep/.table-header-tips {
        margin-left: 4px;
        font-size: 14px;
        color: #c4c6cc;
        cursor: pointer;
    }
}
</style>
