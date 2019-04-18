<template>
    <bk-dialog
        class="new-task-dialog"
        :quick-close="false"
        :has-header="true"
        :ext-cls="'common-dialog'"
        :title="i18n.title"
        width="850"
        padding="0"
        :is-show.sync="isNewTaskDialogShow"
        @confirm="onCreateTask"
        @cancel="onCancel">
        <div slot="content" class="task-container">
            <div class="task-wrapper">
                <div class="task-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="filterCondition.keywords" />
                    <i class="common-icon-search"></i>
                </div>
                <div class="task-search">
                    <bk-selector
                        :list="taskCategories"
                        :display-key="'name'"
                        :setting-name="'value'"
                        :search-key="'name'"
                        :setting-key="'name'"
                        :selected.sync="filterCondition.type">
                    </bk-selector>
                </div>
                <div class="task-list" v-bkloading="{ isLoading: exportPending, opacity: 1 }">
                    <ul v-if="!searchMode" class="grouped-list">
                        <template v-for="item in templates">
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
                                        <div class="task-item-name">{{template.name}}</div>
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
    import { mapState, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'TaskCreateDialog',
        components: {
            NoData
        },
        props: ['isNewTaskDialogShow', 'businessInfoLoading', 'common', 'cc_id'],
        data () {
            return {
                i18n: {
                    title: gettext('新建任务'),
                    placeholder: gettext('请输入关键字'),
                    noSearchResult: gettext('搜索结果为空'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消'),
                    errorInfo: gettext('请选择流程模版')
                },
                searchStr: '',
                selectedTaskCategory: '',
                selectedId: '',
                exportPending: false,
                searchMode: false,
                selectError: false,
                taskList: [],
                selectedList: [],
                templates: [],
                filterCondition: {
                    type: gettext('全部分类'),
                    keywords: ''
                }
            }
        },
        computed: {
            ...mapState({
                'businessBaseInfo': state => state.template.businessBaseInfo
            }),
            taskCategories () {
                if (this.businessBaseInfo.task_categories.length === 0) {
                    this.getCategorys()
                }
                const list = toolsUtils.deepClone(this.businessBaseInfo.task_categories)
                list.unshift({ value: 'all', name: gettext('全部分类') })
                return list
            }
        },
        watch: {
            filterCondition: {
                deep: true,
                handler (condition) {
                    // 过滤出一级分类信息
                    const sourceList = JSON.parse(JSON.stringify(this.taskList))
                    const template = sourceList.find(item => item.name === condition.type)
                    let filteredList = sourceList
                    if (template) {
                        filteredList = [template]
                    }
                    this.templates = filteredList.filter(item => {
                        item.children = item.children.filter(childItem => childItem.name.includes(condition.keywords))
                        return item.children.length
                    })
                }
            }
        },
        created () {
            this.getTaskData()
        },
        methods: {
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions([
                'getCategorys'
            ]),
            async getTaskData () {
                this.exportPending = true
                try {
                    const data = {
                        common: this.common
                    }
                    const respData = await this.loadTemplateList(data)
                    const list = respData.objects
                    this.taskList = this.getGroupedList(list)
                    this.taskList.forEach((item) => {
                        item.children.forEach((group) => {
                            this.$set(group, 'ischecked', false)
                        })
                    })
                    this.templates = this.taskList
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.exportPending = false
                }
            },
            getGroupedList (list) {
                const groups = []
                const atomGrouped = []
                this.businessBaseInfo.task_categories.forEach(item => {
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
                if (this.common) {
                    url += '&common=1'
                }
                this.$router.push(url)
            },
            onCancel () {
                this.$emit('onCreateTaskCancel')
            },
            onSelectTask (template) {
                this.selectError = false
                this.selectedId = template.id
                template.ischecked = !template.ischecked
            }
        }
    }
</script>

<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
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
            font-weight:400;
        }
    }
    .task-search {
        position: relative;
        margin-left: 10px;
        margin-bottom: 20px;
        float: right;
        .search-input {
            padding: 0 40px 0 10px;
            width: 320px;
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
    .bk-selector {
        width: 320px;
    }
    .task-item {
        display: inline-block;
        margin-left: 15px;
        width: 260px;
        cursor: pointer;
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
            margin-left: 56px;
            padding: 0 12px;
            height: 56px;
            line-height: 56px;
            color: #313238;
            background: #dcdee5;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        &:hover {
            color: $blueDefault;
        }
    }
    .task-item-selected {
        .task-item-icon {
            background: #666a7c;
            color: #ffffff;
        }
        .task-item-name {
            background: #838799;
            color: #ffffff;
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
