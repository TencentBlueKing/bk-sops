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
        :title="i18n.title"
        width="600"
        :is-show.sync="isExportDialogShow"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div slot="content" class="export-container" v-bkloading="{isLoading: exportPending, opacity: 1}">
            <div class="common-form-item">
                <label>{{ i18n.choose }}</label>
                <div class="common-form-content">
                    <bk-selector
                        :is-loading="loading"
                        :list="templateList"
                        :selected.sync="selectedList"
                        :searchable="true"
                        :has-children='true'
                        :multi-select="true"
                        :allow-clear="true">
                    </bk-selector>
                </div>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
export default {
    name: 'ExportTemplateDialog',
    props: ['isExportDialogShow', 'businessInfoLoading', 'exportPending'],
    data () {
        return {
            listLoading: false,
            templateList: [],
            selectedList: [],
            i18n: {
                title: gettext('导出流程'),
                choose: gettext('选择流程')
            }
        }
    },
    computed: {
        ...mapState({
            'businessBaseInfo': state => state.template.businessBaseInfo
        }),
        loading () {
            return this.listLoading || this.businessInfoLoading
        }
    },
    created () {
        this.getTemplateData()
    },
    methods: {
        ...mapActions('templateList/', [
            'loadTemplateList'
        ]),
        async getTemplateData () {
            this.listLoading = true
            try {
                const respData = await this.loadTemplateList()
                const list = respData.objects
                this.templateList = this.getGroupedList(list)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.listLoading = false
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
        onConfirm () {
            if (this.selectedList.length) {
                this.$emit('onExportConfirm', this.selectedList)
            } else {
                this.$bkMessage({
                    message: gettext('请选择需要导出的流程'),
                    theme: 'warning'
                })
            }
        },
        onCancel () {
            this.$emit('onExportCancel')
        }
    }
}
</script>
<style lang="scss" scoped>
.export-container {
    padding: 30px 0;
}
</style>
