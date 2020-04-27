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
    <div class="resource-list">
        <div class="opt-btns" v-if="!viewValue">
            <bk-button
                theme="default"
                :disabled="!editable"
                @click="$emit('update:showFilter', true)">
                {{ i18n.resourceFilter }}
            </bk-button>
            <bk-button
                theme="default"
                :disabled="!editable"
                @click="exportData">
                {{ i18n.export }}
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
                    :disabled="!editable"
                    theme="default">
                    {{ i18n.import }}
                </bk-button>
            </el-upload>
        </div>
        <div class="data-table">
            <bk-table :data="tableData" :fit="false">
                <bk-table-column
                    v-for="(item, colIndex) in cols"
                    :key="item.config.tag_code"
                    :label="item.config.attrs.name"
                    :width="item.width"
                    :index="colIndex"
                    :prop="item.config.tag_code"
                    :fixed="item.config.tag_code === 'tb_btns' ? 'right' : false"
                    :align="item.config.tag_code === 'tb_btns' ? 'center' : 'left'">
                    <template slot-scope="props">
                        <template v-if="item.config.tag_code !== 'tb_btns'">
                            <render-form
                                :ref="`row_${props.$index}_${item.config.tag_code}`"
                                :scheme="[item.config]"
                                :form-option="getCellOption(props.$index)"
                                v-model="props.row[item.config.tag_code]">
                            </render-form>
                        </template>
                        <template v-else>
                            <template v-if="editRow !== props.$index">
                                <bk-button :text="true" :disabled="!editable" @click="rowEditClick(props)">{{ i18n.edit }}</bk-button>
                                <bk-button :text="true" :disabled="!editable" @click="rowDelClick(props)">{{ i18n.delete }}</bk-button>
                            </template>
                            <template v-else>
                                <bk-button :text="true" :disabled="!editable" @click="rowSaveClick(props, item.config.tag_code)">{{ i18n.save }}</bk-button>
                                <bk-button :text="true" :disabled="!editable" @click="rowCancelClick">{{ i18n.cancel }}</bk-button>
                            </template>
                        </template>
                    </template>
                </bk-table-column>
                <template v-slot:empty>
                    <no-data :style="{ background: 'transparent' }"></no-data>
                </template>
            </bk-table>
        </div>
    </div>
</template>
<script >
    import '@/utils/i18n.js'
    import XLSX from 'xlsx'
    import tools from '@/utils/tools.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import RenderForm from '../RenderForm.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'ResourceList',
        components: {
            RenderForm,
            NoData
        },
        props: {
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
            }
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
                i18n: {
                    resourceFilter: gettext('资源筛选'),
                    export: gettext('导出'),
                    import: gettext('导入'),
                    edit: gettext('编辑'),
                    delete: gettext('删除'),
                    save: gettext('保存'),
                    cancel: gettext('取消')
                }
            }
        },
        watch: {
            value: {
                handler (val) {
                    this.tableData = tools.deepClone(val)
                }
            },
            deep: true
        },
        methods: {
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
                const fileType = ['xlsx', 'xlc', 'xlm', 'xls', 'xlt', 'xlw', 'csv'].some(item => item === types)
                if (!fileType) {
                    errorHandler(gettext('格式错误！请选择xlsx,xls,xlc,xlm,xlt,xlw或csv文件'))
                    return
                }
                this.readFileData(file).then(data => {
                    if (data && data.length > 0) {
                        this.$emit('importData', data[0].sheet)
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
                        const result = this.$refs[item][1].validate() // bk-table 里的body会有两份内容
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
                this.editRow = data.$index
            },
            rowDelClick (row) {
                this.tableData.splice(row.$index, 1)
                this.$emit('update', tools.deepClone(this.tableData))
            },
            rowSaveClick (data) {
                const valid = this.validateRow(`row_${data.$index}`)
                if (valid) {
                    this.editRow = ''
                    this.$emit('update', tools.deepClone(this.tableData))
                }
            },
            rowCancelClick (data) {
                this.editRow = ''
                this.tableData = tools.deepClone(this.value)
            },
            validate () {
                return this.validateRow(`row_`)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .opt-btns {
        margin-bottom: 20px;
        /deep/ .bk-button {
            font-size: 12px;
        }
        /deep/ .upload-btn {
            display: inline-block;
            font-size: 12px;
        }
    }
    .data-table {
        /deep/ .bk-table tbody .cell {
            padding-top: 16px;
            padding-bottom: 16px;
        }
    }
</style>
