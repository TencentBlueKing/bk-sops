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
    <div class="task-param-wrapper">
        <RenderForm
            ref="renderForm"
            v-if="!isConfigLoading"
            :scheme="renderConfig"
            :form-option="renderOption"
            v-model="renderData">
        </RenderForm>
        <NoData v-if="isNoData && !isConfigLoading"></NoData>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import atomFilter from '@/utils/atomFilter.js'
    import tools from '@/utils/tools.js'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'TaskParamEdit',
        components: {
            RenderForm,
            NoData
        },
        props: ['constants', 'editable', 'showRequired'],
        data () {
            return {
                variables: tools.deepClone(this.constants),
                renderOption: {
                    showRequired: true,
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
                atomFormConfig: state => state.atomForm.config
            }),
            ...mapState('project', {
                project_id: state => state.project_id
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
            if (this.showRequired === false) {
                this.renderOption.showRequired = this.showRequired
            }
        },
        beforeDestroy () {
            this.clearAtomForm()
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig'
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
                for (const cKey in this.variables) {
                    const variable = tools.deepClone(this.variables[cKey])
                    // 输入参数只展示显示类型全局变量
                    if (variable.show_type === 'show') {
                        variableArray.push(variable)
                    }
                }

                this.isNoData = !variableArray.length

                variableArray = variableArray.sort((a, b) => {
                    return a.index - b.index
                })

                if (variableArray.length > 0) {
                    this.isConfigLoading = true
                    this.$emit('onChangeConfigLoading', true)
                }

                for (const variable of variableArray) {
                    const { key } = variable
                    const { name, atom, tagCode, classify } = atomFilter.getVariableArgs(variable)
                    // custom_type 可以判断是手动新建节点还是组件勾选
                    const version = variable.version || 'legacy'
                    if (!atomFilter.isConfigExists(atom, version, this.atomFormConfig)) {
                        await this.loadAtomConfig({ name, atom, classify, version, project_id: this.project_id })
                    }
                    const atomConfig = this.atomFormConfig[atom][version]
                    let currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))

                    if (currentFormConfig) {
                        // 若该变量是元变量则进行转换操作
                        if (variable.is_meta || currentFormConfig.meta_transform) {
                            currentFormConfig = currentFormConfig.meta_transform(variable.meta || variable)
                            this.metaConfig[key] = tools.deepClone(variable)
                            if (!variable.meta) {
                                variable.value = currentFormConfig.attrs.value
                            }
                        }
                        currentFormConfig.tag_code = key
                        currentFormConfig.name = variable.name // 变量名称，全局变量编辑时填写的名称，和表单配置项 label 名称不同
                        currentFormConfig.attrs.desc = variable.desc
                        if (
                            variable.custom_type === 'input'
                            && variable.validation !== ''
                        ) {
                            currentFormConfig.attrs.validation.push({
                                type: 'regex',
                                args: variable.validation,
                                error_message: i18n.t('参数值不符合正则规则：') + variable.validation
                            })
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
                return this.isConfigLoading ? false : this.$refs.renderForm.validate()
            },
            async getVariableData () {
                const variables = tools.deepClone(this.constants)
                for (const key in variables) {
                    const variable = variables[key]
                    if (variable.show_type === 'hide') {
                        if (variable.is_meta) {
                            const { name, atom, tagCode, classify } = atomFilter.getVariableArgs(variable)
                            // custom_type 可以判断是手动新建节点还是组件勾选
                            const version = variable.version || 'legacy'
                            if (!atomFilter.isConfigExists(atom, version, this.atomFormConfig)) {
                                await this.loadAtomConfig({ name, atom, classify, version })
                            }
                            const atomConfig = this.atomFormConfig[atom][version]
                            let currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                            currentFormConfig = currentFormConfig.meta_transform(variable.meta || variable)
                            variable.meta = tools.deepClone(variable) // JSON.stringify 循环引用的问题，需要深拷贝一下
                            variable.value = currentFormConfig.attrs.value
                        }
                    } else {
                        variable.value = this.renderData[key]
                        variable.meta = this.metaConfig[key]
                    }
                }
                return Promise.resolve(variables)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
    .task-param-wrapper {
        /deep/ .render-form {
            .form-item {
                margin-bottom: 20px;
            }
        }
    }
</style>
