<template>
    <div class="variable-cited-wrap" :class="{ 'select-variable-mode': isSelect }" v-bkloading="{ isLoading }">
        <dl class="reference-wrap">
            <dt>{{ isSubFlow ? $t('所属模板') : $t('所属插件') }}</dt>
            <dd>{{ citedConfig.plugin || '--' }}</dd>
            <dt>{{ $t('字段') }}</dt>
            <dd>{{ citedConfig.field || '--' }}</dd>
            <template v-if="isSelect">
                <dt class="select-dt">{{ $t('选择变量') }}</dt>
                <div class="variable-content">
                    <div
                        :class="['variable-list', { 'active': selectedVarKey === variable.key }]"
                        v-for="variable in reuseList"
                        :key="variable.key"
                        @click="onSelectVariable(variable)">
                        <div class="variable-info">
                            <p class="key" v-bk-overflow-tips>{{ variable.key }}</p>
                            <p class="field" v-bk-overflow-tips>{{ variable.name.split('(')[0] }}</p>
                            <i class="bk-icon icon-edit-line" @click.stop="onEditVariable(variable, 'edit')"></i>
                        </div>
                        <div class="variable-cited">
                            <dt class="source-dt">{{ $t('变量来源节点') }}</dt>
                            <template v-if="variable.list.length">
                                <dd
                                    v-for="item in variable.list"
                                    :key="item.id"
                                    class="source-dd">
                                    {{ item.name }}
                                </dd>
                            </template>
                            <dd v-else>{{ '--' }}</dd>
                        </div>
                    </div>
                    <div class="create-variable" @click="onEditVariable(variableData, 'create')">
                        <i class="bk-icon icon-plus-line"></i>
                        {{ $t('使用新变量') }}
                    </div>
                </div>
            </template>
            <template v-else>
                <dt class="source-dt">{{ $t('变量来源节点') }}</dt>
                <dd
                    v-for="item in varSourceNode"
                    :key="item.id"
                    class="source-dd">
                    {{ item.name }}
                </dd>
            </template>
        </dl>
        
    </div>
</template>

<script>
    import { mapState, mapActions } from 'vuex'
    import atomFilter from '@/utils/atomFilter.js'
    import tools from '@/utils/tools.js'
    import { random4 } from '@/utils/uuid.js'
    export default {
        name: 'VariableCitedConfig',
        props: {
            variableCited: Object,
            variableData: Object,
            isSelect: Boolean,
            hookParams: Object
        },
        data () {
            const {
                plugin,
                field,
                nodeId,
                isSubFlow,
                reuseList
            } = this.variableData.cited_info || {}
            return {
                citedConfig: {
                    plugin,
                    field
                },
                nodeId,
                isSubFlow,
                reuseList,
                isLoading: false,
                subFlowForms: {},
                outputs: [],
                selectedVarKey: this.variableData.key
            }
        },
        computed: {
            ...mapState({
                constants: state => state.template.constants,
                atomList: state => state.template.atomList,
                activities: state => state.template.activities,
                thirdPartyList: state => state.template.thirdPartyList,
                pluginOutput: state => state.atomForm.output
            }),
            varSourceNode () {
                const { source_info: sourceInfo = {}, cited_info: citedInfo } = this.variableData
                const list = Object.keys(sourceInfo).map(key => {
                    const nodeConfig = this.activities[key]
                    return {
                        ...nodeConfig,
                        name: nodeConfig.name || citedInfo.nodeName
                    }
                })
                return list
            },
            atomGroup () { // 某一标准插件下所有版本分组
                let atom = this.atomList.find(item => item.code === this.basicInfo.plugin)
                atom = atom || this.isolationAtomConfig
                return atom
            }
        },
        created () {
            if (!this.variableData.cited_info) {
                this.getCitedConfig()
            }
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail',
                'loadPluginServiceAppDetail'
            ]),
            
            ...mapActions('task', [
                'loadSubflowConfig'
            ]),
            async getCitedConfig () {
                try {
                    const {
                        source_info: sourceInfo = {},
                        source_tag: sourceTag,
                        source_type: sourceType
                    } = this.variableData
                    let plugin; let field; let isThird
                    // 来源节点
                    const list = Object.keys(sourceInfo).map(key => this.activities[key])

                    const nodeConfig = list[0]
                    const {
                        component,
                        id: nodeId,
                        template_id: tplId,
                        scheme_id_list: schemes,
                        type: compType,
                        name
                    } = nodeConfig

                    let version; let atom
                    
                    // 所属插件/模板
                    this.isSubFlow = compType !== 'ServiceActivity'
                    if (this.isSubFlow) {
                        plugin = name
                        version = nodeConfig.version
                    } else {
                        isThird = component?.code === 'remote_plugin'
                        if (isThird) {
                            const code = component.data.plugin_code.value
                            const resp = await this.loadPluginServiceAppDetail({ plugin_code: code })
                            plugin = resp.data.name
                            atom = this.$parent.thirdPartyList[this.nodeId]
                            version = atom.version
                        } else {
                            atom = this.atomList.find(item => item.code === component.code)
                            plugin = `${atom.group_name}-${atom.name}`
                            version = component.hasOwnProperty('version') ? component.version : 'legacy'
                        }
                    }
                    // 来源字段
                    let atomConfig = []
                    if (this.isSubFlow) {
                        await this.getSubFlowDetail({
                            tpl: tplId,
                            version,
                            schemes
                        })
                        atomConfig = await this.getSubFlowInputsConfig()
                    } else {
                        const code = isThird ? component.data.plugin_code.value : component.code
                        atomConfig = await this.getAtomConfig({
                            plugin: code,
                            version,
                            isThird
                        })
                    }
                    if (sourceType === 'component_inputs') {
                        const config = atomConfig.find(item => {
                            let code = sourceTag.split('.')[1]
                            code = this.isSubFlow ? `\${${code}}` : code
                            return code === item.tag_code
                        })
                        field = config.attrs.name
                    } else {
                        const key = sourceInfo[nodeId][0]
                        const outputs = (isThird || this.isSubFlow)
                            ? this.outputs
                            : atom.list.find(item => item.version === version).output
                        const config = outputs.find(item => item.key === key)
                        field = config.name
                    }

                    this.citedConfig = {
                        plugin,
                        field,
                        list
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isLoading = false
                }
            },
            /**
             * 加载标准插件表单配置项文件
             * 优先取 store 里的缓存
             */
            async getAtomConfig (config) {
                const { plugin, version, name, classify, isThird } = config
                const { params, query } = this.$route
                const project_id = query.common ? undefined : params.project_id
                try {
                    // 第三方插件
                    if (isThird) {
                        const resp = await this.loadPluginServiceDetail({
                            plugin_code: plugin,
                            plugin_version: version,
                            with_app_detail: true
                        })
                        if (!resp.result) return
                        // 获取参数
                        const { outputs: respOutputs, forms, inputs } = resp.data
                        if (forms.renderform) {
                            if (!this.isSubFlow) {
                                // 获取第三方插件公共输出参数
                                if (!this.pluginOutput['remote_plugin']) {
                                    await this.loadAtomConfig({ atom: 'remote_plugin', version: '1.0.0' })
                                }
                                // 输出参数
                                const storeOutputs = this.pluginOutput['remote_plugin']['1.0.0']
                                const outputs = []
                                for (const [key, val] of Object.entries(respOutputs.properties)) {
                                    outputs.push({
                                        name: val.title,
                                        key,
                                        type: val.type,
                                        schema: { description: val.description || '--' }
                                    })
                                }
                                this.outputs = [...storeOutputs, ...outputs]
                            }
                            // 获取host
                            const { origin } = window.location
                            const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${plugin}/`
                            $.context.bk_plugin_api_host[plugin] = hostUrl
                            // 输入参数
                            $.atoms[plugin] = {}
                            const renderFrom = forms.renderform
                            /* eslint-disable-next-line */
                            eval(renderFrom)
                        } else {
                            $.atoms[plugin] = inputs
                            this.outputs = [] // jsonschema form输出参数
                        }
                    } else {
                        await this.loadAtomConfig({ atom: plugin, version, name, classify, project_id })
                    }
                    const config = $.atoms[plugin]
                    return config
                } catch (e) {
                    console.log(e)
                }
            },
            /**
             * 加载子流程任务节点输入、输出、版本配置项
             */
            async getSubFlowDetail ({ tpl, version = '', schemes = [] }) {
                try {
                    const params = {
                        template_id: tpl,
                        scheme_id_list: schemes,
                        version
                    }
                    const { params: routeParams, query } = this.$route
                    if (query.common) {
                        params.template_source = 'common'
                    } else {
                        params.project_id = routeParams.project_id
                    }
                    const resp = await this.loadSubflowConfig(params)
                    // 子流程的输入参数包括流程引用的变量、自定义变量和未被引用的变量
                    this.subFlowForms = { ...resp.data.pipeline_tree.constants, ...resp.data.custom_constants, ...resp.data.constants_not_referred }

                    // 输出变量
                    this.outputs = Object.keys(resp.data.outputs).map(item => {
                        const output = resp.data.outputs[item]
                        return {
                            plugin_code: output.plugin_code,
                            name: output.name,
                            key: output.key,
                            version: output.hasOwnProperty('version') ? output.version : 'legacy'
                        }
                    })
                } catch (e) {
                    console.log(e)
                }
            },
            /**
             * 加载子流程输入参数表单配置项
             * 遍历每个非隐藏的全局变量，由 source_tag、coustom_type 字段确定需要加载的标准插件
             * 同时根据 source_tag 信息获取全局变量对应标准插件的某一个表单配置项
             *
             * @return {Array} 每个非隐藏全局变量对应表单配置项组成的数组
             */
            async getSubFlowInputsConfig () {
                const variables = Object.keys(this.subFlowForms)
                    .map(key => this.subFlowForms[key])
                    .filter(item => item.show_type === 'show')
                    .sort((a, b) => a.index - b.index)

                const inputs = await Promise.all(variables.map(async (variable) => {
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
                    // 自定义输入框变量正则校验添加到插件配置项
                    if (['input', 'textarea'].includes(variable.custom_type) && variable.validation !== '') {
                        formItemConfig.attrs.validation.push({
                            type: 'regex',
                            args: variable.validation,
                            error_message: this.$t('默认值不符合正则规则：') + variable.validation
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
                    return formItemConfig
                }))
                return inputs
            },
            // 选中变量
            onSelectVariable (variable) {
                this.selectedVarKey = variable.key
                this.$emit('update', variable.key)
            },
            // 编辑变量
            onEditVariable (variable, type) {
                const { cited_info: citedInfo } = this.variableData
                if (type === 'create') {
                    const { nodeId } = variable.cited_info
                    const code = variable.source_tag.split('.')[1]
                    const key = `\${${code}_${random4()}}`
                    this.$emit('onAddVariable', {
                        ...this.variableData,
                        key,
                        name: this.citedConfig.field,
                        type,
                        source_info: {
                            [nodeId]: [code]
                        },
                        cited_info: {
                            ...citedInfo,
                            key: '',
                            oldKey: citedInfo.key
                        }
                    })
                } else {
                    const varInfo = this.constants[variable.key]
                    // 使用变量勾选时变量来源
                    const source_info = variable.list.reduce((acc, cur) => {
                        acc[cur.id] = [variable.key.slice(2, -1)]
                        return acc
                    }, {})
                    this.$emit('onEditVariable', {
                        ...this.variableData,
                        ...varInfo,
                        type,
                        source_info,
                        cited_info: { // 处理编辑未选中变量的情况
                            ...citedInfo,
                            key: variable.key,
                            oldKey: citedInfo.key
                        }
                    })
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.variable-cited-wrap {
    padding: 12px 16px 16px;
    margin-bottom: 30px;
    font-size: 12px;
    line-height: 26px;
    color: #313238;
    background: #f5f7fa;
    border-radius: 2px;
    dt {
        color: #979ba5;
        margin: 16px 0 2px;
        &.select-dt,
        &.source-dt {
            line-height: 20px;
            margin-bottom: 6px;
        }
        &:first-child {
            margin-top: 0;
        }
    }
    .source-dd {
        line-height: 20px;
        margin-bottom: 6px;
        color: #63656e;
        &::before {
            content: '';
            display: inline-block;
            height: 8px;
            width: 8px;
            position: relative;
            top: 1px;
            margin: 0 8px 0 4px;
            background: #f0f1f5;
            border: 1px solid #c4c6cc;
            border-radius: 50%;
        }
        &:last-child {
            margin-bottom: 0;
        }
    }
}
.select-variable-mode {
    padding: 16px 0 0;
    margin-bottom: 0;
    background: #fff;
    .reference-wrap {
        height: 100%;
        display: flex;
        flex-direction: column;
        dt,
        dd {
            padding: 0 24px;
        }
    }
    .variable-content {
        padding: 0 24px;
        overflow-y: auto;
        @include scrollbar;
    }
    .variable-list {
        margin-bottom: 8px;
        line-height: 20px;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        &:hover {
            border-color: #979ba5;
            cursor: pointer;
            .icon-edit-line {
                display: block;
            }
        }
        &.active {
            border-color: #3a84ff;
            .key {
                color: #3a84ff;
            }
        }
    }
    .variable-info {
        position: relative;
        padding: 7px 16px 8px;
        color: #979ba5;
        background: #f5f7fa;
        border-radius: 2px 2px 0 0;
        .key {
            color: #313238;
            margin-bottom: 4px;
        }
        .key,
        .field {
            padding-right: 25px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        .icon-edit-line {
            position: absolute;
            top: 22px;
            right: 16px;
            display: none;
            font-size: 16px;
            color: #979ba5;
            &:hover {
                color: #3a84ff;
            }
        }
    }
    .variable-cited {
        padding: 12px 15px 16px;
    }
    .create-variable {
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
        color: #63656e;
        border: 1px dashed #979ba5;
        border-radius: 2px;
        i {
            font-size: 14px;
            color: #979ba5;
            margin-right: 5px;
        }
        &:hover {
            cursor: pointer;
            color: #3a84ff !important;
            border-color: #3a84ff;
            i {
                color: #3a84ff;
            }
        }
    }
}
</style>
