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
    <div class="tag-datatable">
        <template v-if="editable && formMode">
            <bk-button
                v-if="add_btn"
                class="add-column"
                size="small"
                @click="add_row">
                {{ i18n.add_text }}
            </bk-button>
            <div v-for="btn in table_buttons" :key="btn.type" class="table-buttons">
                <bk-button
                    v-if="btn.type !== 'import'"
                    type="default"
                    size="small"
                    @click="onBtnClick(btn.callback)">
                    {{ btn.text}}
                </bk-button>
                <el-upload
                    v-else
                    ref="upload"
                    class="upload-btn"
                    action="/"
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
            </div>
        </template>
        <el-table
            v-if="Array.isArray(value)"
            style="width: 100%; font-size: 12px"
            :data="currPageValue"
            :empty-text="empty_text"
            @row-click="onRowClick"
            v-loading="loading"
            border>
            <template v-for="(item, cIndex) in columns">
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
                            :option="getColumnOptions(scope.$index)"
                            :value="scope.row[item.tag_code]"
                            :parent-value="scope.row"
                            @change="onEditColumn">
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
                        <a class="operate-btn" @click="onEdit(scope.$index, scope.row)">{{ i18n.edit_text }}</a>
                        <a v-if="add_btn" class="operate-btn" @click="onDelete(scope.$index, scope.row)">{{ i18n.delete_text }}</a>
                    </div>
                </template>
            </el-table-column>
        </el-table>
        <div class="table-pagination">
            <el-pagination
                v-if="show_pagination"
                layout="prev, pager, next"
                :current-page="pagination.current"
                :page-size="limit"
                :total="tableValue.length"
                @current-change="handlerPageChange">
            </el-pagination>
        </div>
        <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations } from 'vuex'
    import tools from '@/utils/tools.js'
    import { getFormMixins } from '../formMixins.js'
    import FormItem from '../FormItem.vue'
    import FormGroup from '../FormGroup.vue'
    import XLSX from 'xlsx'
    import { errorHandler } from '@/utils/errorHandler.js'

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
            type: String,
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
        show_pagination: {
            type: Boolean,
            require: false,
            default: false,
            desc: 'show table pagination or not'
        },
        limit: {
            type: Number,
            require: false,
            default: 5,
            desc: 'the number of per page'
        },
        row_click_handler_name: {
            type: String,
            require: false,
            default: '',
            desc: 'on table row click callback function name'
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
                editRowNumber: undefined,
                tableValue: tools.deepClone(this.value),
                loading: false,
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
            /**
             * notice：兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
             */
            ...mapState({
                'atomForm': state => state.atomForm,
                'constants': state => state.template.constants
            }),
            currPageValue () {
                if (this.show_pagination) {
                    const start = (this.pagination.current - 1) * this.limit
                    const end = start + this.limit
                    return this.tableValue.slice(start, end)
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
            }
        },
        mounted () {
            if (this.tagCode === 'job_global_var' && this.formEdit) {
                this.setOutputParams()
            }
            this.remoteMethod()
        },
        methods: {
            /**
             * notice：兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
             */
            ...mapMutations('atomForm/', [
                'setAtomOutput'
            ]),
            ...mapMutations('template/', [
                'deleteVariable'
            ]),
            formatJson (filterVal, jsonData) {
                return jsonData.map(v => filterVal.map(j => v[j]))
            },
            export2Excel () {
                require.ensure([], () => {
                    const TableToExcel = require('table-to-excel')
                    const tableToExcel = new TableToExcel()
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
                    tableToExcel.render(tableData)
                })
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
                        this.tableValue = tabJson[0]['sheet']
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
            onBtnClick (callback) {
                typeof callback === 'function' && callback()
            },
            onEdit (index, row) {
                this.editRowNumber = index
            },
            onEditColumn (fieldsArr, val) {
                const field = fieldsArr.slice(-1)
                this.$set(this.tableValue[this.editRowNumber], field, val)
            },
            onDelete (index, row) {
                this.tableValue.splice(index, 1)
                this.updateForm(this.tableValue)
            },
            onSave (index, row) {
                const valueValid = this.validateSubCom(index)
                if (!valueValid) return

                this.editRowNumber = undefined
                this.updateForm(tools.deepClone(this.tableValue))
            },
            onCancel (index, row) {
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
                    originData[item.tag_code] = item.default || ''
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
                const specialAtom = 'job_execute_task'
                const version = this.atomForm.SingleAtomVersionMap[specialAtom]
                if (Array.isArray(this.value)) {
                    const atomOutput = this.atomForm.form[specialAtom][version].output.slice(0)
                    this.value.forEach(item => {
                        if (typeof item.type === 'number' && item.type !== 2 && item.category === 1) {
                            atomOutput.push({
                                key: item.name,
                                name: item.name
                            })
                        }
                    })
                    this.setAtomOutput({
                        atomType: specialAtom,
                        outputData: atomOutput,
                        version
                    })
                }
                // 删除输出变量已勾选的全局变量
                if (oldVal && this.node.id) {
                    oldVal.forEach(item => {
                        if (val.find(v => v.id === item.id)) {
                            return
                        }
                        if (typeof item.type === 'number' && item.type !== 2) {
                            Object.keys(this.constants).some(key => {
                                const cst = this.constants[key]
                                const sourceInfo = cst.source_info[this.node.id]
                                if (sourceInfo && sourceInfo.indexOf(item.name) > -1) {
                                    this.deleteVariable(key)
                                    return true
                                }
                            })
                        }
                    })
                }
            },
            handlerPageChange (val) {
                this.pagination.current = val
            },
            // 表格单行点击
            onRowClick (row, column, event) {
                const handlerName = this.row_click_handler_name
                if (handlerName && typeof this[handlerName] === 'function') {
                    this[handlerName](row, column, event)
                }
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
    }
    .add-column {
        margin-bottom: 10px;
    }
    .operate-btn {
        color: $blueDefault;
        white-space: nowrap;
        cursor: pointer;
    }
    .table-buttons{
        display: inline-block;
        margin-left: 10px;
        margin-bottom: 15px;
    }
    .table-pagination {
        margin-top: 20px;
    }
</style>
