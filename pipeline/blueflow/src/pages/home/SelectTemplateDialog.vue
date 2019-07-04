/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <bk-dialog
        :quick-close="false"
        :has-header="true"
        :ext-cls="'common-dialog'"
        :title="i18n.addTasks"
        width="800"
        padding="0"
        :is-show.sync="isShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <template slot="content">
            <div v-if="templateList.length" class="dialog-centent">
                <div v-bkloading="{isLoading: submitting, opacity: 1}">
                    <div class="template-wrapper">
                        <ul v-if="!searchMode" class="grouped-list">
                            <li
                                v-for="group in templateGrouped"
                                v-if="group.list.length"
                                :key="group.code"
                                class="template-group">
                                <h4 class="group-name">
                                    {{group.name}} (
                                    <span class="list-count">{{group.list.length}}</span>
                                    )
                                </h4>
                                <ul>
                                    <li
                                        v-for="item in group.list"
                                        :key="item.id"
                                        @click="onSelectTemplate(item)"
                                        class="template-item">
                                        <span :class="['checkbox', {checked: getItemStatus(item.id)}]"></span>
                                        {{item.name}}
                                    </li>
                                </ul>
                            </li>
                        </ul>
                        <div v-else class="search-list">
                            <ul v-if="searchList.length">
                                <li
                                    v-for="item in searchList"
                                    :key="item.id"
                                    @click="onSelectTemplate(item)"
                                    class="template-item">
                                    <span :class="['checkbox', {checked: getItemStatus(item.id)}]"></span>
                                    {{item.name}}
                                </li>
                            </ul>
                            <NoData v-else class="empty-task">{{i18n.noSearchResult}}</NoData>
                        </div>
                    </div>
                </div>
                <div class="template-search">
                    <input class="search-input" :placeholder="i18n.placeholder" v-model="searchStr" @input="onSearchInput"/>
                    <i class="common-icon-search"></i>
                </div>
                <div class="select-tips">
                    {{i18n.selected}}
                    <span class="select-count">{{selectedTemplate.length}}</span>
                    {{i18n.num}}{{i18n.maxSelect}}
                    <span class="select-count">10</span>
                    {{i18n.num}}
                </div>
            </div>
            <div v-else class="empty-task">
                <NoData>
                    <div>
                        {{i18n.noTemplate}}
                        <router-link class="create-template" :to="`/template/new/${cc_id}`">{{i18n.createTemplate}}</router-link>
                    </div>
                </NoData>
            </div>
        </template>
    </bk-dialog>
</template>
<script>
import '@/utils/i18n.js'
import toolsUtils from '@/utils/tools.js'
import NoData from '@/components/common/base/NoData.vue'
import BaseCheckbox from '@/components/common/base/BaseCheckbox.vue'
export default {
    name: 'SelectTemplateDialog',
    components: {
        NoData
    },
    props: ['cc_id', 'submitting', 'isSelectTemplateDialogShow', 'templateList', 'quickTaskList', 'templateGrouped'],
    data () {
        const selectedTemplate = this.quickTaskList.slice(0)
        return {
            isShow: false,
            selectedTemplate,
            searchMode: false,
            searchStr: '',
            searchList: [],
            i18n: {
                placeholder: gettext('请输入流程名称'),
                addTasks: gettext('添加常用流程'),
                selected: gettext('已选'),
                num: gettext('项'),
                maxSelect: gettext('，最多可选'),
                noSearchResult: gettext('搜索结果为空'),
                noTemplate: gettext('该业务下暂无流程，'),
                createTemplate: gettext('立即创建')
            }
        }
    },
    watch: {
        isSelectTemplateDialogShow (val) {
            this.isShow = val
        },
        quickTaskList (val) {
            this.selectedTemplate = val.slice(0)
        }
    },
    created () {
        this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
    },
    methods: {
        getItemStatus (id) {
            return this.selectedTemplate.some(item => item.id === id)
        },
        searchInputhandler () {
            if (this.searchStr.length) {
                this.searchMode = true
                const reg = new RegExp(this.searchStr, 'g')
                this.searchList = this.templateList.filter(item => {
                    return reg.test(item.name)
                })
            } else {
                this.searchMode = false
                this.searchList = []
            }
        },
        onSelectTemplate (template) {
            let index
            const isSelected = this.selectedTemplate.some((item, i) => {
                if (item.id === template.id) {
                    index = i
                    return true
                }
            })
            if (isSelected) {
                this.selectedTemplate.splice(index, 1)
            } else {
                if (this.selectedTemplate.length === 10) {
                    this.$bkMessage({
                        message: gettext('最多只能添加10项'),
                        theme: 'warning'
                    })
                    return
                }
                this.selectedTemplate.push(template)
            }
        },
        onConfirm () {
            this.$emit('confirm', this.selectedTemplate)
        },
        onCancel () {
            this.selectedTemplate = this.quickTaskList.slice(0)
            this.$emit('cancel')
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/config.scss';
.template-search {
    position: absolute;
    top: 80px;
    right: 30px;
    .search-input {
        padding: 0 40px 0 10px;
        width: 300px;
        height: 36px;
        line-height: 36px;
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
        top: 11px;
        color: $commonBorderColor;
    }
}
.template-wrapper {
    padding: 16px 30px 0;
    height: 400px;
    overflow-y: auto;
    @include scrollbar;
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
        margin-right: 20px;
        margin-bottom: 5px;
        width: 230px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        &:nth-child(3n) {
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
.select-tips {
    position: absolute;
    bottom: 20px;
    left: 30px;
    .select-count {
        color: $blueDefault;
    }
}
.empty-task  {
    padding: 80px 0;
}
.create-template {
    color: #3c96ff;
}
</style>

