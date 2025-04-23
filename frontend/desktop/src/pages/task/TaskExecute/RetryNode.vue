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
    <div class="retry-node-container" v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 100 }">
        <div class="edit-wrapper">
            <RenderForm
                ref="renderForm"
                v-if="!isEmptyParams && !loading"
                :scheme="renderConfig"
                :form-option="renderOption"
                v-model="renderData">
            </RenderForm>
            <NoData v-else></NoData>
        </div>
        <div class="action-wrapper">
            <bk-button
                theme="primary"
                class="confirm-btn"
                :loading="retrying"
                data-test-id="taskExcute_form_configRetryBtn"
                @click="onRetryTask">
                {{ $t('确定') }}
            </bk-button>
            <bk-button
                theme="default"
                data-test-id="taskExcute_form_cancelBtn"
                @click="onCancelRetry">
                {{ $t('取消') }}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import atomFilter from '@/utils/atomFilter.js'
    export default {
        name: 'RetryNode',
        components: {
            RenderForm,
            NoData
        },
        props: ['nodeDetailConfig', 'engineVer', 'nodeInputs', 'retrying', 'nodeInfo'],
        data () {
            return {
                loading: false,
                bkMessageInstance: null,
                renderOption: {
                    showGroup: false,
                    showLabel: true,
                    showHook: false
                },
                renderConfig: [],
                renderData: {},
                initalRenderData: {}
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config
            }),
            ...mapState('project', {
                project_id: state => state.project_id
            }),
            isEmptyParams () {
                return this.renderConfig.length === 0
            },
            componentValue () {
                const { componentData, component_code } = this.nodeDetailConfig
                if (component_code === 'subprocess_plugin') {
                    return componentData.subprocess.value
                }
                return {}
            }
        },
        watch: {
            nodeInputs: {
                handler (value) {
                    this.initalRenderData = tools.deepClone(value)
                    this.renderData = tools.deepClone(value)
                },
                immediate: true
            }
        },
        mounted () {
            $.context.exec_env = 'NODE_RETRY'
            const { version, component_code } = this.nodeDetailConfig
            if (component_code) {
                this.getNodeConfig(component_code, version)
            }
        },
        beforeDestroy () {
            $.context.exec_env = ''
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            async getNodeConfig (type, version) {
                if (atomFilter.isConfigExists(type, version, this.atomFormConfig)) {
                    this.renderConfig = this.atomFormConfig[type][version]
                } else {
                    try {
                        this.loading = true
                        // 第三方插件节点拼接输出参数
                        if (this.nodeDetailConfig.component_code === 'remote_plugin') {
                            const { inputs } = this.nodeInfo.data
                            const pluginVersion = inputs && inputs.plugin_version
                            const pluginCode = inputs && inputs.plugin_code
                            const resp = await this.loadPluginServiceDetail({
                                plugin_code: pluginCode,
                                plugin_version: pluginVersion,
                                with_app_detail: true
                            })
                            if (!resp.result) return

                            // 设置host
                            const { origin } = window.location
                            const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${pluginCode}/`
                            $.context.bk_plugin_api_host[pluginCode] = hostUrl
                            // 输入参数
                            const renderFrom = resp.data.forms.renderform
                            /* eslint-disable-next-line */
                            eval(renderFrom)
                            const config = $.atoms[pluginCode]
                            this.renderConfig = config || []
                        } else if (type === 'subprocess_plugin') {
                            const { constants } = this.componentValue.pipeline
                            this.renderConfig = await this.getSubflowInputsConfig(constants)
                        } else {
                            await this.loadAtomConfig({ atom: type, version, project_id: this.project_id })
                            this.renderConfig = this.atomFormConfig[type][version]
                        }
                    } catch (e) {
                        console.log(e)
                    } finally {
                        this.loading = false
                    }
                }
            },
            /**
             * 加载子流程输入参数表单配置项
             * 遍历每个非隐藏的全局变量，由 source_tag、coustom_type 字段确定需要加载的标准插件
             * 同时根据 source_tag 信息获取全局变量对应标准插件的某一个表单配置项
             *
             * @return {Array} 每个非隐藏全局变量对应表单配置项组成的数组
             */
            async getSubflowInputsConfig (subflowForms) {
                const inputs = []
                const variables = Object.keys(subflowForms)
                    .map(key => subflowForms[key])
                    .filter(item => item.show_type === 'show')
                    .sort((a, b) => a.index - b.index)

                await Promise.all(variables.map(async (variable) => {
                    const { key } = variable
                    const { name, atom, tagCode, classify } = atomFilter.getVariableArgs(variable)
                    const version = variable.version || 'legacy'
                    const isThird = Boolean(variable.plugin_code)
                    const atomConfig = await this.getAtomConfig({ plugin: atom, version, classify, name, isThird })
                    let formItemConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                    if (variable.is_meta || formItemConfig.meta_transform) {
                        formItemConfig = formItemConfig.meta_transform(variable.meta || variable)
                        if (!variable.meta) {
                            variable.meta = tools.deepClone(variable)
                            variable.value = formItemConfig.attrs.value
                        }
                    }
                    // 特殊处理逻辑，针对子流程节点，如果为自定义类型的下拉框变量，默认开始支持用户创建不存在的选项配置项
                    if (variable.custom_type === 'select') {
                        formItemConfig.attrs.allowCreate = true
                    }
                    formItemConfig.tag_code = key
                    formItemConfig.attrs.name = variable.name
                    if (formItemConfig.type === 'combine') {
                        formItemConfig.name = variable.name
                    }
                    // 自定义输入框变量正则校验添加到插件配置项
                    if (['input', 'textarea'].includes(variable.custom_type) && variable.validation !== '') {
                        formItemConfig.attrs.validation.push({
                            type: 'regex',
                            args: variable.validation,
                            error_message: i18n.t('默认值不符合正则规则：') + variable.validation
                        })
                    }
                    // 参数填写时为保证每个表单 tag_code 唯一，原表单 tag_code 会被替换为变量 key，导致事件监听不生效
                    if (formItemConfig.hasOwnProperty('events')) {
                        formItemConfig.events.forEach(e => {
                            if (e.source === tagCode) {
                                e.source = '${' + e.source + '}'
                            }
                        })
                    }
                    inputs.push(formItemConfig)
                }))
                return inputs
            },
            /**
             * 加载标准插件表单配置项文件
             * 优先取 store 里的缓存
             */
            async getAtomConfig (config) {
                const { plugin, version, classify, name } = config
                try {
                    // 先取标准节点缓存的数据
                    const pluginGroup = this.atomFormConfig[plugin]
                    if (pluginGroup && pluginGroup[version]) {
                        return pluginGroup[version]
                    }
                    await this.loadAtomConfig({ atom: plugin, version, classify, name, project_id: this.project_id })
                    const config = $.atoms[plugin]
                    return config
                } catch (e) {
                    console.log(e)
                }
            },
            judgeDataEqual () {
                return tools.isDataEqual(this.initalRenderData, this.renderData)
            },
            async onRetryTask () {
                let formvalid = true
                if (this.$refs.renderForm) {
                    formvalid = this.$refs.renderForm.validate()
                }
                if (!formvalid || this.retrying) return false

                const { instance_id, component_code, node_id } = this.nodeDetailConfig
                try {
                    if (this.nodeDetailConfig.component_code) {
                        const data = {
                            instance_id,
                            node_id,
                            component_code,
                            inputs: this.renderData
                        }
                        if (component_code === 'subprocess_plugin') {
                            const { inputs } = this.nodeInfo.data
                            const constants = inputs.subprocess ? inputs.subprocess.pipeline.constants : {}
                            Object.keys(constants).forEach(key => {
                                constants[key].value = this.renderData[key]
                            })
                            data.inputs = inputs
                            data.inputs['_escape_render_keys'] = ['subprocess']
                        }
                        this.$emit('retrySuccess', data)
                    } else {
                        this.$emit('retrySuccess', { instance_id, node_id })
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            onCancelRetry () {
                const { node_id } = this.nodeDetailConfig
                this.$emit('retryCancel', node_id)
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';
    .retry-node-container {
        position: relative;
        height: 100%;
        overflow: hidden;
        .edit-wrapper {
            padding: 20px;
            height: calc(100% - 60px);
            overflow-y: auto;
            @include scrollbar;
        }
        .action-wrapper {
            padding-left: 20px;
            height: 60px;
            line-height: 60px;
            border-top: 1px solid $commonBorderColor;
            .confirm-btn{
                margin-right: 12px;
            }
        }
    }
</style>
