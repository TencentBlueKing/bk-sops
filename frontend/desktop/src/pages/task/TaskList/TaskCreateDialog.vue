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
        @confirm="onCreateTask"
        @cancel="onCancel">
        <div class="task-container">
            <div class="task-wrapper">
                <div class="filtrate-wrapper">
                    <div class="task-search flow-types">
                        <bk-select
                            v-if="createEntrance"
                            v-model="selectedTplType"
                            class="bk-select-inline"
                            :popover-width="260"
                            :disabled="!categoryListPending"
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
                            :popover-width="260"
                            class="bk-select-inline"
                            :disabled="!categoryListPending"
                            @selected="onChooseTplCategory">
                            <bk-option
                                v-for="(option, index) in templateCategories"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="task-search">
                        <input class="search-input" :placeholder="i18n.placeholder" v-model="searchWord" @input="onSearchInput" />
                        <i class="common-icon-search"></i>
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
                                        :class="['task-item', { 'task-item-selected': selectedId === template.id }]"
                                        @click="onSelectTask(template)">
                                        <div class="task-item-icon">{{template.name.substr(0,1).toUpperCase()}}</div>
                                        <div class="task-item-name-box">
                                            <div class="task-item-name">{{template.name}}</div>
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
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'TaskCreateDialog',
        components: {
            NoData
        },
        props: ['isNewTaskDialogShow', 'businessInfoLoading', 'common', 'cc_id', 'taskCategory', 'createEntrance', 'dialogTitle'],
        data () {
            return {
                i18n: {
                    title: gettext('新建任务'),
                    placeholder: gettext('请输入关键字'),
                    noSearchResult: gettext('搜索结果为空'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消'),
                    errorInfo: gettext('请选择流程模版'),
                    allType: gettext('全部分类')
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
                        id: 'BusinessProcess',
                        name: gettext('业务流程')
                    },
                    {
                        id: 'PublicProcess',
                        name: gettext('公共流程')
                    }
                ],
                selectedTplType: gettext('BusinessProcess'),
                selectedTplCategory: gettext('all'),
                searchWord: '',
                nowTypeList: []
            }
        },
        computed: {
            templateCategories () {
                const list = toolsUtils.deepClone(this.taskCategory)
                list.unshift({ value: 'all', name: gettext('全部分类') })
                return list.map(m => ({ id: m.value || m.id, name: m.name }))
            },
            categoryListPending () {
                return this.taskCategory.length !== 0 && this.taskListPending === false
            },
            isNoData () {
                return this.templateList.length === 0
            },
            title () {
                return this.dialogTitle || this.i18n.title
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
                    if (this.createEntrance === true) {
                        Promise.all([
                            this.getBusinessData(),
                            this.getcommonData()
                        ]).then(values => {
                            const businessList = values[0]
                            const commonList = values[1]
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
                        this.businessTplList = this.getGroupedList(list)
                        this.templateList = this.businessTplList
                        this.taskListPending = false
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async getBusinessData () {
                const data = {
                    common: this.common
                }
                try {
                    const respData = await this.loadTemplateList(data)
                    return respData.objects
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
                    return respData.objects
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            getGroupedList (list) {
                const groups = []
                const atomGrouped = []
                this.taskCategory.forEach(item => {
                    groups.push(item.value)
                    atomGrouped.push({
                        name: item.name,
                        children: []
                    })
                })
                list.forEach(item => {
                    const type = item.category
                    const index = groups.indexOf(type)
                    if (index > -1) {
                        atomGrouped[index].children.push({
                            id: item.id,
                            name: item.name
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
                let url = `/template/newtask/${this.cc_id}/selectnode/?template_id=${this.selectedId}`
                if (this.selectedTplType === this.templateType[1].name) {
                    url += '&common=1'
                }
                if (this.createEntrance === false) {
                    url += '&entrance=0'
                } else if (this.createEntrance === true) {
                    url += '&entrance=1'
                }
                this.$router.push(url)
            },
            onCancel () {
                this.selectedId = ''
                this.$emit('onCreateTaskCancel')
            },
            onSelectTask (template) {
                this.selectError = false
                this.selectedId = template.id
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
                const list = this.selectedTplType === this.templateType[0].name ? this.businessTplList : this.commonTplList
                const sourceList = toolsUtils.deepClone(list)
                let filteredList = []
                if (this.selectedTplCategory === this.i18n.allType) {
                    filteredList = sourceList
                } else {
                    filteredList = sourceList.filter(item => item.name === this.selectedTplCategory)
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

<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
@import '@/scss/config.scss';
.task-container {
    position: relative;
    height: 340px;
    .task-wrapper {
        float: left;
        padding: 20px;
        width: 850px;
        height: 100%;
        .task-list {
            width: 830px;
            height: 268px;
            overflow-y: auto;
            @include scrollbar;
        }
        .task-group {
            margin-bottom: 30px;
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
        }
    }
    .task-search {
        position: relative;
        margin-left: 15px;
        margin-bottom: 20px;
        flex: 1;
        .search-input {
            padding: 0 40px 0 10px;
            width: 260px;
            height: 32px;
            line-height: 32px;
            font-size: 14px;
            background: $whiteDefault;
            border: 1px solid $commonBorderColor;
            border-radius: 4px;
            outline: none;
            &:hover {
                border-color: #c0c4cc;
            }
            &:focus {
                border-color: $blueDefault;
                & + i {
                    color: $blueDefault;
                }
            }
        }
        .common-icon-search {
            position: absolute;
            right: 15px;
            top: 9px;
            color: $commonBorderColor;
        }
    }
    .flow-types {
        margin-left: 0px;
    }
    .bk-selector {
        width: 260px;
    }
    .task-item {
        display: inline-block;
        margin-left: 15px;
        margin-bottom: 5px;
        width: 260px;
        cursor: pointer;
        background: #dcdee5;
        border-radius: 4px;
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
            border-radius: 4px 0 0 4px;
        }
        .task-item-name {
            color: #313238;
            word-break: break-all;
            border-radius: 0 4px 4px 0;
            @include multiLineEllipsis(14px, 2);
            &:after {
                background: #dcdee5
            }
        }
        &:hover {
            color: $blueDefault;
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
        border-radius: 0 4px 4px 0;
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
