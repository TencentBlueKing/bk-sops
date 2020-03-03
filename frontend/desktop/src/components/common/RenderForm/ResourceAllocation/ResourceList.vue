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
        <div class="opt-btns">
            <bk-button theme="default" @click="$emit('update:showFilter', true)">{{ i18n.resourceFilter }}</bk-button>
            <bk-button theme="default" @click="exportData">{{ i18n.export }}</bk-button>
            <bk-button theme="default" @click="importData">{{ i18n.import }}</bk-button>
        </div>
        <div class="data-table">
            <bk-table :data="colsData">
                <bk-table-column
                    v-for="item in cols"
                    :key="item.config.tag_code"
                    :label="item.config.attrs.name"
                    :width="item.width"
                    :prop="item.config.tag_code"
                    :fixed="item.config.tag_code === 'tb_btns' ? 'right' : false"
                    :align="item.config.tag_code === 'tb_btns' ? 'center' : 'left'">
                    <template slot-scope="props">
                        <template v-if="item.config.tag_code === 'tb_btns'">
                            <render-form
                                :scheme="props.row.config"
                                :form-option="cellOption"
                                v-model="props.row.data">
                            </render-form>
                        </template>
                        <template v-else>
                            <template v-if="editRow === props.row.index">
                                <bk-button :text="true" @click="rowEditClick">{{ i18n.edit }}</bk-button>
                                <bk-button :text="true" @click="rowDelClick">{{ i18n.delete }}</bk-button>
                            </template>
                            <template v-else>
                                <bk-button :text="true" @click="rowSaveClick">{{ i18n.save }}</bk-button>
                                <bk-button :text="true" @click="rowCancelClick">{{ i18n.cancel }}</bk-button>
                            </template>
                        </template>
                    </template>
                </bk-table-column>
                <template v-slot:empty>
                    <no-data></no-data>
                </template>
            </bk-table>
        </div>
    </div>
</template>
<script >
    import '@/utils/i18n.js'
    import RenderForm from '../RenderForm.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'ResourceList',
        components: {
            RenderForm,
            NoData
        },
        props: {
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
                    showLabel: false
                },
                editRow: '',
                colsData: this.value,
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
        watch: {},
        mounted () {},
        methods: {
            exportData () {
                // const tableHeader = []
                // const tableData = []
                // const filterVal = []
                // for (let i = 0; i < this.columns.length; i++) {
                //     const tagCode = this.columns[i].tag_code
                //     const name = this.columns[i].attrs.name
                //     tableHeader.push(name)
                //     filterVal.push(tagCode)
                // }
                // tableData.push(tableHeader)
                // const list = this.tableValue
                // for (let i = 0; i < list.length; i++) {
                //     const row = []
                //     for (let j = 0; j < filterVal.length; j++) {
                //         row.push(list[i][filterVal[j]])
                //     }
                //     tableData.push(row)
                // }
                // const wsName = 'Sheet1'
                // const wb = XLSX.utils.book_new()
                // const ws = XLSX.utils.aoa_to_sheet(tableData)
                // XLSX.utils.book_append_sheet(wb, ws, wsName)
                // XLSX.writeFile(wb, 'tableData.xlsx')
            },
            importData () {
                // const types = file.name.split('.')[1]
                // const fileType = ['xlsx', 'xlc', 'xlm', 'xls', 'xlt', 'xlw', 'csv'].some(item => item === types)
                // if (!fileType) {
                //     errorHandler(gettext('格式错误！请选择xlsx,xls,xlc,xlm,xlt,xlw或csv文件'))
                //     return
                // }
                // this.file2Xce(file).then(tabJson => {
                //     if (tabJson && tabJson.length > 0) {
                //         // 首先做一个name与tag_code的对应字典
                //         const nameToTagCode = {}
                //         for (let i = 0; i < this.columns.length; i++) {
                //             nameToTagCode[this.columns[i].attrs.name] = this.columns[i].tag_code
                //         }
                //         // 循环进行对比，如果发现与表头一致的name，就将其替换成tag_code
                //         const excelValue = tabJson[0]['sheet']
                //         for (let i = 0; i < excelValue.length; i++) {
                //             for (const key in excelValue[i]) {
                //                 const newKey = nameToTagCode[key]
                //                 excelValue[i][newKey] = excelValue[i][key]
                //                 delete excelValue[i][key]
                //             }
                //         }
                //         this._set_value(tabJson[0]['sheet'])
                //     }
                // })
            },
            rowEditClick (row) {
                this.editRow = row.index
            },
            rowDelClick (row) {
                this.colsData.splice(row.index, 1)
            },
            rowSaveClick (row, data) {
                this.colsData[row.index] = data
            },
            rowCancelClick (data) {
                this.editRow = ''
            }
        }
    }
</script>
<style lang="scss">
    .opt-btns {
        margin: 20px 0;
    }
</style>
