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
    <div class="project-container">
        <skeleton :loading="firstLoading" loader="commonList">
            <div class="list-wrapper">
                <div class="list-header mb20">
                    <bk-checkbox v-model="isClosedShow" @change="onClosedProjectToggle">{{$t('显示已停用项目')}}</bk-checkbox>
                    <search-select
                        ref="searchSelect"
                        id="projectList"
                        :placeholder="$t('ID/CC_ID/项目名称/创建人')"
                        v-model="searchSelectValue"
                        :search-list="searchList"
                        @change="handleSearchValueChange">
                    </search-select>
                </div>
                <div class="project-table-content" data-test-id="project_table_projectList">
                    <bk-table
                        class="project-table"
                        :data="projectList"
                        :pagination="pagination"
                        :size="setting.size"
                        v-bkloading="{ isLoading: !firstLoading && loading, opacity: 1, zIndex: 100 }"
                        @page-change="onPageChange"
                        @page-limit-change="handlePageLimitChange">
                        <bk-table-column
                            v-for="item in setting.selectedFields"
                            :key="item.id"
                            :label="item.label"
                            :prop="item.id"
                            :width="item.width"
                            show-overflow-tooltip
                            :render-header="renderTableHeader"
                            :min-width="item.min_width">
                            <template slot-scope="props">
                                {{ props.row[item.id] || '--' }}
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('操作')">
                            <template slot-scope="props">
                                <template
                                    v-for="(item, index) in OptBtnList">
                                    <a
                                        v-if="isShowOptBtn(props.row.is_disable, item.name)"
                                        v-cursor="{ active: !hasPermission([item.power], props.row.auth_actions) }"
                                        :key="index"
                                        :class="['operate-btn', {
                                            'text-permission-disable': !hasPermission([item.power], props.row.auth_actions)
                                        }]"
                                        :text="true"
                                        @click="onClickOptBtn(props.row, item.name)">
                                        {{
                                            item.name === 'view'
                                                ? (!hasPermission([item.power], props.row.auth_actions) ? item.text : item.enter )
                                                : item.text
                                        }}
                                    </a>
                                </template>
                            </template>
                        </bk-table-column>
                        <bk-table-column type="setting">
                            <bk-table-setting-content
                                :fields="setting.fieldList"
                                :selected="setting.selectedFields"
                                :size="setting.size"
                                @setting-change="handleSettingChange">
                            </bk-table-setting-content>
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
        <bk-dialog
            width="600"
            padding="30px 20px"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="projectDialogTitle"
            :value="isProjectDialogShow"
            data-test-id="project_table_projectDialog"
            @confirm="onProjectConfirm"
            @cancel="onEditProjectCancel">
            <div class="dialog-content">
                <div class="common-form-item">
                    <label class="required">{{ $t('名称') }}</label>
                    <div class="common-form-content">
                        <bk-input
                            name="projectName"
                            :disabled="dialogType === 'edit'"
                            v-model="projectDetail.name"
                            data-vv-validate-on=" "
                            v-validate="nameRule">
                        </bk-input>
                        <span v-show="veeErrors.has('projectName')" class="common-error-tip error-msg">{{ veeErrors.first('projectName') }}</span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label class="required">{{ $t('时区') }}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="projectDetail.timeZone"
                            :searchable="true"
                            :disabled="dialogType === 'edit'"
                            :placeholder="$t('请选择')"
                            @selected="onChangeTimeZone">
                            <bk-option
                                v-for="(option, index) in timeZoneList"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{ $t('描述') }}</label>
                    <div class="common-form-content">
                        <textarea
                            v-model="projectDetail.desc"
                            rows="5"
                            name="projectDesc"
                            data-vv-validate-on=" "
                            v-validate="descRule">
                        </textarea>
                        <span v-show="veeErrors.has('projectDesc')" class="common-error-tip error-msg">{{ veeErrors.first('projectDesc') }}</span>
                    </div>
                </div>
            </div>
        </bk-dialog>
        <bk-dialog
            width="400"
            padding="30px"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="projectStatusTitle"
            :value="isOperationDialogShow"
            @confirm="onChangeStatusConfirm"
            @cancel="isOperationDialogShow = false">
            <div class="operation-dialog-tips">
                {{$t('确认')}}{{operationType === 'start' ? $t('启用') : $t('停用')}}{{$t('项目')}}:{{projectDetail.name}}?
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import toolsUtils from '@/utils/tools.js'
    import Skeleton from '@/components/skeleton/index.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import { getTimeZoneList } from '@/constants/timeZones.js'
    import permission from '@/mixins/permission.js'
    import SearchSelect from '@/components/common/searchSelect/index.vue'
    const SEARCH_LIST = [
        {
            id: 'project_id',
            name: 'ID'
        },
        {
            id: 'bk_biz_id',
            name: 'CC_ID'
        },
        {
            id: 'project_name',
            name: i18n.t('项目名称'),
            isDefaultOption: true
        },
        {
            id: 'creator',
            name: i18n.t('创建人')
        }
    ]
    const OptBtnList = [
        {
            name: 'view',
            power: 'project_view',
            text: i18n.t('查看'),
            enter: i18n.t('进入')
        },
        {
            name: 'mandate',
            power: 'project_view',
            text: i18n.t('项目配置')
        },
        {
            name: 'edit',
            power: 'project_edit',
            text: i18n.t('编辑')
        },
        {
            name: 'start',
            power: 'project_edit',
            text: i18n.t('启用')
        },
        {
            name: 'stop',
            power: 'project_edit',
            text: i18n.t('停用')
        }
    ]
    const TABLE_FIELDS = [
        {
            id: 'id',
            label: 'ID',
            width: 80
        }, {
            id: 'bk_biz_id',
            label: 'CC_ID',
            width: 80
        }, {
            id: 'name',
            label: i18n.t('项目名称'),
            disabled: true,
            min_width: 200
        }, {
            id: 'desc',
            label: i18n.t('项目描述')
        }, {
            id: 'creator',
            label: i18n.t('创建人')
        }
    ]
    export default {
        name: 'ProjectHome',
        components: {
            Skeleton,
            NoData,
            SearchSelect
        },
        mixins: [permission],
        data () {
            const {
                page = 1,
                limit = 15,
                project_id = '',
                bk_biz_id = '',
                project_name = '',
                creator = ''
            } = this.$route.query
            const searchSelectValue = SEARCH_LIST.reduce((acc, cur) => {
                const values_text = this.$route.query[cur.id]
                if (values_text) {
                    const { id, name } = cur
                    acc.push({ id, name, values: [values_text] })
                }
                return acc
            }, [])
            return {
                firstLoading: true,
                OptBtnList,
                searchStr: '',
                projectList: [],
                loading: false,
                totalPage: 1,
                isClosedShow: false,
                isProjectDialogShow: false,
                isOperationDialogShow: false,
                dialogType: 'create',
                operationType: 'stop',
                projectDetailLoading: false,
                addPengding: false,
                updatePending: false,
                isMandateView: false,
                projectDetail: {
                    name: '',
                    timeZone: 'Asia/Shanghai',
                    desc: ''
                },
                timeZoneList: getTimeZoneList(),
                nameRule: {
                    required: true,
                    max: STRING_LENGTH.PROJECT_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                descRule: {
                    max: STRING_LENGTH.PROJECT_DESC_LENGTH
                },
                projectActions: [],
                pagination: {
                    current: Number(page),
                    count: 0,
                    limit: Number(limit),
                    'limit-list': [15, 30, 50, 100]
                },
                tableFields: TABLE_FIELDS,
                setting: {
                    fieldList: TABLE_FIELDS,
                    selectedFields: TABLE_FIELDS.slice(0),
                    size: 'small'
                },
                requestData: {
                    project_id,
                    bk_biz_id,
                    project_name,
                    creator
                },
                searchList: toolsUtils.deepClone(SEARCH_LIST),
                searchSelectValue
            }
        },
        computed: {
            ...mapState('project', {
                'project_id': state => state.project_id
            }),
            projectDialogTitle () {
                return this.dialogType === 'create' ? i18n.t('新建项目') : i18n.t('编辑项目')
            },
            projectStatusTitle () {
                return this.operationType === 'stop' ? i18n.t('停用') : i18n.t('启用')
            }
        },
        async created () {
            this.getFields()
            this.queryProjectCreatePerm()
            await this.getProjectList()
            this.firstLoading = false
        },
        methods: {
            ...mapMutations('project', [
                'setTimeZone'
            ]),
            ...mapMutations('atomForm', [
                'clearAtomForm'
            ]),
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('project', [
                'loadUserProjectList',
                'createProject',
                'loadProjectDetail',
                'updateProject',
                'changeDefaultProject'
            ]),
            async queryProjectCreatePerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'project_create'
                    })
                    if (res.data.is_allow) {
                        this.projectActions = ['project_create']
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async getProjectList () {
                this.loading = true

                try {
                    const { project_id, bk_biz_id, project_name, creator } = this.requestData
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        is_disable: this.isClosedShow,
                        id: project_id || undefined,
                        bk_biz_id: bk_biz_id || undefined,
                        name__icontains: project_name || undefined,
                        creator: creator || undefined
                    }

                    const projectList = await this.loadUserProjectList(data)
                    this.projectList = (projectList.results || []).map(item => {
                        if (!item.from_cmdb) {
                            item.bk_biz_id = '--'
                        }
                        return item
                    })
                    this.pagination.count = projectList.count
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.loading = false
                }
            },
            // 获取当前视图表格头显示字段
            getFields () {
                const settingFields = localStorage.getItem('ProjectList')
                let selectedFields
                if (settingFields) {
                    const { fieldList, size } = JSON.parse(settingFields)
                    this.setting.size = size || 'small'
                    selectedFields = fieldList || this.tableFields.map(item => item.id)
                    if (!fieldList || !size) {
                        localStorage.removeItem('ProjectList')
                    }
                } else {
                    selectedFields = this.tableFields.map(item => item.id)
                }
                this.setting.selectedFields = this.tableFields.slice(0).filter(m => selectedFields.includes(m.id))
            },
            async getProjectDetail (id) {
                try {
                    this.projectDetailLoading = false
                    this.projectDetail = await this.loadProjectDetail(id)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.projectDetailLoading = false
                }
            },
            renderTableHeader (h, { column, $index }) {
                return h('p', {
                    class: 'label-text',
                    directives: [{
                        name: 'bk-overflow-tips'
                    }]
                }, [
                    column.label
                ])
            },

            async addProject () {
                if (this.addPengding) {
                    return
                }
                this.addPengding = true
                try {
                    const { name, timeZone: time_zone, desc } = this.projectDetail
                    const data = {
                        name,
                        desc,
                        time_zone
                    }
                    await this.createProject(data)
                    this.isProjectDialogShow = false
                    this.getProjectList()
                    this.loadUserProjectList() // 新增项目后需要更新导航右上角的项目列表
                } catch (e) {
                    console.log(e)
                } finally {
                    this.addPengding = false
                }
            },
            async changeProject (disabled = false) {
                if (this.updatePending) {
                    return
                }
                this.updatePending = true
                try {
                    const { id, name, timeZone: time_zone, desc } = this.projectDetail
                    const data = {
                        id,
                        name,
                        desc,
                        time_zone,
                        is_disable: disabled
                    }
                    await this.updateProject(data)
                    this.isProjectDialogShow = false
                    this.isOperationDialogShow = false
                    this.clearProjectDetail()
                    this.getProjectList()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.updatePending = false
                }
            },
            // 表格功能选项
            handleSettingChange ({ fields, size }) {
                this.setting.size = size
                this.setting.selectedFields = fields
                const fieldIds = fields.map(m => m.id)
                localStorage.setItem('ProjectList', JSON.stringify({
                    fieldList: fieldIds,
                    size
                }))
            },
            onPageChange (page) {
                this.pagination.current = page
                this.updateUrl()
                this.getProjectList()
            },
            updateUrl () {
                const { current, limit } = this.pagination
                const { project_id, bk_biz_id, project_name, creator } = this.requestData
                const filterObj = {
                    current,
                    limit,
                    project_id,
                    bk_biz_id,
                    project_name,
                    creator
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
            handleSearchValueChange (data) {
                data = data.reduce((acc, cur) => {
                    const value = cur.values[0]
                    acc[cur.id] = cur.children ? value.id : value
                    return acc
                }, {})
                this.requestData = data
                this.pagination.current = 1
                this.updateUrl()
                this.getProjectList()
            },
            clearProjectDetail () {
                this.projectDetail = {
                    name: '',
                    timeZone: 'Asia/Shanghai',
                    desc: ''
                }
            },
            onClosedProjectToggle () {
                this.pagination.current = 1
                this.getProjectList()
            },
            onCreateProject () {
                if (!this.hasPermission(['project_create'], this.projectActions)) {
                    this.applyForPermission(['project_create'])
                } else {
                    this.dialogType = 'create'
                    this.isProjectDialogShow = true
                }
            },
            async onViewProject (project) {
                if (!this.hasPermission(['project_view'], project.auth_actions)) {
                    const resourceData = {
                        project: [{
                            id: project.id,
                            name: project.name
                        }]
                    }
                    this.applyForPermission(['project_view'], project.auth_actions, resourceData)
                    return
                }
                const id = project.id
                // 切换项目上下文
                await this.changeDefaultProject(id)
                const timeZone = this.projectList.find(m => Number(m.id) === Number(id)).time_zone || 'Asia/Shanghai'
                this.setTimeZone(timeZone)
                this.clearAtomForm() // notice: 清除标准插件配置项里的全局变量缓存

                this.$router.push({
                    name: 'processHome',
                    params: { project_id: id }
                })
            },
            onGoToConfig (project) {
                if (!this.hasPermission(['project_view'], project.auth_actions)) {
                    const resourceData = {
                        project: [{
                            id: project.id,
                            name: project.name
                        }]
                    }
                    this.applyForPermission(['project_view'], project.auth_actions, resourceData)
                    return
                }
                this.$router.push({ name: 'projectConfig', params: { id: project.id } })
            },
            onEditProject (project) {
                if (!this.hasPermission(['project_edit'], project.auth_actions)) {
                    const resourceData = {
                        project: [{
                            id: project.id,
                            name: project.name
                        }]
                    }
                    this.applyForPermission(['project_edit'], project.auth_actions, resourceData)
                    return
                }
                this.isProjectDialogShow = true
                this.dialogType = 'edit'
                this.projectDetail = {
                    id: project.id,
                    name: project.name,
                    timeZone: project.time_zone,
                    desc: project.desc
                }
            },
            onEditProjectCancel () {
                this.isProjectDialogShow = false
                this.clearProjectDetail()
            },
            onProjectConfirm () {
                this.$validator.validateAll().then(result => {
                    if (!result) {
                        return
                    }
                    if (this.dialogType === 'edit') {
                        this.changeProject()
                    } else {
                        this.addProject()
                    }
                })
            },
            onChangeTimeZone (value) {
                this.projectDetail.timeZone = value
            },
            onChangeProjectStatus (project, type) {
                if (!this.hasPermission(['project_edit'], project.auth_actions)) {
                    const resourceData = {
                        project: [{
                            id: project.id,
                            name: project.name
                        }]
                    }
                    this.applyForPermission(['project_edit'], project.auth_actions, resourceData)
                    return
                }
                this.operationType = type
                this.projectDetail = {
                    id: project.id,
                    name: project.name,
                    timeZone: project.time_zone,
                    desc: project.desc
                }
                this.isOperationDialogShow = true
            },
            onChangeStatusConfirm () {
                const disabled = this.operationType === 'stop'
                this.isOperationDialogShow = false
                this.changeProject(disabled)
            },
            /**
             * 是否显示操作按钮
             * @param {Boolean} isDisable
             * @param {String} name
             */
            isShowOptBtn (isDisable, name) {
                if (isDisable) {
                    return name === 'start'
                } else {
                    return ['view', 'stop', 'mandate'].includes(name)
                }
            },
            /**
             * 操作按钮点击
             * @param {Object} item
             * @param {String} name
             */
            onClickOptBtn (item, name) {
                switch (name) {
                    case 'view':
                        this.onViewProject(item)
                        break
                    // case 'edit':
                    //     this.onEditProject(item)
                    //     break
                    case 'mandate':
                        this.onGoToConfig(item)
                        break
                    default:
                        this.onChangeProjectStatus(item, name)
                }
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.updateUrl()
                this.getProjectList()
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';

    .project-container {
        padding: 20px 24px;
        height: 100%;
        overflow: auto;
        @include scrollbar;
        .dialog-content {
            word-break: break-all;
        }
    }
    .list-header {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        .bk-form-checkbox {
            position: relative;
            right: 495px;
        }
    }
    .project-table {
        background-color: #ffffff;
    }
    .operate-btn {
        margin-right: 5px;
        padding: 5px;
        height: auto;
        line-height: 1;
        background: transparent;
        border: none;
        font-size: 12px;
        color: #3a84ff;
        cursor: pointer;
        &.bk-button {
            min-width: unset;
        }
    }
    .dialog-content {
        padding: 20px 0;
        label {
            font-weight: normal;
        }
        .common-form-content {
            margin-right: 30px;
        }
        textarea {
            padding: 10px;
            width: 100%;
            border: 1px solid #dddddd;
            border-radius: 2px;
            resize: none;
            outline: none;
            &:hover {
                border-color: #c0c4cc;
            }
        }
    }
    .operation-dialog-tips {
        word-break: break-all;
        padding: 20px;
    }
</style>
