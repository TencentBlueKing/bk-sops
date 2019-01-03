/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-form tag-datatable" v-show="showForm">
        <bk-button v-if="add_btn && editable" class="add-column" type="default" @click="add_row">{{ i18n.add_text }}</bk-button>
        <el-table
            style="width: 100%"
            ref="datatable"
            :data="tempValue"
            :empty-text="empty_text"
            v-loading="loading"
            border>
            <el-table-column
                v-for="(item, cIndex) in columns"
                v-if="'attrs' in item && 'hidden' in item.attrs? !item.attrs.hidden : true"
                :key="item.tag_code"
                :index="cIndex"
                :prop="item.tag_code"
                :label="'attrs' in item && 'name' in item.attrs ? item.attrs.name : ''"
                :width="'attrs' in item && 'width' in item.attrs ? item.attrs.width : ''"
                align="center">
                <template slot-scope="scope">
                    <div v-if="scope.$index === editRowNumber">
                        <component
                            v-if="item.type !== 'text'"
                            :ref="`row_${scope.$index}_${cIndex}_${item.tag_code}`"
                            :is="'tag-' + item.type"
                            :initialTag_code= "item.tag_code"
                            :initialValue="scope.row[item.tag_code]"
                            :initialType="item.type"
                            :initialEditable="'attrs' in item && 'editable' in item.attrs ? item.attrs.editable : false"
                            :initialValidation="'attrs' in item && 'validation' in item.attrs ? item.attrs.validation : []"
                            @change="columnChange">
                        </component>

                        <span v-else>{{scope.row[item.tag_code]}}</span>
                    </div>
                    <span v-else>
                        {{ scope.row[item.tag_code]}}
                    </span>
                </template>
            </el-table-column>
            <el-table-column v-if="editable"
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
        <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { checkDataType } from '@/utils/checkDataType.js'
import { getAtomFormMixins, getInitialProps } from './atomFormMixins.js'
import TagRadio from './TagRadio.vue'
import Tagcheckbox from './TagCheckbox.vue'
import TagInput from './TagInput.vue'
import TagSelect from './TagSelect.vue'
import TagTextarea from './TagTextarea.vue'
import TagDatetime from './TagDatetime.vue'
import TagDatatable from './TagDatatable.vue'
import TagUpload from './TagUpload.vue'
import TagTree from './TagTree.vue'
const datatableAttrs = {
    columns: {
        type: Array,
        required: false,
        default () {
            return []
        },
        desc: "initial data, which should be a array like [{tag_code: '', title: '', type: '', editable: true}, {}]"
    },
    editable: {
        type: Boolean,
        required: false,
        default () {
            return true
        },
        desc: "show edit and delete button or not"
    },
    value: {
        type: Array,
        required: false,
        default () {
            return []
        }
    },
    add_btn: {
        type: Boolean,
        required: false,
        default () {
            return false
        },
        desc: "show add button or not"
    },
    empty_text: {
        type: String,
        required: false,
        default () {
            return gettext("无数据")
        },
        desc: "tips when data is empty"
    },
    remote_url: {
        type: String,
        required: false,
        default () {
            return ""
        },
        desc: "remote url when remote is true"
    },
    remote_data_init: {
        type: Function,
        required: false,
        default () {
            return function (data) {
                return data
            }
        },
        desc: "how to process data after getting remote data"
    }
}
export default {
    name: 'TagDatatable',
    mixins: [getAtomFormMixins(datatableAttrs)],
    props: getInitialProps(datatableAttrs),
    data () {
        return {
            i18n: {
                save_text: gettext("保存"),
                cancel_text: gettext("取消"),
                edit_text: gettext("编辑"),
                operate_text: gettext("操作"),
                delete_text: gettext("删除"),
                add_text: gettext("添加")
            },
            isAddStatus: false,
            originData: {},
            editData: {},
            editRowNumber: undefined,
            tempValue: JSON.parse(JSON.stringify(this.initialValue)),
            loading: false
        }
    },
    watch: {
        initialValue (value) {
            this.tempValue = JSON.parse(JSON.stringify(value))
        },
        remote_url (value) {
            this.remoteMethod()
        }
    },
    mounted () {
        this.remoteMethod()
    },
    methods: {
        validateSubCom (index) {
            let isValid = true
            const startNameReg = `^row_${index}`
            for (let ref in this.$refs) {
                let singleItemValid = true
                if (new RegExp(startNameReg).test(ref)) {
                    const component = this.$refs[ref]
                    if (checkDataType(component) === 'Undefined') {
                        delete this.$refs[ref]
                    } else if (checkDataType(component) === 'Array') {
                        // hack element 在有固定列的情况下复制表格导致的冲突
                        let item = component[0]
                        singleItemValid = !item.validate || item.validate()
                    } else {
                        singleItemValid = !component.validate || component.validate()
                    }
                    if (isValid) {
                        isValid = singleItemValid
                    }
                }
            }
            return isValid
        },
        onEdit: function (index, row) {
            this.editRowNumber = index
            this.columns.forEach(item => {
                this.originData[item.tag_code] = this.tempValue[index][item.tag_code]
            })
            this.editData = Object.assign({}, this.originData)
        },
        onDelete: function (index, row) {
            this.value.splice(index, 1)
            this.tempValue.splice(index, 1)
        },
        onSave: function (index, row) {
            const valueValid = this.validateSubCom(index)
            if (!valueValid) return
            const editData = Object.assign({}, this.editData)
            this.editRowNumber = undefined
            this.isAddStatus = false
            this.value.splice(index, 1, editData)
            this.tempValue.splice(index, 1, editData)
        },
        onCancel: function (index, row) {
            this.editRowNumber = undefined
            if (this.isAddStatus) {
                this.tempValue.splice(index, 1)
                this.isAddStatus = false
            }
        },
        set_loading: function (loading) {
            this.loading = loading
        },
        add_row (){
            this.isAddStatus = true
            this.columns.forEach((item, index) => {
                this.editData[item.tag_code] = item.default || ''
            })
            this.editRowNumber = this.tempValue.length
            this.tempValue.push(this.editData)
        },
        columnChange (val, tagCode) {
            this.editData[tagCode] = val
        },
        remoteMethod () {
            var remote_url = typeof this.remote_url === 'function' ? this.remote_url() : this.remote_url
            if (remote_url) {
                this.loading = true
                var $this = this

                $.ajax({
                    url: remote_url,
                    method: "GET",
                    success: res => {
                        var data = $this.remote_data_init(res)
                        for (let i in data) {
                            data[i].width = Math.max(150, data[i].attrs.name.length * 20) + 'px'
                        }
                        $this.columns = data
                        $this.loading = false
                    },
                    error: () => {
                        $this.empty_text = gettext("请求表头数据失败，使用预置表头")
                        $this.loading = false
                    }
                })
            }
        }
    },
    components: {
        'tag-radio': TagRadio,
        'tag-checkbox': Tagcheckbox,
        'tag-input': TagInput,
        'tag-select': TagSelect,
        'tag-textarea': TagTextarea,
        'tag-datetime': TagDatetime,
        'tag-datatable': TagDatatable,
        'tag-upload': TagUpload,
        'tag-tree': TagTree
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.tag-datatable {
    .el-table .tag-form.tag-input {
        margin-right: 0;
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
</style>
