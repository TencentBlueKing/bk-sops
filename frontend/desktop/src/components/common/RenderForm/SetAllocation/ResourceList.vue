/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="resource-list">
        <div class="opt-btns" v-if="!viewValue">
            <bk-button
                theme="default"
                size="small"
                :disabled="!editable"
                @click="$emit('update:showFilter', true)">
                {{ $t('资源筛选') }}
            </bk-button>
            <bk-button
                theme="default"
                size="small"
                :disabled="!editable"
                @click="exportData">
                {{ $t('导出') }}
            </bk-button>
            <el-upload
                ref="upload"
                class="upload-btn"
                action="/"
                :disabled="!editable"
                :show-file-list="false"
                :on-change="importData"
                :auto-upload="false">
                <bk-button
                    slot="trigger"
                    size="small"
                    :disabled="!editable"
                    theme="default">
                    {{ $t('导入') }}
                </bk-button>
            </el-upload>
        </div>
        <bk-alert v-if="hasDiff" :class="{ 'alert-disabled': !editable }" ref="diffAlert" type="warning" style="margin-bottom: 10px;" :show-icon="false">
            <div class="diff-alert" slot="title">
                <span>{{ $t('变量保存数据与最新的CMDB集群配置存在差异，是否更新变量数据？') }}</span>
                <bk-link theme="primary" @click="updateDiffData">{{ $t('确认') }}</bk-link>
            </div>
        </bk-alert>
        <div class="data-table">
            <bk-table
                v-if="!loading"
                :data="dataList"
                :pagination="pagination"
                @page-change="handlePageChange">
                <bk-table-column
                    v-for="(item, colIndex) in cols"
                    :key="item.config.tag_code"
                    :label="item.config.attrs.name"
                    :min-width="item.width"
                    :index="colIndex"
                    show-overflow-tooltip
                    :render-header="renderTableHeader"
                    :prop="item.config.tag_code"
                    :fixed="item.config.tag_code === 'tb_btns' ? 'right' : false"
                    :align="item.config.tag_code === 'tb_btns' ? 'center' : 'left'">
                    <template slot-scope="props">
                        <template v-if="item.config.tag_code !== 'tb_btns'">
                            <render-form
                                :ref="`row_${(pagination.current - 1) * pagination.limit + props.$index}_${item.config.tag_code}`"
                                :scheme="[item.config]"
                                :form-option="getCellOption((pagination.current - 1) * pagination.limit + props.$index)"
                                v-model="props.row[item.config.tag_code]">
                            </render-form>
                        </template>
                        <template v-else>
                            <template v-if="editRow !== (pagination.current - 1) * pagination.limit + props.$index">
                                <bk-button :text="true" :disabled="!editable" @click="rowEditClick(props)">{{ $t('编辑') }}</bk-button>
                                <bk-button :text="true" :disabled="!editable" @click="rowDelClick(props)">{{ $t('删除') }}</bk-button>
                            </template>
                            <template v-else>
                                <bk-button :text="true" :disabled="!editable" @click="rowSaveClick(props, item.config.tag_code)">{{ $t('保存') }}</bk-button>
                                <bk-button :text="true" :disabled="!editable" @click="rowCancelClick">{{ $t('取消') }}</bk-button>
                            </template>
                        </template>
                    </template>
                </bk-table-column>
                <template v-slot:empty>
                    <no-data :style="{ background: 'transparent' }"></no-data>
                </template>
            </bk-table>
        </div>
        <separator-select :editable="editable" :value="separator" @change="$emit('update:separator', $event)"></separator-select>
    </div>
</template>
<script >
    import '@/utils/i18n.js'
    import * as XLSX from 'xlsx'
    import tools from '@/utils/tools.js'
    import RenderForm from '../RenderForm.vue'
    import SeparatorSelect from '../SeparatorSelect.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'ResourceList',
        components: {
            RenderForm,
            SeparatorSelect,
            NoData
        },
        props: {
            loading: Boolean,
            hasDiff: Boolean,
            editable: {
                type: Boolean,
                default: true
            },
            viewValue: { // 查看值模式，不需要要编辑表单操作
                type: Boolean,
                default: false
            },
            cols: {
                type: Array
            },
            config: { // 资源筛选表单值
                type: Object,
                default () {
                    return {}
                }
            },
            value: { // 表格值
                type: Array,
                default () {
                    return []
                }
            },
            separator: String
        },
        data () {
            return {
                cellOption: {
                    showGroup: false,
                    showHook: false,
                    showLabel: false,
                    formMode: false
                },
                editRow: '',
                tableData: tools.deepClone(this.value),
                pagination: {
                    current: 1,
                    count: this.value.length,
                    limit: 10,
                    'show-limit': false
                }
            }
        },
        computed: {
            dataList () {
                const { current, limit } = this.pagination
                const start = (current - 1) * limit
                return this.tableData.slice(start, start + limit)
            }
        },
        watch: {
            value: {
                handler (val) {
                    this.tableData = tools.deepClone(val)
                    this.pagination.count = val.length
                }
            },
            deep: true
        },
        methods: {
            renderTableHeader (h, { column, $index }) {
                return h('p', {
                    class: 'label-text',
                    directives: [{
                        name: 'bk-overflow-tips'
                    }]
                }, [
                    column.label
                ])
            },
            exportData () {
                const sheetHeader = []
                this.cols.forEach(item => {
                    const tagCode = item.config.tag_code
                    const name = item.config.attrs.name
                    if (tagCode !== 'tb_btns') {
                        const headerName = item.config.module ? name : `${name}(${tagCode})`
                        sheetHeader.push(headerName)
                    }
                })
                const sheetValue = this.value.map(rowData => {
                    const dataItem = []
                    this.cols.forEach(col => {
                        const tagCode = col.config.tag_code
                        if (tagCode !== 'tb_btns') {
                            dataItem.push(rowData[col.config.tag_code][col.config.tag_code])
                        }
                    })
                    return dataItem
                })
                const sheetData = [sheetHeader, ...sheetValue]

                const wsName = 'Sheet1'
                const wb = XLSX.utils.book_new()
                const ws = XLSX.utils.aoa_to_sheet(sheetData)
                XLSX.utils.book_append_sheet(wb, ws, wsName)
                XLSX.writeFile(wb, 'resource_data.xlsx')
            },
            importData (file) {
                const types = file.name.split('.')[1]
                const fileTypeValid = ['xlsx', 'xlc', 'xlm', 'xls', 'xlt', 'xlw', 'csv'].some(item => item === types)
                if (!fileTypeValid) {
                    this.$bkMessage({
                        theme: 'error',
                        message: this.$t('格式错误！请选择xlsx,xls,xlc,xlm,xlt,xlw或csv文件'),
                        delay: 10000
                    })
                    return
                }
                this.readFileData(file).then(data => {
                    if (data && data.length > 0) {
                        this.$emit('importData', data[0].sheet)
                        this.pagination.current = 1
                    }
                })
            },
            // 将本地Excel文件的二进制数据转化为json数据
            readFileData (file) {
                return new Promise(function (resolve, reject) {
                    const reader = new FileReader()
                    reader.onload = function (e) {
                        const data = e.target.result
                        const wb = XLSX.read(data, {
                            type: 'binary'
                        })
                        const result = []
                        wb.SheetNames.forEach((sheetName) => {
                            result.push({
                                sheetName: sheetName,
                                sheet: XLSX.utils.sheet_to_json(wb.Sheets[sheetName])
                            })
                        })
                        resolve(result)
                    }
                    reader.readAsBinaryString(file.raw)
                })
            },
            updateDiffData () {
                this.$refs.diffAlert.handleClose()
                this.$emit('handleDiff')
            },
            // 单元格内的renderform表单属性配置
            getCellOption (index) {
                const options = Object.assign({}, this.cellOption)
                if (index === this.editRow) {
                    options.formMode = true
                }

                return options
            },
            validateRow (name) {
                const refs = Object.keys(this.$refs).filter(item => item.startsWith(name))
                let valid = true
                refs.forEach(item => {
                    if (this.$refs[item].length > 0) {
                        const col = this.$refs[item][1] || this.$refs[item][0]
                        const result = col.validate() // bk-table 里的body会有两份内容
                        if (!result) {
                            valid = false
                        }
                    } else {
                        delete this.$refs[item]
                    }
                })
                return valid
            },
            rowEditClick (data) {
                this.editRow = (this.pagination.current - 1) * this.pagination.limit + data.$index
            },
            rowDelClick (row) {
                const index = (this.pagination.current - 1) * this.pagination.limit + row.$index
                if (this.dataList.length === 1 && this.pagination.current > 1) {
                    this.pagination.current -= 1
                }
                this.editRow = ''
                this.tableData.splice(index, 1)
                this.$emit('update', tools.deepClone(this.tableData))
            },
            rowSaveClick (data) {
                let index = data.index
                if ('$index' in data) {
                    index = (this.pagination.current - 1) * this.pagination.limit + data.$index
                }
                const valid = this.validateRow(`row_${index}`)
                if (valid) {
                    this.editRow = ''
                    this.$emit('update', tools.deepClone(this.tableData))
                }
            },
            rowCancelClick (data) {
                this.editRow = ''
                this.tableData = tools.deepClone(this.value)
            },
            handlePageChange (val) {
                this.pagination.current = val
            },
            validate () {
                // 当前正在编辑行时，自动触发保存
                if (typeof this.editRow === 'number') {
                    this.rowSaveClick({ 'index': this.editRow })
                }
                return this.validateRow(`row_`)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .opt-btns {
        margin-bottom: 10px;
        ::v-deep .bk-button {
            font-size: 12px;
        }
        ::v-deep .upload-btn {
            display: inline-block;
            font-size: 12px;
        }
    }
    .diff-alert {
        display: flex;
        justify-content: space-between;
        align-items: center;
        ::v-deep .bk-link-text {
            font-size: 12px;
        }
    }
    .alert-disabled {
        color: #ccc;
        cursor: not-allowed;
        ::v-deep .bk-link-text {
            color: #ccc;
            cursor: not-allowed;
        }
    }
    .data-table {
        ::v-deep .bk-table tbody .cell {
            padding-top: 16px;
            padding-bottom: 16px;
        }
    }
</style>
