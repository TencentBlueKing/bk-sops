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
        width="850"
        :ext-cls="'common-dialog'"
        :title="i18n.title"
        :mask-close="false"
        :value="isExportDialogShow"
        :header-position="'left'"
        :auto-close="false"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="export-container" v-bkloading="{ isLoading: businessInfoLoading, opacity: 1 }">
            <div class="template-wrapper">
                <div class="search-wrapper">
                    <div class="business-selector">
                        <bk-select
                            v-model="filterCondition.classifyId"
                            class="bk-select-inline"
                            :clearable="false"
                            :disabled="exportPending"
                            @change="onSelectClassify">
                            <bk-option
                                v-for="(item, index) in taskCategories"
                                :key="index"
                                :id="item.value"
                                :name="item.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="template-search">
                        <bk-input
                            class="search-input"
                            v-model="filterCondition.keywords"
                            :clearable="true"
                            :placeholder="i18n.placeholder"
                            :right-icon="'icon-search'"
                            @input="onSearchInput">
                        </bk-input>
                    </div>
                </div>
                <div class="template-list" v-bkloading="{ isLoading: exportPending, opacity: 1 }">
                    <ul class="grouped-list">
                        <template v-for="group in templateInPanel">
                            <li
                                v-if="group.children.length"
                                :key="group.id"
                                class="template-group">
                                <h5 class="group-name">
                                    {{group.name}}
                                    (<span class="list-count">{{group.children.length}}</span>)
                                </h5>
                                <ul>
                                    <li
                                        v-for="template in group.children"
                                        :key="template.id"
                                        :title="template.name"
                                        :class="[
                                            'template-item',
                                            {
                                                'template-item-selected': getTplIndexInSelected(template) > -1,
                                                'permission-disable': !hasPermission(['export'], template.auth_actions, tplOperations)
                                            }
                                        ]"
                                        @click="onSelectTemplate(template)">
                                        <div class="template-item-icon">{{getTemplateIcon(template)}}</div>
                                        <div class="item-name-box">
                                            <div class="template-item-name">{{template.name}}</div>
                                        </div>
                                        <div class="apply-permission-mask">
                                            <bk-button theme="primary" size="small">{{i18n.applyPermission}}</bk-button>
                                        </div>
                                    </li>
                                </ul>
                            </li>
                        </template>
                        <NoData v-if="!templateInPanel.length" class="empty-template"></NoData>
                    </ul>
                </div>
            </div>
            <div class="selected-wrapper">
                <div class="selected-area-title">
                    {{i18n.selected}}
                    <span class="select-count">{{selectedTemplates.length}}</span>
                    {{i18n.num}}
                </div>
                <ul class="selected-list">
                    <li
                        class="selected-item"
                        v-for="template in selectedTemplates"
                        :key="template.id">
                        <div class="selected-item-icon">
                            <span class="selected-name" :title="template.name">{{getTemplateIcon(template)}}</span>
                        </div>
                        <div class="item-name-box">
                            <div class="selected-item-name">{{template.name}}</div>
                        </div>
                        <i class="selected-delete bk-icon icon-close-circle-shape" @click="deleteTemplate(template)"></i>
                    </li>
                </ul>
            </div>
            <bk-checkbox class="template-checkbox" @change="onSelectAllClick" :value="isTplInPanelAllSelected">{{ i18n.selectAll }}</bk-checkbox>
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
    import permission from '@/mixins/permission.js'

    export default {
        name: 'ExportTemplateDialog',
        components: {
            NoData
        },
        mixins: [permission],
        props: ['isExportDialogShow', 'businessInfoLoading', 'projectInfoLoading', 'common', 'pending'],
        data () {
            return {
                exportPending: false,
                isTplInPanelAllSelected: false,
                isCheckedDisabled: false,
                templateList: [],
                templateInPanel: [],
                searchList: [],
                selectedTemplates: [],
                selectError: false,
                tplOperations: [],
                tplResource: {},
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
                    allCategories: gettext('全部分类'),
                    errorInfo: gettext('请选择流程模版'),
                    applyPermission: gettext('申请权限')
                },
                templateEmpty: false,
                selectedTaskCategory: '',
                category: '',
                filterCondition: {
                    classifyId: 'all',
                    keywords: ''
                },
                dialogFooterData: [
                    {
                        type: 'primary',
                        loading: false,
                        btnText: gettext('确认'),
                        click: 'onConfirm'
                    }, {
                        btnText: gettext('取消'),
                        click: 'onCancel'
                    }
                ]
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo
            }),
            taskCategories () {
                const list = toolsUtils.deepClone(this.projectBaseInfo.task_categories || [])
                list.unshift({ value: 'all', name: gettext('全部分类') })
                return list
            }
        },
        watch: {
            pending () {
                this.dialogFooterData[0].loading = this.pending
            }
        },
        created () {
            this.getData()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions([
                'getCategorys'
            ]),
            async getData () {
                if (this.projectBaseInfo.task_categories && this.projectBaseInfo.task_categories.length === 0) {
                    await this.getCategorys()
                    this.getTemplateData()
                } else {
                    this.getTemplateData()
                }
            },
            async getTemplateData () {
                this.exportPending = true
                this.isCheckedDisabled = true
                try {
                    const data = {
                        common: this.common || undefined
                    }
                    const respData = await this.loadTemplateList(data)
                    const list = respData.objects
                    this.tplOperations = respData.meta.auth_operations
                    this.tplResource = respData.meta.auth_resource
                    this.templateList = this.getGroupedList(list)
                    this.templateInPanel = this.templateList.slice(0)
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
                this.taskCategories.forEach(item => {
                    groups.push(item.value)
                    atomGrouped.push({
                        name: item.name,
                        value: item.value,
                        children: []
                    })
                })
                list.forEach(item => {
                    const type = item.category
                    const index = groups.indexOf(type)
                    if (index > -1) {
                        atomGrouped[index].children.push(item)
                    }
                })
                const listGroup = atomGrouped.filter(item => item.children.length)
                return listGroup
            },
            getTemplateIcon (template) {
                return template.name.trim().substr(0, 1).toUpperCase()
            },
            getTplIndexInSelected (template) {
                return this.selectedTemplates.findIndex(item => item.id === template.id)
            },
            getTplIsAllSelected () {
                if (!this.templateInPanel.length) {
                    return false
                }
                return this.templateInPanel.every(group => {
                    return group.children.every(template => {
                        return this.selectedTemplates.findIndex(item => item.id === template.id) > -1
                    })
                })
            },
            onSelectClassify (value) {
                let groupedList = []
                this.filterCondition.classifyId = value

                if (value === 'all') {
                    groupedList = this.templateList.slice(0)
                } else {
                    groupedList = this.templateList.filter(group => group.value === value)
                }

                if (this.filterCondition.keywords !== '') {
                    this.searchInputhandler()
                } else {
                    this.templateInPanel = groupedList
                }

                this.isTplInPanelAllSelected = this.getTplIsAllSelected()
            },
            searchInputhandler () {
                let searchList = []

                if (this.filterCondition.classifyId !== 'all') {
                    searchList = this.templateList.filter(group => group.value === this.filterCondition.classifyId)
                } else {
                    searchList = this.templateList.slice(0)
                }
                this.templateInPanel = toolsUtils.deepClone(searchList).filter(group => {
                    group.children = group.children.filter(template => {
                        return template.name.includes(this.filterCondition.keywords)
                    })
                    return group.children.length
                })
            },
            onSelectTemplate (template) {
                if (this.hasPermission(['export'], template.auth_actions, this.tplOperations)) {
                    this.selectError = false
                    const tplIndex = this.getTplIndexInSelected(template)
                    if (tplIndex > -1) {
                        this.selectedTemplates.splice(tplIndex, 1)
                        this.isTplInPanelAllSelected = false
                    } else {
                        this.selectedTemplates.push(template)
                        this.isTplInPanelAllSelected = this.getTplIsAllSelected()
                    }
                } else {
                    this.applyForPermission(['export'], template, this.tplOperations, this.tplResource)
                }
            },
            deleteTemplate (template) {
                const tplIndex = this.getTplIndexInSelected(template)
                this.selectedTemplates.splice(tplIndex, 1)
                this.isTplInPanelAllSelected = false
            },
            onSelectAllClick () {
                if (this.isCheckedDisabled) {
                    return
                }

                this.templateInPanel.forEach(group => {
                    group.children.forEach(template => {
                        if (this.hasPermission(['export'], template.auth_actions, this.tplOperations)) {
                            const tplIndex = this.getTplIndexInSelected(template)
                            if (this.isTplInPanelAllSelected) {
                                if (tplIndex > -1) {
                                    this.selectedTemplates.splice(tplIndex, 1)
                                }
                            } else {
                                if (tplIndex === -1) {
                                    this.selectedTemplates.push(template)
                                }
                            }
                        }
                    })
                })
                this.isTplInPanelAllSelected = !this.isTplInPanelAllSelected
            },
            onConfirm () {
                const idList = []
                if (this.selectedTemplates.length === 0) {
                    this.selectError = true
                    return false
                } else {
                    this.selectedTemplates.forEach(item => {
                        idList.push(item.id)
                    })
                    this.$emit('onExportConfirm', idList)
                    this.resetData()
                }
            },
            onCancel () {
                this.templateEmpty = false
                this.selectError = false
                this.resetData()
                this.$emit('onExportCancel')
            },
            resetData () {
                this.selectedTemplates = []
                this.filterCondition = {
                    classifyId: 'all',
                    keywords: ''
                }
                this.isTplInPanelAllSelected = false
                this.templateInPanel = this.templateList.slice(0)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
@import '@/scss/config.scss';
.export-container {
    position: relative;
    height: 340px;
    .search-wrapper {
        padding: 0 18px 0 20px;
    }
    .project-selector {
        position: absolute;
        top: 20px;
        width: 255px;
        height: 32px;
    }
    .business-selector {
        width: 260px;
        display: inline-block;
        vertical-align: top;
    }
    .template-search {
        width: 250px;
        display: inline-block;
        vertical-align: top;
    }
    .template-wrapper {
        float: left;
        padding: 20px 4px 20px 0;
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
        position: relative;
        display: inline-block;
        margin: 0 0 7px 10px;
        width: 252px;
        background: #dcdee5;
        border-radius: 2px;
        overflow: hidden;
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
            font-size: 24px;
            color: #ffffff;
            text-align: center;
        }
        .template-item-name {
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
        &:nth-child(2n) {
            margin-right: 0;
        }
        &.permission-disable {
            background: #f7f7f7;
            .template-item-icon {
                color: #dcdee5;
                background: #f7f7f7;
                border: 1px solid #dcdee5;
            }
            .item-name-box {
                border: 1px solid #dcdee5;
                border-left: none;
            }
            .template-item-name {
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
    .item-name-box {
        display: table-cell;
        vertical-align: middle;
        margin-left: 56px;
        padding: 0 15px;
        height: 56px;
        width: 195px;
        font-size: 12px;
        border-radius: 0 2px 2px 0;
    }
    .template-item-selected {
        .template-item-icon {
            background: #666a7c;
        }
        .template-item-name, .item-name-box {
            background: #838799;
            color: #ffffff;
            &:after {
                background: #838799
            }
        }
    }
    .empty-template {
        padding-top: 104px;
    }
    .selected-wrapper {
        width: 292px;
        height: 100%;
        margin-left: 557px;
        padding-right: 4px;
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
            width: 252px;
            height: 56px;
            background: #838799;
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
            border-radius: 2px;
            .selected-name {
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 24px;
                color: #ffffff;
            }
        }
        .selected-item-name {
            color: #ffffff;
            word-break: break-all;
            @include multiLineEllipsis(14px, 2);
            &:after {
                background: #838799
            }
        }
        .selected-delete {
            display: none;
            position: absolute;
            top: -7px;
            right: -7px;
            padding: 2px;
            color: #838799;
            background: #ffffff;
            border-radius: 50%;
            cursor: pointer;
        }
    }
    .template-checkbox {
        position: absolute;
        left: 20px;
        bottom: -42px;
    }
    .task-footer {
        position: absolute;
        right: 290px;
        bottom: -40px;
        .error-info {
            margin-right: 20px;
            font-size: 12px;
            color: #ea3636;
        }
    }
}
</style>
