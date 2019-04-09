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
                <div class="template-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                    <i class="common-icon-search"></i>
                </div>
                <div class="template-list" v-bkloading="{isLoading: exportPending, opacity: 1}">
                    <ul v-if="!searchMode" class="grouped-list">
                        <template v-for="item in templateList">
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
                                        class="template-item"
                                        v-for="group in item.children"
                                        :key="group.id"
                                        :title="group.name"
                                        @click="onSelectTemplate(group)">
                                        <span :class="['checkbox', {checked: group.ischecked}]"></span>
                                        {{group.name}}
                                    </li>
                                </ul>
                            </li>
                        </template>
                    </ul>
                    <div v-else class="search-list">
                        <ul v-if="searchList.length">
                            <li
                                class="template-item"
                                v-for="item in searchList"
                                :key="item.id"
                                :title="item.name"
                                @click="onSelectTemplate(item)">
                                <span :class="['checkbox', {checked: item.ischecked}]"></span>
                                {{item.name}}
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
                        <span class="selected-name" :title="item.name">{{item.name}}</span>
                        <span class="selected-delete">
                            <i class="bk-icon icon-close-circle-shape" @click="deleteTemplate(item)"></i>
                        </span>
                    </li>
                </ul>
            </div>
            <div class="template-checkbox" @click="onSelectAll">
                <span :class="['checkbox', {checked: ischecked,'checkbox-disabled':isCheckedDisabled}]"></span>
                <span class="checkbox-name">{{ i18n.selectAll }}</span>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
import '@/utils/i18n.js'
import toolsUtils from '@/utils/tools.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import BaseCheckbox from '@/components/common/base/BaseCheckbox.vue'
import NoData from '@/components/common/base/NoData.vue'
export default {
    name: 'ExportTemplateDialog',
    props: ['isExportDialogShow', 'businessInfoLoading', 'common'],
    components: {
        NoData
    },
    data () {
        return {
            exportPending: false,
            searchMode: false,
            ischecked: false,
            isCheckedDisabled: false,
            selectedTemplate: [],
            templateList: [],
            searchList: [],
            selectedList: [],
            i18n: {
                title: gettext('导出流程'),
                choose: gettext('选择流程'),
                noSearchResult: gettext('搜索结果为空'),
                templateEmpty: gettext('请选择需要导出的流程'),
                placeholder: gettext('请输入流程名称'),
                selected: gettext('已选择'),
                num: gettext('项'),
                selectAll: gettext('全选'),
                delete: gettext('删除')
            },
            templateEmpty: false,
            searchStr: ''
        }
    },
    computed: {
        ...mapState({
            'businessBaseInfo': state => state.template.businessBaseInfo
        })
    },
    created () {
        this.getTemplateData()
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    methods: {
        ...mapActions('templateList/', [
            'loadTemplateList'
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
                        this.selectedList.push(group)
                    })
                })
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
        searchInputhandler () {
            if (this.searchStr.length) {
                this.searchMode = true
                const reg = new RegExp(this.searchStr, 'g')
                this.searchList =  this.selectedList.filter(item => {
                    return reg.test(item.name)
                })
            } else {
                this.searchMode = false
                this.searchList = []
            }
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
            this.templateList.forEach((item) => {
                item.children.forEach((group) => {
                    group.ischecked = this.ischecked
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
    .common-form-content {
        margin-right: 30px;
    }
    .template-search {
        position: relative;
        margin-bottom: 20px;
        text-align: right;
        .search-input {
            padding: 0 40px 0 10px;
            width: 362px;
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
    .template-wrapper {
        float: left;
        padding: 20px;
        width: 590px;
        height: 100%;
        .template-list {
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
            margin: 0 0 14px;
            font-size: 16px;
            font-weight: bold;
            .list-count {
                color: $blueDefault;
            }
        }
        .template-item {
            display: inline-block;
            margin-bottom: 7px;
            width: 250px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            &:nth-child(2n) {
                margin-right: 0;
            }
            &:hover {
                color: $blueDefault;
                cursor: pointer;
            }
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
        }
    }
    .selected-wrapper {
        margin-left: 590px;
        width: 260px;
        height: 100%;
        margin-left: 590px;
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
        .selected-list {
            height: 276px;
            overflow-y: auto;
            @include scrollbar;
            .selected-item {
                position: relative;
                padding-left: 20px;
                height: 33px;
                line-height: 33px;
                &:hover {
                    background-color: #F6F6F6;
                }
            }
            .selected-name {
                display: inline-block;
                margin-bottom: 7px;
                width: 200px;
                text-overflow: ellipsis;
                white-space: nowrap;
                overflow: hidden;
            }
            .selected-delete {
                position: absolute;
                top: 1px;
                right: 20px;
            }
            .icon-close-circle-shape {
                display: none;
                margin-left: 10px;
                cursor: pointer;
            }
            .selected-item:hover .icon-close-circle-shape {
                display: inline-block;
                margin-left: 10px;
                bottom: 20px;
            }
        }
    }
    .template-checkbox {
        position: absolute;
        left: 20px;
        bottom: -42px;
        .checkbox {
            display: inline-block;
            position: relative;
            width: 14px;
            height: 14px;
            color: $whiteDefault;
            border: 1px solid $formBorderColor;
            border-radius: 2px;
            text-align: center;
            cursor: pointer;
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
