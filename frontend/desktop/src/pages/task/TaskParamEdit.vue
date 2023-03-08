/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
            :key="randomKey"
            :scheme="renderConfig"
            :constants="variables"
            :form-option="renderOption"
            v-model="renderData">
        </RenderForm>
        <NoData v-if="isNoData && !isConfigLoading" :message="$t('暂无参数')"></NoData>
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
        props: {
            constants: {
                type: Object,
                default () {
                    return {}
                }
            },
            isUsedTipShow: {
                type: Boolean,
                default: true
            },
            preMakoDisabled: {
                type: Boolean,
                default: false
            },
            editable: {
                type: Boolean,
                default: true
            },
            showRequired: {
                type: Boolean,
                default: true
            },
            unUsedConstants: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                randomKey: new Date().getTime(),
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
                initalRenderData: {},
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
            }),
            reuseTaskId () {
                return this.$route.query.task_id
            }
        },
        watch: {
            constants (val) {
                this.variables = tools.deepClone(val)
                this.getFormData()
            },
            editable (val) {
                this.$set(this.renderOption, 'formEdit', val)
                this.randomKey = new Date().getTime()
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
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            ...mapMutations('atomForm/', [
                'clearAtomForm'
            ]),
            ...mapActions('task/', [
                'getTaskInstanceData'
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

                this.isNoData = variableArray.length === 0

                variableArray = variableArray.sort((a, b) => {
                    return a.index - b.index
                })

                if (variableArray.length > 0) {
                    this.isConfigLoading = true
                    this.$emit('onChangeConfigLoading', true)
                }

                // 任务参数重用
                let pipelineTree = null
                if (this.reuseTaskId) {
                    const instanceData = await this.getTaskInstanceData(this.reuseTaskId)
                    pipelineTree = JSON.parse(instanceData.pipeline_tree)
                }

                for (const variable of variableArray) {
                    const { key } = variable
                    const { plugin_code } = variable
                    const { name, atom, tagCode, classify } = atomFilter.getVariableArgs(variable)
                    // custom_type 可以判断是手动新建节点还是组件勾选
                    const version = variable.version || 'legacy'
                    let atomConfig
                    if (atomFilter.isConfigExists(atom, version, this.atomFormConfig)) { // 已加载过相同类型且相同版本的插件配置项，直接取缓存
                        atomConfig = this.atomFormConfig[atom][version]
                    } else {
                        if (plugin_code) {
                            atomConfig = await this.getThirdPartyAtomConfig(plugin_code, version)
                        } else {
                            await this.loadAtomConfig({ name, atom, classify, version, project_id: this.project_id })
                            atomConfig = tools.deepClone(this.atomFormConfig[atom][version])
                        }
                    }

                    const isPreRenderMako = this.preMakoDisabled && variable.pre_render_mako // 变量预渲染
                    /* 暂不进行变量是否被使用判断 */
                    // const isUsed = this.unUsedConstants.length && !this.unUsedConstants.includes(variable.key) // 变量是否被使用
                    const isUsed = false
                    atomConfig.forEach(item => {
                        if (!item.attrs) {
                            item.attrs = {}
                        }
                        item.attrs['disabled'] = isPreRenderMako || isUsed
                        if (isPreRenderMako) {
                            item.attrs['pre_mako_tip'] = i18n.t('设为「常量」的参数中途不允许修改')
                        } else if (isUsed) {
                            // item.attrs['used_tip'] = this.isUsedTipShow ? i18n.t('参数已被使用，不可修改') : ''
                        } else {
                            delete item.attrs['pre_mako_tip']
                            delete item.attrs['used_tip']
                        }
                        if (item.attrs.children) { // 子组件是否禁用
                            this.setAtomDisable(item.attrs.children, isPreRenderMako || isUsed)
                        }
                    })
                    let currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                    // 任务参数重用(元变量单独处理)
                    if (pipelineTree && !variable.is_meta) {
                        const taskVariable = pipelineTree.constants[key]
                        if (taskVariable && taskVariable.custom_type === variable.custom_type) { // 重用
                            if (Object.prototype.toString.call(variable.value) === '[Object Object]') {
                                const match = Object.keys(variable.value).every(key => key in taskVariable.value)
                                if (match) {
                                    variable.value = taskVariable.value
                                }
                            } else {
                                variable.value = taskVariable.value
                            }
                        } else if (currentFormConfig) { // 不重用
                            currentFormConfig.attrs.notReuse = true
                        }
                    }

                    if (currentFormConfig) {
                        // 若该变量是元变量则进行转换操作
                        if (variable.is_meta || currentFormConfig.meta_transform) {
                            currentFormConfig = currentFormConfig.meta_transform(variable.meta || variable)
                            // 执行过的元变量，attr配置需要单独处理
                            if (this.preMakoDisabled && variable.pre_render_mako) {
                                currentFormConfig.attrs['disabled'] = true
                                currentFormConfig.attrs['pre_mako_tip'] = i18n.t('设为「常量」的参数中途不允许修改')
                            }
                            // else if (this.unUsedConstants.length && !this.unUsedConstants.includes(variable.key)) {
                            //     currentFormConfig.attrs['disabled'] = true
                            //     currentFormConfig.attrs['used_tip'] = this.isUsedTipShow ? i18n.t('参数已被使用，不可修改') : ''
                            // }
                            this.metaConfig[key] = tools.deepClone(variable)
                            // 任务参数重用(元变量)
                            const { remote_url } = currentFormConfig.attrs
                            if (!remote_url && pipelineTree && pipelineTree.constants[key]) { // 重用(远程数据源不进行重用)
                                const { value, meta, custom_type } = pipelineTree.constants[key]
                                const listType = custom_type === 'datatable' ? 'columns' : 'items'
                                const match = meta && meta.value[`${listType}_text`].replace(/ /g, '') === JSON.stringify(currentFormConfig.attrs[listType])
                                if (match) {
                                    currentFormConfig.attrs.value = value
                                }
                            } else if (pipelineTree) { // 不重用
                                currentFormConfig.attrs.notReuse = true
                            }
                            if (!variable.meta) {
                                variable.value = currentFormConfig.attrs.value
                            }
                        }
                        currentFormConfig.tag_code = key
                        currentFormConfig.name = variable.name // 变量名称，全局变量编辑时填写的名称，和表单配置项 label 名称不同
                        currentFormConfig.attrs.desc = variable.desc

                        // 参数填写时为保证每个表单 tag_code 唯一，原表单 tag_code 会被替换为变量 key，导致事件监听不生效
                        if (currentFormConfig.hasOwnProperty('events')) {
                            currentFormConfig.events.forEach(e => {
                                if (e.source === tagCode) {
                                    e.source = '${' + e.source + '}'
                                }
                            })
                        }

                        if (
                            ['input', 'textarea'].includes(variable.custom_type)
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
                this.initalRenderData = this.renderData
                this.$nextTick(() => {
                    this.isConfigLoading = false
                    this.$emit('onChangeConfigLoading', false)
                })
            },
            setAtomDisable (atomList, disabled = true) {
                atomList.forEach(item => {
                    if (!item.attrs) {
                        item.attrs = {}
                    }
                    item.attrs['disabled'] = disabled
                    if (item.attrs.children) {
                        this.setAtomDisable(item.attrs.children)
                    }
                })
            },
            async getThirdPartyAtomConfig (code, version) {
                try {
                    const resp = await this.loadPluginServiceDetail({
                        plugin_code: code,
                        plugin_version: version,
                        with_app_detail: true
                    })
                    if (!resp.result) return
                    // 设置host
                    const { origin } = window.location
                    const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${code}/`
                    $.context.bk_plugin_api_host[code] = hostUrl
                    // 输入参数
                    $.atoms[code] = {}
                    const renderFrom = resp.data.forms.renderform
                    /* eslint-disable-next-line */
                    eval(renderFrom)
                    const atomConfig = $.atoms[code]
                    return atomConfig
                } catch (error) {
                    console.warn(error)
                }
            },
            validate () {
                return this.isConfigLoading ? false : this.$refs.renderForm.validate()
            },
            judgeDataEqual () {
                const formvalid = this.validate()
                if (formvalid) {
                    return tools.isDataEqual(this.initalRenderData, this.renderData)
                } else {
                    return false
                }
            },
            getChangeParams () {
                return Object.keys(this.initalRenderData).reduce((acc, key) => {
                    if (!(key in this.renderData) || !tools.isDataEqual(this.initalRenderData[key], this.renderData[key])) {
                        acc.push(key)
                    }
                    return acc
                }, [])
            },
            async getVariableData () {
                // renderform表单校验
                const formValid = this.validate()
                if (!formValid) {
                    return
                }
                const variables = tools.deepClone(this.constants)
                for (const key in variables) {
                    const variable = variables[key]
                    if (variable.show_type === 'hide') {
                        if (variable.is_meta) {
                            const { plugin_code } = variable
                            const { name, atom, tagCode, classify } = atomFilter.getVariableArgs(variable)
                            // custom_type 可以判断是手动新建节点还是组件勾选
                            const version = variable.version || 'legacy'
                            let atomConfig
                            if (atomFilter.isConfigExists(atom, version, this.atomFormConfig)) {
                                atomConfig = this.atomFormConfig[atom][version]
                            } else {
                                if (plugin_code) {
                                    atomConfig = await this.getThirdPartyAtomConfig(plugin_code, version)
                                } else {
                                    await this.loadAtomConfig({ name, atom, classify, version, project_id: this.project_id })
                                    atomConfig = this.atomFormConfig[atom][version]
                                }
                            }
                            let currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                            currentFormConfig = currentFormConfig.meta_transform(variable.meta || variable)
                            if (!('meta' in variable)) { // 元变量不存在meta字段
                                variable.meta = tools.deepClone(variable)
                            }
                            variable.value = currentFormConfig.attrs.value
                        }
                    } else {
                        variable.value = this.renderData[key]
                        if (variable.is_meta && !('meta' in variable)) { // 元变量不存在meta字段
                            variable.meta = this.metaConfig[key]
                        }
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
