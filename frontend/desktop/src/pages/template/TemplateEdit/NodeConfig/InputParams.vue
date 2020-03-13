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
    <div class="input-params">
        <render-form
            ref="renderForm"
            v-model="formData"
            :scheme="scheme"
            :form-option="option"
            @change="onInputsChange"
            @onHookChange="onInputHookChange">
        </render-form>
        <reuse-var-dialog
            :reuse-variable="reuseVariable"
            :reuseable-var-list="reuseableVarList">
        </reuse-var-dialog>
    </div>
</template>
<script>
    import tools from '@/utils/tools.js'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import ReuseVarDialog from './ReuseVarDialog.vue'
    import { mapMutations } from 'vuex'
    export default {
        name: 'InputParams',
        components: {
            RenderForm,
            ReuseVarDialog
        },
        props: {
            scheme: {
                type: Array,
                default () {
                    return []
                }
            },
            nodeConfig: {
                type: Object,
                default () {
                    return {}
                }
            },
            value: {
                type: Object,
                default () {
                    return {}
                }
            },
            isSubflow: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                reuseVariable: {},
                reuseableVarList: [],
                formData: tools.deepClone(this.value),
                option: {
                    showGroup: false,
                    showHook: true,
                    showLabel: true,
                    showVarList: true
                }
            }
        },
        watch: {
            value (val) {
                this.formData = tools.deepClone(val)
            }
        },
        created () {
            this.onInputsChange = tools.debounce(this.inputsChange, 800)
        },
        methods: {
            ...mapMutations('template/', [
                'setNodeInputData'
            ]),
            // 输入参数值改变
            inputsChange (val) {
                this.setNodeInputData({
                    id: this.nodeConfig.id,
                    type: this.nodeConfig.type,
                    setVals: val
                })
            },
            // 输入勾选，取消勾选
            onInputHookChange (code, val) {
                const VAR_KEY_REG = /^\$\{(\w+)\}$/
                const variable = {
                    name: '',
                    key: '',
                    source_info: {},
                    custom_type: '',
                    value: '',
                    validation: '',
                    version: ''
                }
                const formScheme = this.scheme.find(m => m.tag_code === code)
                const correctKey = VAR_KEY_REG.test(code) ? code : '${' + code + '}'
                variable.name = formScheme.name.replace(/\s/g, '')
                if (this.isSubflow) {
                    const constants = this.nodeConfig.constants
                    variable.key = correctKey
                    variable.source_tag = constants.source_tag
                    variable.source_info = { [this.nodeConfig.id]: [correctKey] }
                    variable.custom_type = constants.custom_type
                    variable.value = tools.deepClone(this.value[code])
                    if (formScheme.type !== 'combine') {
                        variable.validation = constants.validation
                    }
                } else {
                    const component = this.nodeConfig.component
                    variable.key = code
                    variable.source_tag = `${component.code}.${code}`
                    variable.source_info = { [this.nodeConfig.id]: [code] }
                    variable.custom_type = ''
                    variable.value = tools.deepClone(this.value[code])
                    variable.version = component.version
                }
                
                console.log(code, val, 'lifdslss')
            }
        }
    }
</script>
