/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-datatable" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <div class="button-area" v-if="editable && formMode">
            <bk-button
                v-if="add_btn"
                class="add-column button-item"
                size="small"
                @click="add_row">
                {{ i18n.add_text }}
            </bk-button>
            <template v-for="btn in table_buttons">
                <bk-button
                    v-if="btn.type !== 'import'"
                    class="button-item"
                    type="default"
                    size="small"
                    :key="btn.type"
                    @click.stop="onBtnClick(btn.callback)">
                    {{ btn.text}}
                </bk-button>
                <el-upload
                    v-else
                    ref="upload"
                    class="upload-btn button-item"
                    action="/"
                    :key="btn.type"
                    :show-file-list="false"
                    :on-change="importExcel"
                    :auto-upload="false">
                    <bk-button
                        slot="trigger"
                        size="small"
                        type="default">
                        {{ btn.text }}
                    </bk-button>
                </el-upload>
            </template>
        </div>
        <template v-if="Array.isArray(value) && !loading">
            <el-table
                style="width: 100%; font-size: 12px"
                border
                :data="dataList"
                :empty-text="empty_text"
                :fit="true"
                @row-click="onRowClick">
                <template v-for="(item, cIndex) in cellColumns">
                    <el-table-column
                        v-if="'hidden' in item.attrs ? !item.attrs.hidden : true"
                        :key="item.tag_code"
                        :index="cIndex"
                        :prop="item.tag_code"
                        :label="'name' in item.attrs ? item.attrs.name : ''"
                        :width="'width' in item.attrs ? item.attrs.width : ''"
                        align="center">
                        <template slot-scope="scope">
                            <component
                                :is="item.type === 'combine' ? 'form-group' : 'form-item'"
                                :ref="`row_${scope.$index}_${cIndex}_${item.tag_code}`"
                                :scheme="item"
                                :key="`${item.tag_code}_${cIndex}`"
                                :option="getColumnOptions(scope.$index)"
                                :value="scope.row[item.tag_code]"
                                :parent-value="scope.row"
                                @init="onInitColumn(scope, ...arguments)"
                                @change="onEditColumn(scope, ...arguments)">
                            </component>
                        </template>
                    </el-table-column>
                </template>
                <el-table-column v-if="editable && formMode"
                    prop="operation"
                    fixed="right"
                    align="center"
                    width="100"
                    :label="i18n.operate_text">
                    <template slot-scope="scope">
                        <div v-if="scope.$index === editRowNumber">
                            <a class="operate-btn" @click="onSave(scope.$index, scope.row)">{{ i18n.save_text }}</a>
                            <a class="operate-btn" @click="onCancel(scope.$index, scope.row)">{{ i18n.cancel_text }}</a>
                        </div>
                        <div v-else>
                            <a v-if="rowEditable" class="operate-btn" @click="onEdit(scope.$index, scope.row)">{{ i18n.edit_text }}</a>
                            <a v-if="deleteable" class="operate-btn" @click="onDelete(scope.$index, scope.row)">{{ i18n.delete_text }}</a>
                        </div>
                    </template>
                </el-table-column>
            </el-table>
            <el-pagination
                v-if="pagination && (tableValue.length / page_size) > 1 "
                layout="prev, pager, next"
                :total="tableValue.length"
                :page-size="page_size"
                :current-page.sync="currentPage">
            </el-pagination>
        </template>
        <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import { getFormMixins } from '../formMixins.js'
    import FormItem from '../FormItem.vue'
    import FormGroup from '../FormGroup.vue'
    import XLSX from 'xlsx'
    import atomFilter from '@/utils/atomFilter.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import bus from '@/utils/bus.js'

    export const attrs = {
        columns: {
            type: Array,
            required: false,
            default () {
                return [
                    {
                        tag_code: 'name',
                        type: 'text',
                        attrs: {
                            name: gettext('参数名称')
                        }
                    },
                    {
                        tag_code: 'type',
                        type: 'text',
                        attrs: {
                            name: gettext('参数类型'),
                            hidden: true
                        }
                    },
                    {
                        tag_code: 'value',
                        type: 'textarea',
                        attrs: {
                            name: gettext('参数值'),
                            editable: true
                        }
                    }
                ]
            },
            desc: 'initial data, which should be a array like [{tag config}]'
        },
        editable: {
            type: Boolean,
            required: false,
            default: true,
            desc: 'show edit and delete button or not'
        },
        rowEditable: {
            type: Boolean,
            required: false,
            default: true,
            desc: 'show edit button in a row'
        },
        deleteable: {
            type: Boolean,
            required: false,
            default: true,
            desc: 'show delete button in a row'
        },
        value: {
            type: [Array, String],
            required: false,
            default () {
                return []
            }
        },
        add_btn: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'show add button or not'
        },
        empty_text: {
            type: String,
            required: false,
            default: gettext('无数据'),
            desc: 'tips when data is empty'
        },
        remote_url: {
            type: [String, Function],
            required: false,
            default: '',
            desc: 'remote url when remote is true'
        },
        remote_data_init: {
            type: Function,
            required: false,
            default: function (data) {
                return data
            },
            desc: 'how to process data after getting remote data'
        },
        table_buttons: {
            type: Array,
            required: false,
            default () {
                return []
            },
            desc: 'dataTable buttons setting'
        },
        pagination: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'show table pagination'
        },
        page_size: {
            type: Number,
            required: false,
            default: 10,
            desc: 'number of items displayed per page'
        },
        row_click_handler: {
            type: Function,
            require: false,
            default: function () {},
            desc: 'on table row click callback function'
        }
    }
    export default {
        /**
         * notice：inject为了兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
         */
        inject: {
            node: {
                default () {
                    return {}
                }
            }
        },
        name: 'TagDatatable',
        components: {
            FormItem,
            FormGroup
        },
        mixins: [getFormMixins(attrs)],
        data () {
            return {
                cellColumns: [], // 单元格的 scheme 配置项
                editRowNumber: undefined,
                tableValue: tools.deepClone(this.value),
                loading: false,
                currentPage: 1,
                i18n: {
                    save_text: gettext('保存'),
                    cancel_text: gettext('取消'),
                    edit_text: gettext('编辑'),
                    operate_text: gettext('操作'),
                    delete_text: gettext('删除'),
                    add_text: gettext('添加')
                },
                pagination: {
                    current: 1
                }
            }
        },
        computed: {
            dataList () {
                if (this.pagination) {
                    const start = (this.currentPage - 1) * this.page_size
                    return this.tableValue.slice(start, start + this.page_size)
                }
                return this.tableValue
            }
        },
        watch: {
            remote_url (value) {
                this.remoteMethod()
            },
            value (val, oldVal) {
                this.tableValue = tools.deepClone(val)
                /**
                 * notice：兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
                 */
                if (this.tagCode === 'job_global_var' && this.formEdit) {
                    this.setOutputParams(val, oldVal)
                }
            },
            columns: {
                handler (value) {
                    // 去掉单元格第一层事件监听，改由 datable 组件外层管理
                    this.cellColumns = value.map(item => {
                        return {
                            ...item,
                            events: []
                        }
                    })
                },
                immediate: true
            }
        },
        mounted () {
            if (this.tagCode === 'job_global_var' && this.formEdit) {
                this.setOutputParams(this.value)
            }
            this.remoteMethod()
        },
        methods: {
            formatJson (filterVal, jsonData) {
                return jsonData.map(v => filterVal.map(j => v[j]))
            },
            export2Excel () {
                const tableHeader = []
                const tableData = []
                const filterVal = []
                for (let i = 0; i < this.columns.length; i++) {
                    const tagCode = this.columns[i].tag_code
                    const name = this.columns[i].attrs.name
                    tableHeader.push(name)
                    filterVal.push(tagCode)
                }
                tableData.push(tableHeader)
                const list = this.tableValue
                for (let i = 0; i < list.length; i++) {
                    const row = []
                    for (let j = 0; j < filterVal.length; j++) {
                        row.push(list[i][filterVal[j]])
                    }
                    tableData.push(row)
                }
                const wsName = 'Sheet1'
                const wb = XLSX.utils.book_new()
                const ws = XLSX.utils.aoa_to_sheet(tableData)
                XLSX.utils.book_append_sheet(wb, ws, wsName)
                XLSX.writeFile(wb, 'tableData.xlsx')
            },
            importExcel (file) {
                const types = file.name.split('.')[1]
                const fileType = ['xlsx', 'xlc', 'xlm', 'xls', 'xlt', 'xlw', 'csv'].some(item => item === types)
                if (!fileType) {
                    errorHandler(gettext('格式错误！请选择xlsx,xls,xlc,xlm,xlt,xlw或csv文件'))
                    return
                }
                this.file2Xce(file).then(tabJson => {
                    if (tabJson && tabJson.length > 0) {
                        // 首先做一个name与tag_code的对应字典
                        const nameToTagCode = {}
                        for (let i = 0; i < this.columns.length; i++) {
                            nameToTagCode[this.columns[i].attrs.name] = this.columns[i].tag_code
                        }
                        // 循环进行对比，如果发现与表头一致的name，就将其替换成tag_code
                        const excelValue = tabJson[0]['sheet']
                        for (let i = 0; i < excelValue.length; i++) {
                            for (const key in excelValue[i]) {
                                const newKey = nameToTagCode[key]
                                excelValue[i][newKey] = excelValue[i][key]
                                delete excelValue[i][key]
                            }
                        }
                        this._set_value(tabJson[0]['sheet'])
                    }
                })
            },
            file2Xce (file) {
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
            /**
             * 表格内每列的数据的校验
             * 筛选 ref 接口获得的子表单组件，分别调用 validate 方法
             */
            validateSubCom (index) {
                let isValid = true
                const startNameReg = `^row_${index}`
                for (const ref in this.$refs) {
                    let singleItemValid = true
                    if (new RegExp(startNameReg).test(ref)) {
                        const childComp = this.$refs[ref]
                        if (childComp && childComp.length) {
                            // ElTable 组件在添加固定列时，会生成两个相同的 ElTableBody 组件
                            singleItemValid = childComp[0].validate()
                        } else {
                            delete this.$refs[ref]
                        }

                        if (isValid) {
                            isValid = singleItemValid
                        }
                    }
                }
                return isValid
            },
            getColumnOptions (index) {
                return {
                    showHook: false,
                    showGroup: false,
                    showLabel: false,
                    editable: this.editRowNumber === index,
                    formMode: this.editRowNumber === index,
                    validateSet: ['required', 'custom', 'regex']
                }
            },
            /**
             * 触发同一行单元格注册的监听事件
             * @param {String} type 事件类型
             * @param {Number} row 行序号
             * @param {Number} col 列序号
             * @param {Any} value 当前表单值
             */
            triggerSameRowEvent (type, row, col, value) {
                const tagCode = this.columns[col].tag_code
                this.columns.forEach((col, index) => {
                    if (tagCode !== col.tag_code) {
                        const listenedEvents = (col.events || []).filter(item => item.source === tagCode && item.type === type)
                        if (listenedEvents.length > 0) {
                            let editingCell = null
                            const cells = this.$refs[`row_${row}_${index}_${col.tag_code}`]
                            if (cells && cells.length > 0) {
                                cells.some(crtCell => { // 找到 element table 提供给用户编辑的 body
                                    if (crtCell.$parent.fixed === undefined) {
                                        editingCell = crtCell
                                        return true
                                    }
                                })
                            }
                            if (editingCell) {
                                listenedEvents.forEach(event => {
                                    event.action.call(editingCell.$refs.tagComponent, value)
                                })
                            }
                        }
                    }
                })
            },
            onBtnClick (callback) {
                typeof callback === 'function' && callback.bind(this)()
            },
            onInitColumn (scope, val) {
                this.triggerSameRowEvent('init', scope.$index, scope.column.index, val)
            },
            onEdit (index, row) {
                if (this.pagination) {
                    index = (this.currentPage - 1) * this.page_size + index
                }
                this.editRowNumber = index
            },
            onEditColumn (scope, fieldsArr, val) {
                const field = fieldsArr.slice(-1)
                this.$set(this.tableValue[this.editRowNumber], field, val)
                this.triggerSameRowEvent('change', scope.$index, scope.column.index, val)
            },
            onDelete (index, row) {
                if (this.pagination) {
                    index = (this.currentPage - 1) * this.page_size + index
                }
                this.tableValue.splice(index, 1)
                this.updateForm(this.tableValue)
            },
            onSave (index, row) {
                if (this.pagination) {
                    index = (this.currentPage - 1) * this.page_size + index
                }
                const valueValid = this.validateSubCom(index)
                if (!valueValid) return

                this.editRowNumber = undefined
                this.updateForm(tools.deepClone(this.tableValue))
            },
            onCancel () {
                this.editRowNumber = undefined
                this.tableValue = tools.deepClone(this.value)
            },
            set_loading (loading) {
                this.loading = loading
            },
            add_row () {
                if (typeof this.editRowNumber === 'number') {
                    const valueValid = this.validateSubCom(this.editRowNumber)
                    if (!valueValid) return
                }

                const originData = {}
                this.columns.forEach((item, index) => {
                    let value = ''
                    if ('value' in item.attrs) {
                        value = item.attrs.value
                    } else if ('default' in item.attrs) {
                        value = item.attrs.default
                    } else {
                        value = atomFilter.getFormItemDefaultValue([item])[item.tag_code]
                    }
                    originData[item.tag_code] = value
                })
                this.editRowNumber = this.tableValue.length
                this.tableValue.push(originData)
            },
            remoteMethod () {
                const remote_url = typeof this.remote_url === 'function' ? this.remote_url() : this.remote_url
                if (remote_url) {
                    this.loading = true
                    const $this = this

                    $.ajax({
                        url: remote_url,
                        method: 'GET',
                        success: res => {
                            const data = $this.remote_data_init(res)
                            for (const i in data) {
                                data[i].width = Math.max(150, data[i].attrs.name.length * 20) + 'px'
                            }
                            $this.columns = data
                            $this.loading = false
                        },
                        error: () => {
                            $this.empty_text = gettext('请求表头数据失败，使用预置表头')
                            $this.loading = false
                        }
                    })
                }
            },
            /**
             * notice: 该方法为了兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
             * description: 切换作业模板时，将当前作业的全局变量添加到输出参数
             *
             * @param {Array} val 表格值
             * @param {Array} oldVal 表格变更之前的值
             */
            setOutputParams (val, oldVal) {
                bus.$emit('jobExecuteTaskOutputs', { val, oldVal })
            },
            onRowClick (row, column, event) {
                typeof this.row_click_handler && this.row_click_handler(row, column, event)
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    .tag-datatable {
        .el-table .tag-form.tag-input {
            margin-right: 0;
        }
        .rf-form-item {
            margin: 0;
        }
        /deep/ .rf-view-textarea-value textarea {
            text-align: center;
        }
        .el-pagination {
            text-align: right;
        }
    }
    .button-area {
        margin-bottom: 10px;
        overflow: hidden;
        .button-item {
            float: left;
            margin-right: 10px;
        }
    }
    .operate-btn {
        color: $blueDefault;
        white-space: nowrap;
        cursor: pointer;
    }
</style>
