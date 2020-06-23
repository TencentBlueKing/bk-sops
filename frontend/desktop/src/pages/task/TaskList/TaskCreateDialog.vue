<template>
    <bk-dialog
        width="850"
        class="new-task-dialog"
        ext-cls="common-dialog"
        :theme="'primary'"
        :mask-close="false"
        :header-position="'left'"
        :title="$t('新建任务')"
        :value="isNewTaskDialogShow"
        :auto-close="false"
        @value-change="toggleShow">
        <div class="task-container">
            <div class="task-wrapper">
                <div class="filtrate-wrapper">
                    <div class="task-search flow-types">
                        <bk-select
                            v-model="selectedTplType"
                            class="bk-select-inline"
                            :popover-width="260"
                            :disabled="!categoryListPending"
                            :clearable="false"
                            @selected="onChooseTplType">
                            <bk-option
                                v-for="(option, index) in templateType"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="task-search">
                        <bk-select
                            v-model="selectedTplCategory"
                            class="bk-select-inline"
                            :popover-width="260"
                            :disabled="!categoryListPending"
                            :clearable="false"
                            @selected="onChooseTplCategory">
                            <bk-option
                                v-for="(option, index) in templateCategories"
                                :key="index"
                                :id="option.value"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="task-search">
                        <bk-input
                            class="search-input"
                            :placeholder="$t('请输入关键字')"
                            :right-icon="'bk-icon icon-search'"
                            :clearable="true"
                            v-model.trim="searchWord"
                            @input="onSearchInput">
                        </bk-input>
                    </div>
                </div>
                <div class="task-list" v-bkloading="{ isLoading: taskListPending, opacity: 1 }">
                    <ul v-if="!isNoData" class="grouped-list">
                        <template v-for="item in templateList">
                            <li
                                v-if="item.children.length"
                                :key="item.id"
                                class="task-group">
                                <h5 class="task-name">
                                    {{item.name}}
                                    (<span class="list-count">{{item.children.length}}</span>)
                                </h5>
                                <ul>
                                    <li
                                        v-for="template in item.children"
                                        :key="template.id"
                                        :title="template.name"
                                        :class="[
                                            'task-item',
                                            {
                                                'task-item-selected': selectedTpl.id === template.id,
                                                'permission-disable': selectedTplType === 'businessProcess' && !hasPermission(action, template.auth_actions)
                                            }
                                        ]"
                                        @click="onSelectTask(template)">
                                        <div class="task-item-icon">{{template.name.substr(0,1).toUpperCase()}}</div>
                                        <div class="task-item-name-box">
                                            <div class="task-item-name">{{template.name}}</div>
                                        </div>
                                        <div class="apply-permission-mask">
                                            <bk-button theme="primary" size="small">{{$t('申请权限')}}</bk-button>
                                        </div>
                                    </li>
                                </ul>
                            </li>
                        </template>
                    </ul>
                    <NoData v-else class="empty-task">{{$t('搜索结果为空')}}</NoData>
                </div>
            </div>
            <div class="task-footer" v-if="selectError">
                <span class="error-info">{{$t('请选择流程模版')}}</span>
            </div>
        </div>
        <div class="dialog-footer" slot="footer">
            <bk-button
                theme="primary"
                :class="{ 'btn-permission-disable': selectedTplType === 'publicProcess' && !hasCommonTplCreateTaskPerm }"
                :loading="permissionLoading"
                v-cursor="{
                    active: selectedTplType === 'publicProcess' && !hasCommonTplCreateTaskPerm
                }"
                @click="onCreateTask">
                {{ $t('确定') }}
            </bk-button>
            <bk-button @click="onCancel">{{ $t('取消') }}</bk-button>
        </div>
    </bk-dialog>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import toolsUtils from '@/utils/tools.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TaskCreateDialog',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            isNewTaskDialogShow: Boolean,
            businessInfoLoading: Boolean,
            common: String,
            project_id: [Number, String],
            taskCategory: Array,
            dialogTitle: String,
            entrance: String
        },
        data () {
            return {
                selectedTpl: {},
                taskListPending: true,
                searchMode: false,
                selectError: false,
                commonTplList: [],
                businessTplList: [],
                templateList: [],
                templateType: [
                    {
                        id: 'businessProcess',
                        name: i18n.t('项目流程')
                    },
                    {
                        id: 'publicProcess',
                        name: i18n.t('公共流程')
                    }
                ],
                selectedTplType: 'businessProcess',
                selectedTplCategory: 'all',
                searchWord: '',
                nowTypeList: [],
                permissionLoading: false,
                hasCommonTplCreateTaskPerm: true, // 有公共流程创建任务/周期任务权限
                tplOperations: [],
                tplResource: {},
                commonTplOperations: [],
                commonTplResource: {}
            }
        },
        computed: {
            ...mapState({
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project/', {
                'projectName': state => state.projectName,
                'projectAuthActions': state => state.authActions
            }),
            templateCategories () {
                const list = toolsUtils.deepClone(this.taskCategory)
                list.unshift({ value: 'all', name: i18n.t('全部分类') })
                return list.map(m => ({ value: m.value, name: m.name }))
            },
            categoryListPending () {
                return this.taskCategory.length !== 0 && this.taskListPending === false
            },
            isNoData () {
                return this.templateList.length === 0
            },
            title () {
                return this.dialogTitle || i18n.t('新建任务')
            },
            resource () {
                return this.selectedTplType === 'businessProcess' ? this.tplResource : this.commonTplResource
            },
            action () {
                if (this.entrance === 'taskflow') {
                    return this.selectedTplType === 'businessProcess' ? ['flow_create_task'] : ['common_flow_create_task']
                } else {
                    return this.selectedTplType === 'businessProcess' ? ['flow_create_periodic_task'] : ['common_flow_create_periodic_task']
                }
            }
        },
        created () {
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            async getBusinessData () {
                this.taskListPending = true
                try {
                    const respData = await this.loadTemplateList({ project__id: this.project_id })
                    const businessList = respData.objects
                    this.tplOperations = respData.meta.auth_operations
                    this.tplResource = respData.meta.auth_resource
                    this.businessTplList = this.getGroupedList(businessList)
                    this.templateList = this.businessTplList
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.taskListPending = false
                }
            },
            async getcommonData () {
                this.taskListPending = true
                const data = {
                    common: 1
                }
                try {
                    const respData = await this.loadTemplateList(data)
                    const commonList = respData.objects
                    this.commonTplOperations = respData.meta.auth_operations
                    this.commonTplResource = respData.meta.auth_resource
                    this.commonTplList = this.getGroupedList(commonList)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.taskListPending = false
                }
            },
            getGroupedList (list) {
                const groups = []
                const atomGrouped = []
                this.taskCategory.forEach(item => {
                    groups.push(item.name)
                    atomGrouped.push({
                        id: item.value,
                        name: item.name,
                        children: []
                    })
                })
                list.forEach(item => {
                    const type = item.category_name
                    const index = groups.indexOf(type)
                    if (index > -1) {
                        atomGrouped[index].children.push({
                            id: item.id,
                            name: item.name,
                            auth_actions: item.auth_actions
                        })
                    }
                })
                const listGroup = atomGrouped.filter(item => item.children.length)
                return listGroup
            },
            async toggleShow (val) {
                if (val) {
                    await this.getBusinessData()
                    this.onFiltrationTemplate()
                }
            },
            onCreateTask () {
                if (typeof this.selectedTpl.id !== 'number') {
                    this.selectError = true
                    return
                }
                if (this.permissionLoading) {
                    return
                }

                if (!this.hasCommonTplCreateTaskPerm) {
                    this.applyCommonTplCreateTaskPerm()
                    return
                }

                const url = {
                    name: 'taskStep',
                    params: {
                        project_id: this.project_id,
                        step: 'selectnode'
                    },
                    query: {
                        template_id: this.selectedTpl.id,
                        common: this.selectedTplType === 'publicProcess' ? '1' : undefined,
                        entrance: this.entrance || undefined
                    }
                }
                this.$router.push(url)
            },
            onCancel () {
                this.selectedTplType = 'businessProcess'
                this.selectedTplCategory = 'all'
                this.selectedTpl = {}
                this.selectError = false
                this.$emit('onCreateTaskCancel')
            },
            onSelectTask (template) {
                if (this.selectedTplType === 'businessProcess') {
                    if (this.hasPermission(this.action, template.auth_actions)) {
                        this.selectError = false
                        this.selectedTpl = template
                    } else {
                        const resourceData = {
                            flow: [{
                                id: template.id,
                                name: template.name
                            }]
                        }
                        this.applyForPermission(this.action, template.auth_actions, resourceData)
                    }
                } else {
                    this.selectError = false
                    this.selectedTpl = template
                    this.checkCommonTplPermission(template)
                }
            },
            async checkCommonTplPermission (template) {
                try {
                    this.permissionLoading = true
                    const bkSops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                    const data = {
                        action: this.entrance === 'taskflow' ? 'common_flow_create_task' : 'common_flow_create_periodic_task',
                        resources: [
                            {
                                system: bkSops.id,
                                type: 'project',
                                id: this.project_id,
                                attributes: {}
                            },
                            {
                                system: bkSops.id,
                                type: 'common_flow',
                                id: template.id,
                                attributes: {}
                            }
                        ]
                    }
                    const resp = await this.queryUserPermission(data)
                    this.hasCommonTplCreateTaskPerm = resp.data.is_allow
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.permissionLoading = false
                }
            },
            applyCommonTplCreateTaskPerm () {
                const reqPermission = this.entrance === 'taskflow' ? ['common_flow_create_task'] : ['common_flow_create_periodic_task']
                const curPermission = [...this.selectedTpl.auth_actions, ...this.projectAuthActions]
                const resourceData = {
                    common_flow: [{
                        id: this.selectedTpl.id,
                        name: this.selectedTpl.name
                    }],
                    project: [{
                        id: this.project_id,
                        name: this.projectName
                    }]
                }

                this.applyForPermission(reqPermission, curPermission, resourceData)
            },
            searchInputhandler () {
                const list = toolsUtils.deepClone(this.nowTypeList)
                this.templateList = list.filter(group => {
                    group.children = group.children.filter(template => template.name.includes(this.searchWord))
                    return group.children.length
                })
            },
            async onChooseTplType (value) {
                this.selectedTplType = value
                this.selectedTpl = {}
                if (value === 'businessProcess') {
                    await this.getBusinessData()
                } else {
                    await this.getcommonData()
                }
                this.onFiltrationTemplate()
            },
            onChooseTplCategory (value) {
                this.selectedTplCategory = value
                this.selectedTpl = {}
                this.onFiltrationTemplate()
            },
            onFiltrationTemplate () {
                const list = this.selectedTplType === 'businessProcess' ? this.businessTplList : this.commonTplList
                const sourceList = toolsUtils.deepClone(list)
                let filteredList = []
                if (this.selectedTplCategory === 'all') {
                    filteredList = sourceList
                } else {
                    filteredList = sourceList.filter(item => item.id === this.selectedTplCategory)
                }
                this.templateList = filteredList
                this.nowTypeList = filteredList
                if (this.searchWord !== '') {
                    this.searchInputhandler()
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
@import '@/scss/config.scss';
.task-container {
    position: relative;
    .task-wrapper {
        padding: 20px 20px 0;
        width: 850px;
        height: 100%;
        .task-list {
            width: 830px;
            height: 268px;
            overflow: hidden;
        }
        .task-group {
            margin-bottom: 30px;
        }
        .grouped-list {
            height: 100%;
            overflow-y: auto;
            @include scrollbar;
        }
        .search-list {
            padding-top: 40px;
        }
        .task-name {
            margin-bottom: 15px;
            font-size: 12px;
            font-weight: 400;
        }
        .filtrate-wrapper {
            display: flex;
            margin-bottom: 20px;
        }
    }
    .task-search {
        position: relative;
        margin-left: 15px;
        flex: 1;
        .search-input {
            width: 260px;
        }
    }
    .flow-types {
        margin-left: 0px;
    }
    .bk-selector {
        width: 260px;
    }
    .task-item {
        position: relative;
        display: inline-block;
        margin-left: 15px;
        margin-bottom: 5px;
        width: 260px;
        cursor: pointer;
        background: #dcdee5;
        border-radius: 2px;
        overflow: hidden;
        &:nth-child(3n + 1) {
            margin-left: 0;
        }
        .task-item-icon {
            float: left;
            width: 56px;
            height: 56px;
            line-height: 56px;
            background: #c4c6cc;
            text-align: center;
            color: #ffffff;
            font-size: 28px;
            overflow: hidden;
        }
        .task-item-name {
            color: #313238;
            word-break: break-all;
            @include multiLineEllipsis(14px, 2);
            &:after {
                background: #dcdee5
            }
        }
        .apply-permission-mask {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            text-align: center;
            .bk-button {
                margin-top: 12px;
            }
        }
        &.permission-disable {
            background: #f7f7f7;
            .task-item-icon {
                color: #dcdee5;
                background: #f7f7f7;
                border: 1px solid #dcdee5;
            }
            .task-item-name-box {
                border: 1px solid #dcdee5;
                border-left: none;
            }
            .task-item-name {
                color: #c4c6cc;
                &:after {
                    background: #f7f7f7;
                }
            }
            .apply-permission-mask {
                background: rgba(255, 255, 255, 0.6);
                text-align: center;
            }
            .bk-button {
                height: 32px;
                line-height: 30px;
            }
            &:hover .apply-permission-mask {
                display: block;
            }
        }
    }
    .task-item-name-box {
        display: table-cell;
        vertical-align: middle;
        margin-left: 56px;
        padding: 0 15px;
        height: 56px;
        width: 205px;
        font-size: 12px;
    }
    .task-item-selected {
        .task-item-icon {
            background: #666a7c;
            color: #ffffff;
        }
        .task-item-name, .task-item-name-box {
            background: #838799;
            color: #ffffff;
            &:after {
                background: #838799
            }
        }
    }
    .task-footer {
        position: absolute;
        right: 210px;
        bottom: -40px;
        .error-info {
            margin-right: 20px;
            font-size: 12px;
            color: #ea3636;
        }
    }
}
</style>
