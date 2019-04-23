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
    <bk-dialog
        :quick-close="false"
        :has-header="true"
        :ext-cls="'common-dialog'"
        :title="i18n.title"
        width="850"
        padding="0"
        :is-show.sync="isExportDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div slot="content" class="export-container">
            <div class="template-wrapper">
                <div class="search-wrapper">
                    <div class="business-selector">
                        <bk-selector
                            :list="taskCategories"
                            :display-key="'name'"
                            :setting-name="'value'"
                            :search-key="'name'"
                            :setting-key="'name'"
                            :selected.sync="filterCondition.type">
                        </bk-selector>
                    </div>
                    <div class="template-search">
                        <input class="search-input" :placeholder="i18n.placeholder" v-model="filterCondition.keywords" />
                        <i class="common-icon-search"></i>
                    </div>
                </div>
                <div class="template-list" v-bkloading="{ isLoading: exportPending, opacity: 1 }">
                    <ul v-if="!searchMode" class="grouped-list">
                        <template v-for="item in templates">
                            <li
                                v-if="item.children.length"
                                :key="item.id"
                                class="template-group">
                                <h5 class="group-name">
                                    {{item.name}}
                                    (<span class="list-count">{{item.children.length}}</span>)
                                </h5>
                                <ul>
                                    <li
                                        v-for="group in item.children"
                                        :key="group.id"
                                        :title="group.name"
                                        :class="['template-item', { 'template-item-selected': group.ischecked }]"
                                        @click="onSelectTemplate(group)">
                                        <div class="template-item-icon">{{group.name.substr(0,1).toUpperCase()}}</div>
                                        <div class="template-item-name">{{group.name}}</div>
                                    </li>
                                </ul>
                            </li>
                        </template>
                    </ul>
                    <div v-else class="search-list">
                        <ul v-if="searchList.length">
                            <li
                                v-for="item in searchList"
                                :key="item.id"
                                :title="item.name"
                                :class="[{
                                    'template-item': !item.ischecked,
                                    'template-item-selected': item.ischecked
                                }]"
                                @click="onSelectTemplate(item)">
                                <div class="template-item-icon">{{item.name.substr(0,1).toUpperCase()}}</div>
                                <div class="template-item-name">
                                    <span>{{item.name}}</span>
                                </div>
                            </li>
                        </ul>
                        <NoData v-else class="empty-task">{{i18n.noSearchResult}}</NoData>
                    </div>
                </div>
            </div>
            <div class="selected-wrapper">
                <div class="selected-area-title">
                    {{i18n.selected}}
                    <span class="select-count">{{selectedTemplate.length}}</span>
                    {{i18n.num}}
                </div>
                <ul class="selected-list">
                    <li
                        class="selected-item"
                        v-for="item in selectedTemplate"
                        :key="item.id">
                        <div class="selected-item-icon">
                            <span class="selected-name" :title="item.name">{{item.name.substr(0,1).toUpperCase()}}</span>
                        </div>
                        <div class="selected-item-name">
                            <span class="item-name">{{item.name}}</span>
                        </div>
                        <i class="selected-delete bk-icon icon-close-circle-shape" @click="deleteTemplate(item)"></i>
                    </li>
                </ul>
            </div>
            <div class="template-checkbox" @click="onSelectAll">
                <span :class="['checkbox', { checked: ischecked,'checkbox-disabled': isCheckedDisabled }]"></span>
                <span class="checkbox-name">{{ i18n.selectAll }}</span>
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
        name: 'ExportTemplateDialog',
        components: {
            NoData
        },
        props: ['isExportDialogShow', 'businessInfoLoading', 'common'],
        data () {
            return {
                exportPending: false,
                searchMode: false,
                ischecked: false,
                isCheckedDisabled: false,
                selectedTemplate: [],
                templateList: [],
                templates: [],
                searchList: [],
                i18n: {
                    title: gettext('导出流程'),
                    choose: gettext('选择流程'),
                    noSearchResult: gettext('搜索结果为空'),
                    templateEmpty: gettext('请选择需要导出的流程'),
                    placeholder: gettext('请输入流程名称'),
                    selected: gettext('已选择'),
                    num: gettext('项'),
                    selectAll: gettext('全选'),
                    delete: gettext('删除'),
                    allCategories: gettext('全部分类')
                },
                templateEmpty: false,
                selectedTaskCategory: '',
                category: '',
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
                    const sourceList = JSON.parse(JSON.stringify(this.templateList))
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
            this.getTemplateData()
        },
        methods: {
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions([
                'getCategorys'
            ]),
            async getTemplateData () {
                this.exportPending = true
                this.isCheckedDisabled = true
                try {
                    const data = {
                        common: this.common
                    }
                    const respData = await this.loadTemplateList(data)
                    const list = respData.objects
                    this.templateList = this.getGroupedList(list)
                    this.templateList.forEach((item) => {
                        item.children.forEach((group) => {
                            this.$set(group, 'ischecked', false)
                        })
                    })
                    this.templates = this.templateList
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.exportPending = false
                    this.isCheckedDisabled = false
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
            onSelectTemplate (group, clearAll) {
                group.ischecked = !group.ischecked
                if (group.ischecked) {
                    this.selectedTemplate.push(group)
                } else {
                    this.deleteTemplate(group)
                }
            },
            deleteTemplate (template) {
                const deleteIndex = this.selectedTemplate.findIndex(item => item.id === template.id)
                if (deleteIndex > -1) {
                    const deleteGroup = this.selectedTemplate.splice(deleteIndex, 1)[0]
                    deleteGroup.ischecked = false
                    this.templateList.forEach((item) => {
                        if (item.children.findIndex(util => !util.ischecked)) {
                            this.ischecked = false
                        }
                    })
                }
            },
            onSelectAll () {
                if (this.isCheckedDisabled) {
                    return false
                }
                this.selectedTemplate = []
                this.ischecked = !this.ischecked
                this.templates.filter(item => {
                    item.children.filter(childItem => {
                        childItem.ischecked = this.ischecked
                    })
                    if (this.ischecked) {
                        this.selectedTemplate.push(...item.children)
                    } else {
                        this.selectedTemplate = []
                    }
                })
            },
            onConfirm () {
                const idList = []
                this.selectedTemplate.forEach(item => {
                    idList.push(item.id)
                })
                this.$emit('onExportConfirm', idList)
            },
            onCancel () {
                this.templateEmpty = false
                this.$emit('onExportCancel')
            }
        }
    }
</script>
<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/config.scss';
.export-container {
    position: relative;
    height: 340px;
    .search-wrapper {
        padding: 0 14px 0 20px;
    }
    .business-selector {
        position: absolute;
        top: 20px;
        width: 255px;
        height: 32px;
    }
    .template-search {
        position: relative;
        margin-left: 265px;
        margin-bottom: 20px;
        .search-input {
            padding: 0 40px 0 10px;
            width: 255px;
            height: 32px;
            line-height: 32px;
            font-size: 14px;
            background: $whiteDefault;
            border: 1px solid #c3cdd7;
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
        .bk-selector {
            width: 255px;
        }
    }
    .template-wrapper {
        float: left;
        padding: 20px 0;
        width: 557px;
        height: 100%;
        .template-list {
            padding: 0 14px 0 20px;
            height: 268px;
            overflow-y: auto;
            @include scrollbar;
        }
        .template-group {
            margin-bottom: 30px;
        }
        .search-list {
            padding-top: 40px;
        }
        .group-name {
            margin-bottom: 8px;
            font-size: 12px;
        }
    }
    .template-item {
        display: inline-block;
        margin: 0 0 7px 10px;
        width: 254px;
        background: #dcdee5;
        border-radius: 2px;
        cursor: pointer;
        &:nth-child(2n + 1) {
            margin-left: 0;
        }
        .template-item-icon {
            float: left;
            width: 56px;
            height: 56px;
            line-height: 56px;
            background: #c4c6cc;
            font-size: 28px;
            color: #ffffff;
            text-align: center;
        }
        .template-item-name {
            margin-left: 56px;
            padding: 0 12px;
            height: 56px;
            line-height: 56px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            color: #313238;
        }
        &:nth-child(2n) {
            margin-right: 0;
        }
    }
    .template-item-selected {
        .template-item-icon {
            background: #666a7c;
        }
        .template-item-name {
            background: #838799;
            color: #ffffff;
        }
    }
    .selected-wrapper {
        width: 292px;
        height: 100%;
        margin-left: 557px;
        border-left:1px solid #dde4eb;
        .selected-area-title {
            padding: 28px 20px 22px;
            line-height: 1;
            font-size: 14px;
            font-weight: 600;
            color: #313238;
            .select-count {
                color: #3a84ff;
            }
        }
    }
    .selected-list {
        padding-top: 8px;
        height: 276px;
        overflow-y: auto;
        @include scrollbar;
        .selected-item {
            position: relative;
            margin: 0 0 10px 14px;
            width: 254px;
            height: 56px;
            border-radius: 2px;
            &:hover .selected-delete {
                display: inline-block;
            }
        }
        .selected-item-icon {
            float: left;
            width: 56px;
            height: 56px;
            line-height: 56px;
            background: #666a7c;
            .selected-name {
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 28px;
                color: #ffffff;
            }
        }
        .selected-item-name {
            margin-left: 56px;
            padding: 0 12px;
            height: 56px;
            line-height: 56px;
            background: #838799;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            color: #ffffff;
        }
        .selected-delete {
            display: none;
            position: absolute;
            top: -7px;
            right: -7px;
            color: #cecece;
            background: #ffffff;
            border-radius: 50%;
            cursor: pointer;
        }
    }
    .template-checkbox {
        position: absolute;
        left: 20px;
        bottom: -42px;
        cursor: pointer;
        .checkbox {
            display: inline-block;
            position: relative;
            width: 14px;
            height: 14px;
            color: $whiteDefault;
            border: 1px solid $formBorderColor;
            border-radius: 2px;
            text-align: center;
            vertical-align: -2px;
            &:hover {
                border-color: $greyDark;
            }
            &.checked {
                background: $blueDefault;
                border-color: $blueDefault;
                &::after {
                    content: "";
                    position: absolute;
                    left: 2px;
                    top: 2px;
                    height: 4px;
                    width: 8px;
                    border-left: 1px solid;
                    border-bottom: 1px solid;
                    border-color: $whiteDefault;
                    transform: rotate(-45deg);
                }
            }
        }
        .checkbox-disabled {
            display: inline-block;
            position: relative;
            width: 14px;
            height: 14px;
            color: $greyDisable;
            cursor: not-allowed;
            border: 1px solid $formBorderColor;
            border-radius: 2px;
            text-align: center;
            vertical-align: -2px;
            &::after {
                background: #545454;
            }
        }
    }
}
</style>
