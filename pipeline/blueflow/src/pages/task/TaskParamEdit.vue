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
    <div class="task-param-wrapper">
        <RenderForm
            ref="renderForm"
            v-if="!isConfigLoading"
            :scheme="renderConfig"
            :formOption="renderOption"
            v-model="renderData">
        </RenderForm>
        <NoData v-if="isNoData && !isConfigLoading"></NoData>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import atomFilter from '@/utils/atomFilter.js'
import tools from '@/utils/tools.js'
import { checkDataType } from '@/utils/checkDataType.js'
import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
import NoData from '@/components/common/base/NoData.vue'
export default {
    name: 'TaskParamEdit',
    components: {
        RenderForm,
        NoData
    },
    props: ['constants', 'editable'],
    data () {
        return {
            variables: tools.deepClone(this.constants),
            renderOption: {
                showGroup: true,
                showLabel: true,
                showHook: false,
                showDesc: true,
                formEdit: this.editable
            },
            renderConfig: [],
            metaConfig: {},
            renderData: {},
            isConfigLoading: true,
            isNoData: false
        }
    },
    computed: {
        ...mapState({
            'atomFormConfig': state => state.atomForm.config
        })
    },
    watch: {
        constants (val) {
            this.variables = tools.deepClone(val)
            this.getFormData()
        },
        editable (val) {
            this.$set(this.renderOption, 'editable', val)
        }
    },
    created () {
        this.getFormData()
    },
    methods: {
        ...mapActions('atomForm/', [
            'loadAtomConfig'
        ]),
        ...mapMutations ('atomForm/', [
            'setAtomConfig'
        ]),
        ...mapMutations('atomForm/', [
            'clearAtomForm'
        ]),
        /**
         * 加载表单元素的标准插件配置文件
         */
        async getFormData () {
            let variableArray = []
            this.renderConfig = []
            this.renderData = {}
            for (let cKey in this.variables) {
                const variable = tools.deepClone(this.variables[cKey])
                // 输入参数只展示显示类型全局变量
                if (variable.show_type === 'show') {
                    variableArray.push(variable)
                }
            }
            if (variableArray.length === 0) {
                this.isNoData = true
            } else {
                this.isNoData = false
            }
            variableArray = variableArray.sort((a, b) => {
                return a.index - b.index
            })
            for (let variable of variableArray) {
                const sourceTag = variable.source_tag
                const key = variable.key
                if (sourceTag) { // 需要加载标准插件配置文件的表单项
                    const [ atomType, tagCode ] = sourceTag.split('.')
                    if (!this.atomFormConfig[atomType]) {
                        this.isConfigLoading = true
                        await this.loadAtomConfig({atomType})
                        this.setAtomConfig({atomType, configData: $.atoms[atomType]})
                    }
                    const atomConfig = this.atomFormConfig[atomType]
                    var currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                    if (currentFormConfig) {
                        // 若该比变量是原型变量则进行转换操作
                        if (variable.is_meta || currentFormConfig.meta_transform) {
                            currentFormConfig = currentFormConfig.meta_transform(variable.meta || variable)
                            this.metaConfig[key] = tools.deepClone(variable)
                            if (!variable.meta) {
                                variable.value = currentFormConfig.attrs.value
                            }
                        }
                        currentFormConfig.tag_code = key
                        currentFormConfig.attrs.name = variable.name
                        currentFormConfig.attrs.desc = variable.desc
                        this.renderConfig.push(currentFormConfig)
                    }
                } else { // 自定义变量且不需要加载标准插件配置文件的表单项
                    const currentFormConfig = {
                        tag_code: key,
                        type: variable.custom_type,
                        variableKey: key,
                        attrs: {
                            name: variable.name,
                            hookable: true
                        }
                    }
                    if ( // 自定义正则校验注册到表单的校验属性上
                        variable.custom_type === 'input' &&
                        variable.validation &&
                        checkDataType(variable.validation) === 'String'
                    ) {
                        const validation = {
                            type: 'regex',
                            args: variable.validation,
                            error_message: gettext('输入值不满足正则校验') + variable.validation
                        }
                        currentFormConfig.attrs.desc = variable.desc
                        currentFormConfig.attrs.validation = [validation]
                    }
                    this.renderConfig.push(currentFormConfig)
                }
                this.renderData[key] = tools.deepClone(variable.value)
            }
            this.$nextTick(() => {
                this.isConfigLoading = false
                this.$emit('onChangeConfigLoading', false)
            })
        },
        validate () {
            return this.$refs.renderForm.validate()
        },
        getVariableData () {
            const variables = tools.deepClone(this.constants)
            for (let key in variables) {
                const variable = variables[key]
                if (key in this.renderData) {
                    variable.value = this.renderData[key]
                    variable.meta = this.metaConfig[key]
                } else if (variable.is_meta) {
                    const sourceTag = variable.source_tag
                    const [ atomType, tagCode ] = sourceTag.split('.')
                    if (!this.atomFormConfig[atomType]) {
                        this.loadAtomConfig({atomType})
                        this.setAtomConfig({atomType, configData: $.atoms[atomType]})
                    }
                    const atomConfig = this.atomFormConfig[atomType]
                    var currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                    currentFormConfig = currentFormConfig.meta_transform(variable.meta || variable)
                    variable.meta = tools.deepClone(variable)
                    variable.value = currentFormConfig.attrs.value
                }
            }
            return variables
        }
    },
    beforeDestroy () {
        this.clearAtomForm()
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
    .task-param-wrapper {
        /deep/ .render-form {
            .rf-group-name {
                margin-bottom: 12px;
                h3 {
                    display: inline-block;
                    margin: 0;
                    margin-bottom: -1px;
                    padding: 5px 14px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #313238;
                }
                &:before {
                    content: '';
                    display: inline-block;
                    position: relative;
                    top: 4px;
                    width: 2px;
                    height: 20px;
                    background: #A3C5FD;
                }
            }
            .rf-group-desc {
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

