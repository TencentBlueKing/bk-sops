<template>
    <bk-dialog
        width="850"
        class="new-task-dialog"
        ext-cls="common-dialog"
        :theme="'primary'"
        :mask-close="false"
        :header-position="'left'"
        :title="i18n.title"
        :value="isNewTaskDialogShow"
        :auto-close="false"
        @confirm="onCreateTask"
        @cancel="onCancel">
        <div class="task-container">
            <div class="task-wrapper">
                <div class="filtrate-wrapper">
                    <div class="task-search flow-types">
                        <bk-select
                            v-if="type === 'normal'"
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
                            :placeholder="i18n.placeholder"
                            :right-icon="'bk-icon icon-search'"
                            :clearable="true"
                            v-model="searchWord"
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
                                                'task-item-selected': selectedId === template.id,
                                                'permission-disable': !hasPermission(action, template.auth_actions, operations)
                                            }
                                        ]"
                                        @click="onSelectTask(template)">
                                        <div class="task-item-icon">{{template.name.substr(0,1).toUpperCase()}}</div>
                                        <div class="task-item-name-box">
                                            <div class="task-item-name">{{template.name}}</div>
                                        </div>
                                        <div class="apply-permission-mask">
                                            <bk-button theme="primary" size="small">{{i18n.applyPermission}}</bk-button>
                                        </div>
                                    </li>
                                </ul>
                            </li>
                        </template>
                    </ul>
                    <NoData v-else class="empty-task">{{i18n.noSearchResult}}</NoData>
                </div>
            </div>
            <div class="task-footer" v-if="selectError">
                <span class="error-info">{{i18n.errorInfo}}</span>
            </div>
        </div>
    </bk-dialog>
</template>

<script>
    import '@/utils/i18n.js'
    import toolsUtils from '@/utils/tools.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TaskCreateDialog',
        components: {
            NoData
        },
        mixins: [permission],
        props: ['isNewTaskDialogShow', 'businessInfoLoading', 'common', 'project_id', 'taskCategory', 'type', 'dialogTitle'],
        data () {
            return {
                i18n: {
                    title: gettext('新建任务'),
                    placeholder: gettext('请输入关键字'),
                    noSearchResult: gettext('搜索结果为空'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消'),
                    errorInfo: gettext('请选择流程模版'),
                    allType: gettext('全部分类'),
                    applyPermission: gettext('申请权限')
                },
                selectedId: '',
                taskListPending: true,
                searchMode: false,
                selectError: false,
                commonTplList: [],
                businessTplList: [],
                templateList: [],
                templateType: [
                    {
                        id: 'businessProcess',
                        name: gettext('业务流程')
                    },
                    {
                        id: 'publicProcess',
                        name: gettext('公共流程')
                    }
                ],
                selectedTplType: 'businessProcess',
                selectedTplCategory: 'all',
                searchWord: '',
                nowTypeList: [],
                tplOperations: [],
                tplResource: {},
                commonTplOperations: [],
                commonTplResource: {}
            }
        },
        computed: {
            templateCategories () {
                const list = toolsUtils.deepClone(this.taskCategory)
                list.unshift({ value: 'all', name: gettext('全部分类') })
                return list.map(m => ({ value: m.value, name: m.name }))
            },
            categoryListPending () {
                return this.taskCategory.length !== 0 && this.taskListPending === false
            },
            isNoData () {
                return this.templateList.length === 0
            },
            title () {
                return this.dialogTitle || this.i18n.title
            },
            operations () {
                return this.selectedTplType === 'businessProcess' ? this.tplOperations : this.commonTplOperations
            },
            resource () {
                return this.selectedTplType === 'businessProcess' ? this.tplResource : this.commonTplResource
            },
            action () {
                return this.type === 'normal' ? ['create_task'] : ['create_periodic_task']
            }
        },
        watch: {
            isNewTaskDialogShow (val) {
                if (val) {
                    this.getTaskData()
                }
            }
        },
        created () {
            this.getTaskData()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions([
                'getCategorys'
            ]),
            async getTaskData () {
                this.taskListPending = true
                try {
                    if (this.type === 'normal') {
                        Promise.all([
                            this.getBusinessData(),
                            this.getcommonData()
                        ]).then(values => {
                            const businessList = values[0].objects
                            const commonList = values[1].objects
                            this.tplOperations = values[0].meta.auth_operations
                            this.tplResource = values[0].meta.auth_resource
                            this.commonTplOperations = values[1].meta.auth_operations
                            this.commonTplResource = values[1].meta.auth_resource
                            this.businessTplList = this.getGroupedList(businessList)
                            this.commonTplList = this.getGroupedList(commonList)
                            this.templateList = this.businessTplList
                            this.taskListPending = false
                        }).catch(e => {
                            errorHandler(e, this)
                        })
                    } else {
                        const data = {
                            common: this.common
                        }
                        const respData = await this.loadTemplateList(data)
                        const list = respData.objects
                        this.tplOperations = respData.meta.auth_operations
                        this.tplResource = respData.meta.auth_resource
                        this.businessTplList = this.getGroupedList(list)
                        this.templateList = this.businessTplList
                        this.taskListPending = false
                    }
                    this.onFiltrationTemplate()
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getBusinessData () {
                try {
                    const respData = await this.loadTemplateList()
                    return respData
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getcommonData () {
                const data = {
                    common: 1
                }
                try {
                    const respData = await this.loadTemplateList(data)
                    return respData
                } catch (e) {
                    errorHandler(e, this)
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
            onCreateTask () {
                if (this.selectedId === '') {
                    this.selectError = true
                    return
                }
                let url = `/template/newtask/${this.project_id}/selectnode/?template_id=${this.selectedId}`
                if (this.selectedTplType === 'publicProcess') {
                    url += '&common=1'
                }
                if (this.createEntrance === false) {
                    url += '&entrance=periodicTask'
                } else if (this.createEntrance === true) {
                    url += '&entrance=taskflow'
                }
                this.$router.push(url)
            },
            onCancel () {
                this.selectedId = ''
                this.selectError = false
                this.$emit('onCreateTaskCancel')
            },
            onSelectTask (template) {
                if (this.hasPermission(this.action, template.auth_actions, this.operations)) {
                    this.selectError = false
                    this.selectedId = template.id
                } else {
                    this.applyForPermission(this.action, template, this.operations, this.resource)
                }
            },
            searchInputhandler () {
                const list = toolsUtils.deepClone(this.nowTypeList)
                this.templateList = list.filter(group => {
                    group.children = group.children.filter(template => template.name.includes(this.searchWord))
                    return group.children.length
                })
            },
            onChooseTplType (value) {
                this.selectedTplType = value
                this.onFiltrationTemplate()
            },
            onChooseTplCategory (value) {
                this.selectedTplCategory = value
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
                width: 80px;
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
