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
    <div class="output-params">
        <bk-table :data="list" :border="true">
            <bk-table-column :label="$t('名称')" :width="180" align="center" prop="name"></bk-table-column>
            <bk-table-column :label="$t('说明')" align="center">
                <template slot-scope="props">
                    <span
                        v-if="props.row.scheme && (description in props.row.scheme)"
                        :title="props.row.scheme.description">
                        {{ props.row.scheme.description }}
                    </span>
                    <span v-else>--</span>
                </template>
            </bk-table-column>
            <bk-table-column label="KEY" :width="180" align="center" prop="key"></bk-table-column>
            <bk-table-column :label="$t('引用')" :width="100" align="center">
                <template slot-scope="props">
                    <bk-checkbox
                        v-model="props.row.hooked"
                        @change="onHookChange(props, $event)">
                    </bk-checkbox>
                </template>
            </bk-table-column>
        </bk-table>
        <bk-dialog
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :render-directive="'if'"
            :header-position="'left'"
            :title="$t('新建变量')"
            :auto-close="false"
            :value="isShow"
            width="600"
            @confirm="onConfirm"
            @cancel="onCancel">
            <div class="variable-dialog">
                <bk-form
                    ref="form"
                    :model="formData"
                    :rules="rules">
                    <template>
                        <bk-form-item :label="$t('变量名称')" property="name" :required="true">
                            <bk-input name="variableName" v-model="formData.name"></bk-input>
                        </bk-form-item>
                        <bk-form-item :label="$t('变量KEY')" property="key" :required="true">
                            <bk-input name="variableKey" v-model="formData.key"></bk-input>
                        </bk-form-item>
                    </template>
                </bk-form>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import { mapState, mapMutations } from 'vuex'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'
    export default {
        name: 'OutputParams',
        props: {
            params: Array,
            isSubflow: Boolean,
            nodeId: String,
            version: String // 标准插件版本或子流程版本
        },
        data () {
            const list = this.getOutputsList(this.params)
            const $this = this
            return {
                list,
                isShow: false,
                formData: {},
                selectIndex: '',
                rules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                            message: i18n.t('变量名称长度不能超过') + STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('变量名称不能包含') + INVALID_NAME_CHAR + i18n.t('非法字符'),
                            trigger: 'blur'
                        }
                    ],
                    key: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH,
                            message: i18n.t('变量KEY值长度不能超过') + STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            // 合法变量key正则，eg:${fsdf_f32sd},fsdf_f32sd
                            regex: /(^\${[a-zA-Z_]\w*}$)|(^[a-zA-Z_]\w*$)/,
                            message: i18n.t('变量KEY由英文字母、数字、下划线组成，且不能以数字开头'),
                            trigger: 'blur'
                        },
                        {
                            validator (val) {
                                const value = /^\$\{\w+\}$/.test(val) ? val : `\${${val}}`
                                if (value in $this.constants) {
                                    return false
                                }
                                return true
                            },
                            message: i18n.t('变量KEY值已存在'),
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        computed: {
            ...mapState({
                constants: state => state.template.constants
            })
        },
        watch: {
            params (val) {
                this.list = this.getOutputsList(val)
            }
        },
        methods: {
            ...mapMutations('template/', [
                'addVariable',
                'deleteVariable'
            ]),
            getOutputsList () {
                const list = []
                const constants = this.$store.state.template.constants
                const varKeys = Object.keys(constants)
                this.params.forEach(param => {
                    let key = param.key
                    const isHooked = varKeys.some(item => {
                        const varItem = constants[item]
                        if (varItem.source_type === 'component_outputs') {
                            const sourceInfo = varItem.source_info[this.nodeId]
                            if (sourceInfo && sourceInfo.includes(param.key)) {
                                key = item
                                return true
                            }
                        }
                    })
                    list.push({
                        key,
                        name: param.name,
                        version: param.version,
                        hooked: isHooked
                    })
                })
                return list
            },
            /**
             * 输出参数勾选切换
             */
            onHookChange (props, val) {
                const index = props.$index
                if (val) {
                    this.isShow = true
                    this.formData = tools.deepClone(props.row)
                    this.selectIndex = index
                } else {
                    this.deleteVariable(props.row.key)
                    this.list[index].key = this.params[index].key
                    this.list[index].name = this.params[index].name
                }
            },
            onConfirm ($event) {
                this.$refs.form.validate().then(result => {
                    if (result) {
                        const { name, key } = this.formData
                        this.isShow = false
                        console.log(this.params)
                        const version = this.isSubflow ? this.list[this.selectIndex].version : this.version
                        let setKey = ''
                        if ((/^\$\{((?!\{).)*\}$/).test(key)) {
                            this.list[this.selectIndex].key = key
                            setKey = key
                        } else {
                            this.list[this.selectIndex].key = `\$\{${key}\}`
                            setKey = `\$\{${key}\}`
                        }
                        const config = {
                            name: name,
                            key: setKey,
                            source_info: {
                                [this.nodeId]: [this.params[this.selectIndex].key]
                            },
                            version
                        }
                        this.createVariable(config)
                    }
                })
            },
            onCancel () {
                this.isShow = false
                this.list[this.selectIndex].hooked = false
            },
            createVariable (variableOpts) {
                const len = Object.keys(this.constants).length
                const defaultOpts = {
                    name: '',
                    key: '',
                    desc: '',
                    custom_type: '',
                    source_info: {},
                    source_tag: '',
                    value: '',
                    show_type: 'hide',
                    source_type: 'component_outputs',
                    validation: '',
                    index: len,
                    version: ''
                }
                const variable = Object.assign({}, defaultOpts, variableOpts)
                this.addVariable(variable)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .variable-dialog {
        padding: 30px;
        .new-var-notice {
            margin-bottom: 10px;
            font-size: 14px;
            color: #ea3636;
        }
        .bk-form:not(.bk-form-vertical) {
            /deep/ .bk-form-content {
                margin-right: 30px;
            }
        }
    }
</style>
