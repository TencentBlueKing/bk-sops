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
    <div class="quick-create-task-content">
        <h3 class="title">{{i18n.myTasks}}</h3>
        <div v-if="quickTaskList.length" class="clearfix">
            <ul class="task-list">
                <li
                    v-for="item in quickTaskList"
                    :key="item.id"
                    class="task-item">
                    <router-link
                        class="task-name"
                        :title="item.name"
                        :to="`/template/newtask/${cc_id}/selectnode/?template_id=${item.id}`">
                        {{item.name}}
                    </router-link>
                    <i
                        class="common-icon-dark-circle-close delete-task"
                        v-bk-tooltips.top="i18n.cancelCollect"
                        @click="onDeleteTemplate(item.id)">
                    </i>
                </li>
            </ul>
            <div class="add-new-task">
                <button class="btn-with-add-icon" @click="onSelectTemplate">
                    <i class="common-icon-add"></i>
                </button>
                <p>{{i18n.addTasks}}</p>
            </div>
        </div>
        <div class="task-empty" v-else>
            <NoData>
                <p>{{i18n.addTips1}}<button class="empty-to-add" @click="onSelectTemplate">{{i18n.addTips2 }}</button></p>
            </NoData>
        </div>
        <SelectTemplateDialog
            :cc_id="cc_id"
            :submitting="submitting"
            :is-select-template-dialog-show="isSelectTemplateDialogShow"
            :template-list="templateList"
            :quick-task-list="quickTaskList"
            :template-grouped="templateGrouped"
            :select-template-loading="selectTemplateLoading"
            @confirm="onConfirm"
            @cancel="onCancel">
        </SelectTemplateDialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    import SelectTemplateDialog from './SelectTemplateDialog.vue'
    export default {
        name: 'QuickCreateTask',
        components: {
            NoData,
            SelectTemplateDialog
        },
        props: ['quickTaskList', 'cc_id', 'templateClassify', 'totalTemplate'],
        data () {
            return {
                isSelectTemplateDialogShow: false,
                submitting: false,
                i18n: {
                    myTasks: gettext('快速新建任务'),
                    cancelCollect: gettext('取消常用流程'),
                    addTasks: gettext('添加常用流程'),
                    addTips1: gettext('业务下无常用流程，'),
                    addTips2: gettext('立即添加')
                },
                selectTemplateLoading: false,
                templateList: [],
                templateGrouped: []
            }
        },
        methods: {
            ...mapActions('template/', [
                'templateCollectSelect',
                'templateCollectDelete'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            async onDeleteTemplate (id) {
                const list = this.getDeletedList(id)
                try {
                    const resp = await this.templateCollectDelete(id)
                    if (resp.result) {
                        this.$emit('updateQuickTaskList', list)
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onSelectTemplate () {
                this.isSelectTemplateDialogShow = true
                if (this.templateList.length === 0) {
                    this.getTemplateData()
                }
            },
            async onConfirm (selectedTemplate) {
                if (this.submitting) return
                this.submitting = true
                try {
                    const list = selectedTemplate.map(item => item.id)
                    const resp = await this.templateCollectSelect(JSON.stringify(list))
                    if (resp.result) {
                        this.isSelectTemplateDialogShow = false
                        this.$emit('updateQuickTaskList', selectedTemplate)
                    } else {
                        errorHandler(resp, this)
                    }
                    this.submitting = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onCancel () {
                this.isSelectTemplateDialogShow = false
            },
            getDeletedList (id) {
                let index
                const list = this.quickTaskList.slice(0)
                list.some((item, i) => {
                    if (item.id === id) {
                        index = i
                        return true
                    }
                })
                list.splice(index, 1)
                return list
            },
            async getTemplateData () {
                if (this.totalTemplate === 0) {
                    this.$bkMessage({
                        'message': gettext('业务下无流程模板，为您跳转至新建流程'),
                        'theme': 'success'
                    })
                    this.$router.push(`/template/new/${this.cc_id}`)
                    return
                }
                this.selectTemplateLoading = true
                try {
                    const templateData = await this.loadTemplateList()
                    this.templateList = templateData.objects
                    // 如果没有数据跳转至新建页面
                    this.templateGrouped = this.getGroupData(this.templateList, this.templateClassify)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.selectTemplateLoading = false
                }
            },
            getGroupData (list, classify) {
                const groupData = []
                classify.forEach(item => {
                    groupData.push({
                        code: item.code,
                        name: item.name,
                        list: []
                    })
                })
                list.forEach(item => {
                    let index
                    classify.some((cls, i) => {
                        if (item.category === cls.code) {
                            index = i
                            return true
                        }
                    })
                    groupData[index].list.push(item)
                })
                return groupData
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.quick-create-task-content {
    margin: 20px 0;
    padding: 20px 30px 50px;
    border: 1px solid $commonBorderColor;
    border-left: 6px solid $blueDefault;
    border-radius: 2px;
    box-shadow: -1px 1px 8px rgba(180, 180, 180, .15), 1px -1px 8px rgba(180, 180, 180, .15);
    background: $whiteDefault;
    .task-empty {
        padding: 50px 0;
    }
    .empty-to-add {
        padding: 0;
        color: $blueDefault;
        background: $whiteDefault;
        border: none;
    }
    .title {
        margin: 0 0 10px;
        font-size: 16px;
    }
    .task-list {
        float: left;
        width: 940px;
        height: 100px;
        border-right: 1px dashed $commonBorderColor;
        .task-item {
            position: relative;
            display: inline-block;
            margin: 5px 5px 5px 0;
            font-size: 12px;
            font-weight: bold;
            background: #f0f0f0;
            cursor: pointer;
            &:nth-child(5n) {
                margin-right: 0;
            }
            &:hover {
                background: #dce9f9;
                .task-name {
                    color: #3c96ff;
                }
                .delete-task {
                    display: inline-block;
                }
            }
            .task-name {
                display: block;
                padding: 12px 14px;
                width: 180px;
                color: #888888;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .delete-task {
                display: none;
                position: absolute;
                top: -8px;
                right: -8px;
                font-size: 16px;
                color: $redDefault;
                z-index: 1;
            }
        }
    }
    .add-new-task {
        float: right;
        padding: 22px 0;
        width: 160px;
        text-align: center;
        .btn-with-add-icon {
            display: inline-block;
            padding: 0;
            width: 30px;
            height: 30px;
            line-height: 30px;
            font-size: 24px;
            color: $blueDefault;
            background: $whiteDefault;
            border: 1px dashed $blueDefault;
            &:hover {
                background: #d5e0f6;
            }
            & + p {
                margin: 10px 0 0;
                font-size: 12px;
                font-weight: bold;
                color: $blueDefault;
            }
        }
    }
}
</style>
