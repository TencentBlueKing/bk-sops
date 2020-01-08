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
    <div class="node-config-wrapper">
        <section class="config-section">
            <h3>{{i18n.basicInfo}}</h3>
            <basic-info
                :form-data.sync="basicInfo"
                :atom-list="atomList"
                :subflow-list="subflowList"
                @pluginChange="pluginChange"
                @versionChange="versionChange"
                @tplChange="tplChange">
            </basic-info>
        </section>
        <section class="config-section">
            <h3>{{i18n.inputParams}}</h3>
            <div class="inputs-wrapper" v-bkloading="{ isLoading: inputLoading }">
                <template v-if="!inputLoading">
                    <input-params
                        v-if="outputs.length > 0"
                        :node-id="nodeId"
                        :scheme="inputs"
                        :value="inputParamValue">
                    </input-params>
                    <no-data v-else></no-data>
                </template>
            </div>
        </section>
        <section class="config-section">
            <h3>{{i18n.outputParams}}</h3>
            <div class="outputs-wrapper" v-bkloading="{ isLoading: outputLoading }">
                <template v-if="!outputLoading">
                    <output-params
                        v-if="outputs.length > 0"
                        :node-id="nodeId"
                        :params="outputs">
                    </output-params>
                    <no-data v-else></no-data>
                </template>
            </div>
        </section>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import atomFilter from '@/utils/atomFilter.js'
    import tools from '@/utils/tools.js'
    import BasicInfo from './BasicInfo.vue'
    import InputParams from './InputParams.vue'
    import outputParams from './outputParams.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'NodeConfig',
        components: {
            BasicInfo,
            InputParams,
            outputParams,
            NoData
        },
        props: {
            nodeId: {
                type: String,
                default: ''
            },
            atomList: {
                type: Array,
                default () {
                    return []
                }
            },
            subflowList: {
                type: Array,
                default () {
                    return []
                }
            },
            common: {
                type: String,
                required: false
            }
        },
        data () {
            return {
                pluginLoading: false, // 普通任务节点数据加载
                subflowLoading: false, // 子流程任务节点数据加载
                constantsLoading: false, // 子流程输入参数配置项加载
                basicInfo: {},
                inputs: [],
                inputParamValue: {},
                outputs: [],
                constants: {}, // 子流程输入参数（引用的全局变量）
                i18n: {
                    basicInfo: gettext('基础信息'),
                    inputParams: gettext('输入参数'),
                    outputParams: gettext('输出参数')
                }
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'pluginConfigs': state => state.atomForm.config

            }),
            nodeConfig () { // 任务节点原始配置
                return tools.deepClone(this.activities[this.nodeId])
            },
            atomGroup () { // 某一标准插件下所有版本分组
                return this.atomList.find(item => item.code === this.basicInfo.plugin)
            },
            inputLoading () { // 以下任一方法处于 pending 状态，输入参数展示 loading 效果
                return this.pluginLoading || this.subflowLoading || this.constantsLoading
            },
            outputLoading () {
                return this.pluginLoading || this.subflowLoading
            }
        },
        watch: {
            nodeId () {
                this.basicInfo = this.getNodeBasic()
            }
        },
        created () {
            this.basicInfo = this.getNodeBasic()
            if (!this.nodeId) {
                return
            }
            this.initData()
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadSubflowConfig'
            ]),
            // 初始化节点数据
            async initData () {
                if (this.basicInfo.type === 'ServiceActivity') {
                    this.getPluginData()
                    Object.keys(this.nodeConfig.component.data || []).forEach(key => {
                        const val = tools.deepClone(this.nodeConfig.component.data[key].value)
                        this.$set(this.inputParamValue, key, val)
                    })
                } else {
                    this.constants = tools.deepClone(this.nodeConfig.constants)

                    const { version } = this.nodeConfig
                    await this.getSubflowData(version)
                    this.inputs = await this.getSubflowInputsConfig()
                    this.inputParamValue = this.getSubflowInputsValue()
                }
            },
            /**
             * 加载标准插件表单配置项文件
             * 优先取 store 里的缓存
             */
            async getAtomConfig (plugin, version, classify, name) {
                const pluginGroup = this.pluginConfigs[plugin]
                if (pluginGroup && pluginGroup[version]) {
                    return pluginGroup[version]
                }
                try {
                    await this.loadAtomConfig({ atom: plugin, version, classify, name })
                    const config = $.atoms[plugin]
                    return config
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            /**
             * 加载普通任务节点数据
             */
            async getPluginData () {
                const { plugin, version } = this.basicInfo
                this.pluginLoading = true
                try {
                    this.inputs = await this.getAtomConfig(plugin, version)
                    this.outputs = this.atomGroup.list.find(item => item.version === version).output
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pluginLoading = false
                }
            },
            /**
             * 加载子流程任务节点数据
             */
            async getSubflowData (version) {
                const { tpl } = this.basicInfo
                this.subflowLoading = true
                try {
                    const resp = await this.loadSubflowConfig({
                        templateId: tpl,
                        common: this.common,
                        version
                    })
                    // 输出变量
                    this.outputs = Object.keys(resp.outputs).map(item => {
                        const output = resp.outputs[item]
                        return {
                            name: output.name,
                            key: output.key
                        }
                    })
                    return resp
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.subflowLoading = false
                }
            },
            /**
             * 加载子流程输入参数表单配置项
             * 遍历每个非隐藏的全局变量，由 source_tag、coustom_type 字段确定需要加载的标准插件
             * 同时根据 source_tag 信息获取全局变量对应标准插件的某一个表单配置项
             *
             * @return {Array} 每个非隐藏全局变量对应表单配置项组成的数组
             */
            async getSubflowInputsConfig () {
                this.constantsLoading = true
                const inputs = []
                let variables = []
                Object.keys(this.constants).forEach(item => {
                    const from = this.constants[item]
                    if (from.show_type === 'show') { // 隐藏变量不显示
                        variables.push(from)
                    }
                })
                variables = variables.sort((a, b) => a.index - b.index)
                await Promise.all(variables.map(async (variable) => {
                    const { key } = variable
                    const { name, atom, tagCode, classify } = atomFilter.getVariableArgs(variable)
                    const version = variable.version || 'legacy'

                    const atomConfig = await this.getAtomConfig(atom, version, classify, name)
                    let formItemConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                    if (variable.is_meta || formItemConfig.meta_transform) {
                        formItemConfig = formItemConfig.meta_transform(variable.meta || variable)
                        if (!variable.meta) {
                            variable.value = formItemConfig.attrs.value
                        }
                    }
                    formItemConfig.tag_code = key
                    formItemConfig.attrs.name = variable.name

                    // 自定义输入框变量正则校验添加到插件配置项
                    if (variable.custom_type === 'input' && variable.validation !== '') {
                        formItemConfig.attrs.validation.push({
                            type: 'regex',
                            args: variable.validation,
                            error_message: gettext('默认值不符合正则规则：') + variable.validation
                        })
                    }

                    inputs.push(formItemConfig)
                }))
                this.constantsLoading = false
                return inputs
            },
            /**
             * 获取任务节点基础信息数据
             */
            getNodeBasic () {
                if (this.nodeConfig.type === 'ServiceActivity') {
                    const {
                        type, component, name, stage_name, error_ignorable,
                        can_retry, retryable, isSkipped, skippable, optional
                    } = this.nodeConfig
                    // 空节点不存在 atom
                    const atom = this.atomList.find(item => item.code === component.code)

                    return {
                        plugin: component.code,
                        version: component.code ? component.version || 'legacy' : '',
                        versionList: this.getAtomVersions(component.code),
                        name: name,
                        desc: atom ? atom.desc : '',
                        step: stage_name,
                        ignorable: error_ignorable,
                        skippable: isSkipped || skippable,
                        retryable: retryable || can_retry,
                        selectable: optional,
                        type
                    }
                } else {
                    const { type, template_id, name, stage_name, optional } = this.nodeConfig
                    return {
                        tpl: template_id,
                        name: name,
                        step: stage_name,
                        selectable: optional,
                        type
                    }
                }
            },
            /**
             * 获取某一标准插件所有版本列表
             */
            getAtomVersions (code) {
                if (!code) {
                    return []
                }
                const atom = this.atomList.find(item => item.code === code)
                return atom.list.map(item => {
                    return {
                        version: item.version
                    }
                })
            },
            /**
             * 获取子流程任务节点输入参数值
             */
            getSubflowInputsValue () {
                return Object.keys(this.constants).reduce((acc, cur) => {
                    const variable = this.constants[cur]
                    acc[variable.key] = tools.deepClone(variable.value)
                    return acc
                }, {})
            },
            pluginChange () {
                const { name, desc, outputs } = this.atomGroup
                const versionList = this.getAtomVersions(this.basicInfo.plugin)
                const config = {
                    versionList: versionList,
                    version: versionList[versionList.length - 1].version,
                    name: name,
                    desc: desc,
                    ignorable: false,
                    skippable: true,
                    retryable: true,
                    selectable: false
                }
                Object.assign(this.basicInfo, config)
                this.outputs = outputs
                this.inputParamValue = {}
                this.getPluginData()
            },
            versionChange () {
                this.getPluginData()
                this.inputParamValue = {}
            },
            async tplChange () {
                const tpl = this.subflowList.find(item => item.template_id === this.basicInfo.tpl)
                this.basicInfo.name = tpl.name
                this.basicInfo.selectable = false
                const subflowData = await this.getSubflowData()
                this.constants = subflowData.form
                this.inputs = await this.getSubflowInputsConfig()
                this.inputParamValue = this.getSubflowInputsValue()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .node-config-wrapper {
        float: left;
        padding: 15px 20px;
        width: 694px;
        height: 100%;
        background: #ffffff;
        border-left: 1px solid #dddddd;
        box-shadow: -4px 0 6px -4px rgba(0, 0, 0, .15);
        overflow-y: auto;
    }
    .config-section {
        margin-bottom: 50px;
        & > h3 {
            margin: 0 0 20px 0;
            padding-bottom: 14px;
            font-size: 14px;
            font-weight: bold;
            line-height: 1;
            color: #313238;
            border-bottom: 1px solid #cacecb;
        }
        .inputs-wrapper,
        .outputs-wrapper {
            min-height: 80px;
        }
    }
</style>
