/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="task-param-wrapper">
        <RenderForm
            ref="renderForm"
            :option="renderOption"
            :config="renderConfig"
            :data="renderData"
            @dataChange="onInputChange">
        </RenderForm>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import atomFilter from '@/utils/atomFilter.js'
import tools from '@/utils/tools.js'
import { checkDataType } from '@/utils/checkDataType.js'
import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
export default {
    name: 'TaskParamEdit',
    components: {
        RenderForm
    },
    props: ['constants'],
    data () {
        return {
            variables: JSON.parse(JSON.stringify(this.constants)),
            renderOption: {
                showGroup: true,
                showLabel: true,
                showHook: false,
                showDesc: true
            },
            renderConfig: [],
            renderData: {
                hook: {},
                value: {},
                extend: {}
            }
        }
    },
    computed: {
        ...mapState({
            'atomFormConfig': state => state.atomForm.config
        })
    },
    watch: {
        constants (val) {
            this.variables = JSON.parse(JSON.stringify(val))
            this.getFormData()
        }
    },
    mounted () {
        this.getFormData()
    },
    methods: {
        ...mapActions('atomForm/', [
            'loadAtomConfig'
        ]),
        ...mapMutations ('atomForm/', [
            'setAtomConfig'
        ]),
        /**
         * 加载表单元素的原子配置文件
         */
        async getFormData () {
            let variableArray = []

            for (let cKey in this.variables) {
                const variable = JSON.parse(JSON.stringify(this.variables[cKey]))
                // 输入参数只展示显示类型全局变量
                if (variable.show_type === 'show') {
                    variableArray.push(variable)
                }
            }
            variableArray = variableArray.sort((a, b) => {
                return a.index - b.index
            })
            for (let variable of variableArray) {
                const sourceTag = variable.source_tag
                const key = variable.key
                if (sourceTag) { // 需要加载原子配置文件的表单项
                    const [ atomType, tagCode ] = sourceTag.split('.')
                    if (!this.atomFormConfig[atomType]) {
                        await this.loadAtomConfig({atomType})
                        this.setAtomConfig({atomType, configData: $.atoms[atomType]})
                    }
                    const atomConfig = this.atomFormConfig[atomType]
                    const currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                    currentFormConfig.variableKey = key
                    currentFormConfig.attrs.name = variable.name
                    this.renderConfig.push(currentFormConfig)
                } else { // 自定义变量且不需要加载原子配置文件的表单项
                    const currentFormConfig = {
                        tag_code: key,
                        type: variable.custom_type,
                        variableKey: key,
                        attrs: {
                            name: variable.name,
                            hookable: true
                        }
                    }
                    if ( // 自定义校验规则注册到表单的校验属性上
                        variable.custom_type === 'input' &&
                        variable.validation &&
                        checkDataType(variable.validation) === 'String'
                    ) {
                        const validation = {
                            type: 'regex',
                            args: variable.validation,
                            error_message: gettext('输入值不满足校验规则') + variable.validation
                        }
                        currentFormConfig.attrs.validation = [validation]
                    }
                    this.renderConfig.push(currentFormConfig)
                }
                this.renderData.hook[key] = false
                this.renderData.value[key] = JSON.parse(JSON.stringify(variable.value))
                this.renderData.extend[key] = {
                    name: variable.name,
                    desc: variable.desc
                }
            }
        },
        onInputChange (val, tagCode, variableKey) {
            let value = this.renderData.value[variableKey]
            if (checkDataType(value) === 'Object') {
                this.$set(value, tagCode, val)
            } else {
                this.$set(this.renderData.value, variableKey, val)
            }
        },
        validate () {
            return this.$refs.renderForm.validate()
        },
        getVariableData () {
            const variables = JSON.parse(JSON.stringify(this.constants))
            for (let key in variables) {
                const variable = variables[key]
                if (key in this.renderData.value) {
                    variable.value = this.renderData.value[key]
                }
            }
            return variables
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
    .task-param-wrapper {
        /deep/ .render-form {
            .group-name {
                margin-bottom: 20px;
                border-bottom: 2px solid $commonBorderColor;
                h3 {
                    display: inline-block;
                    margin: 0;
                    margin-bottom: -1px;
                    padding: 5px 14px;
                    font-size: 14px;
                    font-weight: normal;
                    color: $whiteDefault;
                    background: $greenDefault;
                    border-radius: 2px;
                }
            }
            .desc {
                position: absolute;
                right: 0;
                top: 10px;
                color: $yellowBg;
                font-size: 14px;
            }
            .form-item {
                margin-bottom: 20px;
            }
        }
    }
</style>

