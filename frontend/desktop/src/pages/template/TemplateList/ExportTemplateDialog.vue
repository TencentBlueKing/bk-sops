/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
        ext-cls="common-dialog export-tpl-dialog"
        :title="$t('导出为') + (type === 'dat' ? 'DAT' : 'YAML')"
        :mask-close="false"
        :value="isExportDialogShow"
        :header-position="'left'"
        :auto-close="false"
        @cancel="closeDialog">
        <div class="export-container" v-bkloading="{ isLoading: businessInfoLoading, opacity: 1, zIndex: 100 }">
            <bk-input
                class="search-input"
                v-model.trim="keywords"
                :clearable="true"
                :placeholder="$t('请输入流程名称')"
                :right-icon="'icon-search'"
                @input="onSearchInput">
            </bk-input>
            <div class="template-list" v-bkloading="{ isLoading: tplLoading, opacity: 1, zIndex: 100 }">
                <bk-table
                    v-if="templateList.length"
                    :data="templateList"
                    :row-class-name="handlerRowClassName"
                    @select-all="onSelectAllTemplate">
                    <bk-table-column :resizable="false" width="50" :render-header="renderHeaderCheckbox">
                        <template slot-scope="props">
                            <bk-checkbox :value="props.row.isChecked" @change="onSelectTemplate(props.row)"></bk-checkbox>
                        </template>
                    </bk-table-column>
                    <bk-table-column :resizable="false" label="ID" prop="id" width="120"></bk-table-column>
                    <bk-table-column :resizable="false" label="流程名称" prop="name"></bk-table-column>
                    <div class="is-loading" slot="append" v-if="!isPageOver && isLoading" v-bkloading="{ isLoading: isLoading, zIndex: 100 }"></div>
                </bk-table>
                <NoData v-else class="empty-template"></NoData>
            </div>
        </div>
        <div class="footer-wrap" slot="footer">
            <div class="footer-left">
                <bk-checkbox
                    class="template-checkbox"
                    :value="isTplInPanelAllSelected"
                    @change="onSelectAllClick">
                    {{ $t('全选所有流程') }}
                </bk-checkbox>
                <p>
                    {{ $t('已选择') }}
                    <span class="selected-num">{{ isHasSelected }}</span>
                    {{ $t('条流程') }}
                </p>
            </div>
            <div class="operate-area">
                <span class="export-tips">{{ exportTips }}</span>
                <bk-button
                    theme="primary"
                    :disabled="!isHasSelected"
                    :loading="exportPending"
                    @click="onConfirm">
                    {{ $t('确定') }}
                </bk-button>
                <bk-button @click="closeDialog">{{ $t('取消') }}</bk-button>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import toolsUtils from '@/utils/tools.js'
    import { mapActions } from 'vuex'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    export default {
        name: 'ExportTemplateDialog',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            isExportDialogShow: Boolean,
            businessInfoLoading: Boolean,
            common: String,
            project_id: [Number, String],
            selected: Array,
            type: String
        },
        data () {
            return {
                tplLoading: false,
                exportPending: false,
                isTplInPanelAllSelected: false,
                isCheckedDisabled: false,
                templateList: [],
                keywords: '',
                isHasSelected: 0,
                tableScroller: null,
                isLoading: false,
                pollingTimer: null,
                isThrottled: false,
                isPageOver: false,
                pageSize: 15,
                currentPage: 1,
                totalPage: null,
                totalCount: 0
            }
        },
        computed: {
            exportTips () {
                return this.type === 'dat' ? i18n.t('DAT文件导出后不可编辑，导出时不能自由覆盖模板') : i18n.t('YAML文件导出后可以编辑，导入时可以自由覆盖模板但节点会丢失位置信息')
            },
            reqPerm () {
                return this.common ? ['common_flow_view'] : ['flow_view']
            }
        },
        watch: {
            isExportDialogShow (val) {
                if (val) {
                    const selected = this.selected
                    if (selected && selected.length > 0) {
                        const idList = selected.map(item => item.id)
                        this.templateList.forEach(template => {
                            this.$set(template, 'isChecked', idList.includes(template.id))
                        })
                        this.isHasSelected = selected.length
                        this.isTplInPanelAllSelected = selected.length === this.totalCount
                    }
                    if (!this.tableScroller) {
                        this.tableScroller = this.$el.querySelector('.export-tpl-dialog .bk-table-body-wrapper')
                        this.tableScroller.addEventListener('scroll', this.handleTableScroll, { passive: true })
                    }
                }
            }
        },
        created () {
            this.getTemplateData()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        beforeDestroy () {
            if (this.tableScroller) {
                this.tableScroller.removeEventListener('scroll', this.handleTableScroll)
            }
        },
        methods: {
            ...mapActions('templateList/', [
                'loadTemplateList',
                'templateExport'
            ]),
            // 滚动加载
            handleTableScroll () {
                if (!this.isPageOver && !this.isThrottled && !this.isLoading) {
                    this.isThrottled = true
                    this.pollingTimer = setTimeout(() => {
                        this.isThrottled = false
                        const el = this.tableScroller
                        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 10) {
                            this.currentPage += 1
                            clearTimeout(this.pollingTimer)
                            this.isLoading = true
                            this.getTemplateData(true)
                        }
                    }, 200)
                }
            },
            // 自定义头部
            renderHeaderCheckbox (h) {
                const self = this
                return h('div', {
                    'class': {
                        'select-all-cell': true,
                        'full-selected': this.isTplInPanelAllSelected
                    }
                }, [
                    h('bk-checkbox', {
                        props: {
                            indeterminate: !!this.isHasSelected,
                            value: this.getTplIsAllSelected()
                        },
                        on: {
                            change: function (val) {
                                self.onSelectAllTemplate(val)
                            }
                        }
                    })
                ])
            },
            // 获取模板列表
            async getTemplateData (isMore) {
                this.tplLoading = !this.isLoading
                this.isCheckedDisabled = true
                try {
                    const offset = (this.currentPage - 1) * this.pageSize
                    const data = {
                        limit: this.pageSize,
                        offset,
                        pipeline_template__name__icontains: this.keywords || undefined
                    }
                    if (this.common) {
                        data.common = 1
                    } else {
                        data.project__id = this.project_id
                    }
                    const respData = await this.loadTemplateList(data)
                    this.totalCount = respData.meta.total_count
                    this.totalPage = Math.ceil(respData.meta.total_count / this.pageSize)
                    this.isPageOver = this.currentPage === this.totalPage

                    const idList = this.selected.map(item => item.id) || []
                    const templateList = respData.objects.map(item => {
                        const isChecked = this.isTplInPanelAllSelected ? true : idList.includes(item.id)
                        this.$set(item, 'isChecked', isChecked)
                        return item
                    })
                    if (isMore) {
                        this.templateList.push(...templateList)
                    } else {
                        this.templateList = templateList
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.tplLoading = false
                    this.isLoading = false
                    this.isCheckedDisabled = false
                }
            },
            // 判断模板列表是否为全选
            getTplIsAllSelected () {
                if (!this.templateList.length) {
                    return false
                }
                return this.templateList.every(template => template.isChecked)
            },
            // 判断模板列表是否勾选
            getTplIsSelected () {
                const selected = this.templateList.reduce((acc, cur) => {
                    if (cur.isChecked) {
                        acc.push(cur.id)
                    }
                    return acc
                }, [])
                return selected && selected.length
            },
            // 搜索
            searchInputhandler () {
                this.currentPage = 1
                this.getTemplateData()
            },
            // 勾选模板
            onSelectTemplate (row) {
                if (this.hasPermission(this.reqPerm, row.auth_actions)) {
                    row.isChecked = !row.isChecked
                    this.isTplInPanelAllSelected = this.getTplIsAllSelected()
                    if (this.selected.length === this.totalCount) {
                        this.isHasSelected = row.isChecked ? this.isHasSelected + 1 : this.isHasSelected - 1
                    } else {
                        this.isHasSelected = this.getTplIsSelected()
                    }
                } else {
                    let permissionData
                    if (this.common) {
                        permissionData = {
                            common_flow: [{
                                id: row.id,
                                name: row.name
                            }]
                        }
                    } else {
                        permissionData = {
                            flow: [{
                                id: row.id,
                                name: row.name
                            }],
                            project: [{
                                id: row.project.id,
                                name: row.project.name
                            }]
                        }
                    }
                    this.applyForPermission(this.reqPerm, row.auth_actions, permissionData)
                }
            },
            // 设置表格行
            handlerRowClassName ({ row }) {
                return row.isChecked ? 'select-row' : ''
            },
            // 当前页全选
            onSelectAllTemplate () {
                const isAllSelected = this.getTplIsAllSelected()
                this.templateList.forEach(item => {
                    item.isChecked = !isAllSelected
                })
                this.isHasSelected = this.getTplIsSelected()
                this.isTplInPanelAllSelected = !isAllSelected && this.isPageOver
            },
            // 跨页全选
            onSelectAllClick () {
                if (this.isCheckedDisabled) {
                    return
                }

                this.templateList.forEach(template => {
                    if (this.hasPermission(this.reqPerm, template.auth_actions)) {
                        template.isChecked = !this.isTplInPanelAllSelected
                    }
                })
                this.isTplInPanelAllSelected = !this.isTplInPanelAllSelected
                this.isHasSelected = this.isTplInPanelAllSelected ? this.totalCount : 0
            },
            // 确定导出
            async onConfirm () {
                const list = this.templateList.reduce((acc, cur) => {
                    if (cur.isChecked) {
                        acc.push(cur.id)
                    }
                    return acc
                }, [])
                try {
                    this.exportPending = true
                    const resp = await this.templateExport({
                        list,
                        type: this.type,
                        common: this.common,
                        is_full: this.isTplInPanelAllSelected
                    })
                    if (resp.result) {
                        this.closeDialog()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.exportPending = false
                }
            },
            // 取消导出
            closeDialog () {
                this.resetData()
                this.$emit('update:isExportDialogShow', false)
            },
            // 数据重置
            resetData () {
                this.templateList.forEach(template => {
                    template.isChecked = false
                })
                this.keywords = ''
                this.isHasSelected = false
                this.isTplInPanelAllSelected = false
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
    height: 450px;
    .search-wrapper {
        padding: 0 18px 0 20px;
    }
    .search-input {
        width: 266px;
        padding: 15px 0 8px 24px;
    }
    .project-selector {
        position: absolute;
        top: 20px;
        width: 255px;
        height: 32px;
    }
    .template-list {
        height: calc(100% - 54px);
        padding: 0 14px 0 24px;
    }
    /deep/.select-all-cell {
        display: flex;
        align-items: center;
        &.full-selected {
            .bk-form-checkbox {
                .bk-checkbox {
                    background: #ffffff;
                    &:after {
                        border-color: #3a84ff;
                    }
                }
            }
        }
    }
    /deep/.select-row {
        background: #e1ecff;
    }
    .is-loading {
        height: 42px;
        border-bottom: 1px solid #dfe0e5;
        background: #fff;
    }
}
</style>
<style lang="scss">
    @import '@/scss/mixins/scrollbar.scss';
    .export-tpl-dialog {
        .bk-dialog-content {
            height: 560px;
            .bk-dialog-tool {
                min-height: 0;
            }
            .bk-dialog-header {
                margin-top: 0;
                flex-shrink: 0;
            }
        }
        .footer-wrap {
            display: flex;
            align-items: center;
            justify-content: space-between;
            .footer-left {
                display: flex;
                align-items: center;
                p {
                    font-size: 12px;
                    margin-left: 10px;
                    color: #63656e;
                    .selected-num {
                        margin: 0 2px;
                    }
                }
            }
        }
        .export-tips {
            font-size: 12px;
            color: #63656e;
        }
        .bk-table-body-wrapper {
            height: 352px;
            overflow-y: auto;
            @include scrollbar;
        }
        .search-input .control-icon {
            transform: translateY(-25%) !important;
        }
    }
</style>
