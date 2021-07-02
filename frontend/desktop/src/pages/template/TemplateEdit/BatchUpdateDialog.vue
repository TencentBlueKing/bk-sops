<template>
    <div class="batch-update-dialog-content">
        <div class="header-wrapper">
            <h4>批量更新子流程{{ $t('（') + expiredTplNum + $t('）') }}</h4>
            <div class="legend-area">
                <span class="legend-item delete">删除</span>
                <span class="legend-item add">新增</span>
            </div>
            <i class="bk-dialog-close bk-icon icon-close" @click="onCloseDialog"></i>
        </div>
        <div class="subflow-form-wrap" v-bkloading="{ isLoading: subflowFormsLoading, opacity: 1 }">
            <section
                v-for="subflow in subflowForms"
                :key="subflow.id"
                class="subflow-item">
                <div class="header-area" @click.self="subflow.fold = !subflow.fold">
                    <bk-checkbox v-model="subflow.checked"></bk-checkbox>
                    <h3>{{ subflow.name }}</h3>
                    <i :class="['bk-icon', 'icon-angle-up', 'fold-icon', subflow.fold ? 'fold' : '']" @click="subflow.fold = !subflow.fold"></i>
                </div>
                <div v-show="!subflow.fold" class="form-area">
                    <!-- 当前版本表单 -->
                    <div class="current-form">
                        <div class="version-tag">{{ $t('原版本') }}</div>
                        <!-- 输入参数 -->
                        <section class="config-section">
                            <h4>{{$t('输入参数')}}</h4>
                            <div class="inputs-wrapper">
                                <input-params
                                    v-if="subflow.currentForm.inputsConfig.length > 0"
                                    :is-subflow="true"
                                    :node-id="subflow.id"
                                    :editable="false"
                                    :scheme="subflow.currentForm.inputsConfig"
                                    :version="subflow.currentForm.version"
                                    :subflow-forms="subflow.currentForm.form"
                                    :value="subflow.currentForm.inputsValue"
                                    :constants="localConstants">
                                </input-params>
                                <no-data v-else></no-data>
                            </div>
                        </section>
                        <!-- 输出参数 -->
                        <section class="config-section">
                            <h4>{{$t('输出参数')}}</h4>
                            <div class="outputs-wrapper">
                                <output-params
                                    v-if="subflow.currentForm.outputs.length > 0"
                                    :constants="localConstants"
                                    :params="subflow.currentForm.outputs"
                                    :hook="false"
                                    :version="subflow.currentForm.version"
                                    :node-id="subflow.id">
                                </output-params>
                                <no-data v-else></no-data>
                            </div>
                        </section>
                    </div>
                    <!-- 新版本表单 -->
                    <div class="latest-form">
                        <div class="version-tag lastest">{{ $t('待更新版本') }}</div>
                        <!-- 输入参数 -->
                        <section class="config-section">
                            <h4>{{$t('输入参数')}}</h4>
                            <div class="inputs-wrapper">
                                <input-params
                                    v-if="subflow.latestForm.inputsConfig.length > 0"
                                    ref="inputParams"
                                    :is-subflow="true"
                                    :node-id="subflow.id"
                                    :scheme="subflow.latestForm.inputsConfig"
                                    :version="subflow.latestForm.version"
                                    :subflow-forms="subflow.latestForm.form"
                                    :value="subflow.latestForm.inputsValue"
                                    :constants="localConstants"
                                    @hookChange="onHookChange"
                                    @update="updateInputsValue(subflow.id, $event)">
                                </input-params>
                                <no-data v-else></no-data>
                            </div>
                        </section>
                        <!-- 输出参数 -->
                        <section class="config-section">
                            <h4>{{$t('输出参数')}}</h4>
                            <div class="outputs-wrapper">
                                <output-params
                                    v-if="subflow.latestForm.outputs.length"
                                    :constants="localConstants"
                                    :params="subflow.latestForm.outputs"
                                    :version="subflow.latestForm.version"
                                    :node-id="subflow.id"
                                    @hookChange="onHookChange">
                                </output-params>
                                <no-data v-else></no-data>
                            </div>
                        </section>
                    </div>
                </div>
            </section>
        </div>
        <div class="bk-dialog-footer">
            <bk-checkbox
                class="selecte-all"
                :indeterminate="selectedTplNum > 0 && selectedTplNum < expiredTplNum"
                :value="selectedTplNum > 0 && selectedTplNum === expiredTplNum"
                @change="onSelectedAllChange">
                {{ $t('全选') }}
            </bk-checkbox>
            <div class="action-btns">
                <span v-if="selectedTplNum > 0" class="selected-tips">{{ $t('已选择') + selectedTplNum + $t('个') + $t('待更新的子流程') }}</span>
                <bk-button
                    theme="primary"
                    style="margin-right: 8px;"
                    :disabled="subflowFormsLoading || !selectedTplNum"
                    @click="onConfirm">
                    {{ $t('批量更新') }}
                </bk-button>
                <bk-button @click="onCloseDialog">{{ $t('取消') }}</bk-button>
            </div>
        </div>
    </div>
</template>
<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import atomFilter from '@/utils/atomFilter.js'
    import tools from '@/utils/tools.js'
    import i18n from '@/config/i18n/index.js'
    import InputParams from './NodeConfig/InputParams.vue'
    import OutputParams from './NodeConfig/OutputParams.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'BatchUpdateDialog',
        components: {
            InputParams,
            OutputParams,
            NoData
        },
        props: {
            projectId: Number,
            list: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                subflowFormsLoading: false,
                subflowForms: [],
                localConstants: tools.deepClone(this.$store.state.template.constants) // 全局变量列表，用来维护当前面板勾选、反勾选后全局变量的变化情况，保存时更新到 store
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'constants': state => state.template.constants,
                'systemConstants': state => state.template.systemConstants.variables,
                'pluginConfigs': state => state.atomForm.config
            }),
            expiredTplNum () {
                return this.list.filter(item => item.expired).length
            },
            selectedTplNum () {
                return this.subflowForms.filter(item => item.checked).length
            }
        },
        created () {
            this.loadSubflowForms()
        },
        methods: {
            ...mapMutations('template/', [
                'setActivities',
                'setConstants',
                'setOutputs',
                'setSubprocessUpdated'
            ]),
            ...mapActions('template', [
                'getBatchForms'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig'
            ]),
            // 批量加载待更新流程模版当前版本和最新版本表单数据
            async loadSubflowForms () {
                try {
                    this.subflowFormsLoading = true
                    const tpls = []
                    this.list.map(item => {
                        if (item.expired) {
                            tpls.push({
                                id: item.template_id,
                                nodeId: item.subprocess_node_id,
                                version: item.version
                            })
                        }
                    })
                    const res = await this.getBatchForms({ tpls, projectId: this.projectId })
                    const subflowForms = []
                    tpls.forEach(tpl => {
                        const activity = this.activities[tpl.nodeId]
                        const { name, id, template_id, constants, version } = activity
                        const latestForm = this.getNodeFormData(res.data[template_id].find(item => item.is_current))
                        const currentForm = this.getNodeFormData(res.data[template_id].find(item => item.version === version))

                        for (const key in latestForm.form) {
                            const latestFormItem = latestForm.form[key]
                            if (!currentForm.form.hasOwnProperty(key) || latestFormItem.version !== currentForm.form[key].version) {
                                latestFormItem.status = 'added' // 标记最新版本子流程输入参数表单项是否为新增
                            }
                        }
                        latestForm.outputs.forEach(latestFormItem => {
                            const currentFormItem = currentForm.outputs.find(item => item.key === latestFormItem.key && item.version === latestFormItem.version)
                            if (!currentFormItem) {
                                latestFormItem.status = 'added' // 标记最新版本子流程输出参数表单项是否为新增
                            }
                        })
                        for (const key in currentForm.form) {
                            const currentFormItem = currentForm.form[key]
                            if (!latestForm.form.hasOwnProperty(key) || currentFormItem.version !== latestForm.form[key].version) {
                                currentFormItem.status = 'deleted' // 标记当前版本子流程输入参数表单项是否被删除
                            }
                            if (constants[currentFormItem.key]) {
                                currentForm.inputsValue[currentFormItem.key] = tools.deepClone(constants[currentFormItem.key].value)
                            }
                        }
                        currentForm.outputs.forEach(currentFormItem => {
                            const latestFormItem = latestForm.outputs.find(item => item.key === currentFormItem.key && item.version === currentFormItem.version)
                            if (!latestFormItem) {
                                currentFormItem.status = 'deleted' // 标记当前版本子流程输出参数表单项是否被删除
                            }
                        })
                        subflowForms.push({
                            name,
                            id,
                            template_id,
                            latestForm,
                            currentForm,
                            loading: false, // 输入参数表单是否在加载中
                            checked: false, // 是否选中更新
                            fold: false // 是否收起
                        })
                    })
                    this.subflowForms = subflowForms
                    this.getTplsFormConfig(subflowForms)
                } catch (e) {
                    console.error(e)
                } finally {
                    this.subflowFormsLoading = false
                }
            },
            // 加载当前版本和待更新版本流程的输入参数表单配置项
            async getTplsFormConfig (subflowForms) {
                const uniqueConfigMap = {}
                const variables = []
                const variablesConfig = {}
                const allSubflowInputForms = []
                subflowForms.forEach(subflow => {
                    const latestFormArr = Object.keys(subflow.latestForm.form).map(key => subflow.latestForm.form[key]).sort((a, b) => a.index - b.index)
                    const currentFormArr = Object.keys(subflow.currentForm.form).map(key => subflow.currentForm.form[key]).sort((a, b) => a.index - b.index)
                    allSubflowInputForms.push({
                        latestFormArr,
                        currentFormArr
                    })
                })
                allSubflowInputForms.forEach(subflowItem => {
                    [...subflowItem.latestFormArr, ...subflowItem.currentFormArr].forEach(item => {
                        const formKey = item.custom_type || item.source_tag.split('.')[0]
                        if (!uniqueConfigMap[`${formKey}_${item.version}`]) {
                            uniqueConfigMap[`${formKey}_${item.version}`] = true
                            variables.push(item)
                        }
                    })
                })
                await Promise.all(variables.map(async (variable) => {
                    const formKey = variable.custom_type || variable.source_tag.split('.')[0]
                    const { name, atom, classify } = atomFilter.getVariableArgs(variable)
                    const version = variable.version || 'legacy'
                    const config = await this.getAtomConfig(atom, version, classify, name)
                    variablesConfig[`${formKey}_${variable.version}`] = config
                }))

                allSubflowInputForms.forEach((subflow, index) => {
                    subflow.latestFormArr.forEach(item => {
                        const formKey = item.custom_type || item.source_tag.split('.')[0]
                        const formConfig = this.getSubflowInputFormItemConfig(item, variablesConfig[`${formKey}_${item.version}`])
                        this.subflowForms[index].latestForm.inputsConfig.push(formConfig)
                        this.subflowForms[index].latestForm.inputsValue[item.key] = tools.deepClone(item.value)
                    })
                    subflow.currentFormArr.forEach(item => {
                        const formKey = item.custom_type || item.source_tag.split('.')[0]
                        const formConfig = this.getSubflowInputFormItemConfig(item, variablesConfig[`${formKey}_${item.version}`])
                        this.subflowForms[index].currentForm.inputsConfig.push(formConfig)
                    })
                })
            },
            async getAtomConfig (plugin, version, classify, name) {
                const project_id = this.common ? undefined : this.project_id
                const pluginGroup = this.pluginConfigs[plugin]
                if (pluginGroup && pluginGroup[version]) {
                    return pluginGroup[version]
                }
                try {
                    await this.loadAtomConfig({ atom: plugin, version, classify, name, project_id })
                    const config = $.atoms[plugin]
                    return config
                } catch (e) {
                    console.error(e)
                }
            },
            getNodeFormData (tplForm) {
                const { form, outputs, version } = tplForm
                const inputForms = {}
                for (const key in form) { // 去掉隐藏变量
                    const item = form[key]
                    if (item.show_type === 'show') {
                        inputForms[key] = tools.deepClone(item)
                    }
                }
                const outputParams = Object.keys(outputs).map(item => { // 输出参数
                    const output = outputs[item]
                    return {
                        name: output.name,
                        key: output.key,
                        version: output.hasOwnProperty('version') ? output.version : 'legacy'
                    }
                })
                return {
                    form: inputForms,
                    outputs: outputParams,
                    inputsConfig: [],
                    inputsValue: {},
                    version
                }
            },
            getSubflowInputFormItemConfig (variable, atomConfig) {
                const { tagCode } = atomFilter.getVariableArgs(variable)
                let formItemConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                if (variable.is_meta || formItemConfig.meta_transform) {
                    formItemConfig = formItemConfig.meta_transform(variable.meta || variable)
                    if (!variable.meta) {
                        variable.value = formItemConfig.attrs.value
                    }
                }
                formItemConfig.attrs.name = variable.name
                formItemConfig.tag_code = variable.key
                formItemConfig.status = variable.status
                // 自定义输入框变量正则校验添加到插件配置项
                if (['input', 'textarea'].includes(variable.custom_type) && variable.validation !== '') {
                    formItemConfig.attrs.validation.push({
                        type: 'regex',
                        args: variable.validation,
                        error_message: i18n.t('默认值不符合正则规则：') + variable.validation
                    })
                }
                return formItemConfig
            },
            onSelectedAllChange (val) {
                this.subflowForms.forEach(item => {
                    item.checked = val
                })
            },
            // 输入、输出参数勾选状态变化
            onHookChange (type, data) {
                if (type === 'create') {
                    this.$set(this.localConstants, data.key, data)
                } else {
                    this.setVariableSourceInfo(data)
                }
            },
            // 更新全局变量的 source_info
            setVariableSourceInfo (data) {
                const { type, id, key, tagCode } = data
                const constant = this.localConstants[key]
                if (!constant) return
                const sourceInfo = constant.source_info
                if (type === 'add') {
                    if (sourceInfo[id]) {
                        sourceInfo[id].push(tagCode)
                    } else {
                        this.$set(sourceInfo, id, [tagCode])
                    }
                } else if (type === 'delete') {
                    if (sourceInfo[id].length <= 1) {
                        this.$delete(sourceInfo, id)
                    } else {
                        let atomIndex
                        sourceInfo[id].some((item, index) => {
                            if (item === tagCode) {
                                atomIndex = index
                                return true
                            }
                        })
                        sourceInfo[id].splice(atomIndex, 1)
                    }
                    if (!Object.keys(sourceInfo).length) {
                        this.deleteVariable(key)
                    }
                }
            },
            // 删除全局变量
            deleteVariable (key) {
                const constant = this.localConstants[key]

                for (const key in this.localConstants) {
                    const varItem = this.localConstants[key]
                    if (varItem.index > constant.index) {
                        varItem.index = varItem.index - 1
                    }
                }

                this.$delete(this.localConstants, key)
            },
            updateInputsValue (subflowId, value) {
                const subflow = this.subflowForms.find(item => item.id === subflowId)
                subflow.latestForm.inputsValue = value
            },
            handleVariableChange () {
                const constants = {}
                // 处理未选中节点中输入、输出参数表单的勾选关联
                const unCheckedNode = this.subflowForms.filter(item => !item.checked).map(item => item.id)
                Object.keys(this.localConstants).forEach(key => {
                    const varItem = tools.deepClone(this.localConstants[key])
                    if (['component_inputs', 'component_outputs'].includes(varItem.source_type)) {
                        const referNodes = Object.keys(varItem.source_info) // 引用该全局变量的节点

                        referNodes.forEach(node => { // 去掉变量被未选中的节点的引用
                            if (unCheckedNode.includes(node)) {
                                delete varItem.source_info[node]
                            }
                        })
                        if (Object.keys(varItem.source_info).length > 0) { // 至少被一个节点引用则保留该变量
                            constants[varItem.key] = varItem
                        }
                    } else {
                        // 自定义变量保留
                        constants[varItem.key] = varItem
                    }
                })

                // 如果变量已删除，需要删除变量是否输出的勾选状态
                this.subflowForms.forEach(subflow => {
                    subflow.latestForm.outputs.forEach(key => {
                        if (!(key in constants)) {
                            this.setOutputs({ changeType: 'delete', key })
                        }
                    })
                })
                // 设置全局变量面板icon小红点
                const localConstantKeys = Object.keys(constants)
                if (Object.keys(this.constants).length !== localConstantKeys.length) {
                    this.$emit('globalVariableUpdate', true)
                } else {
                    localConstantKeys.some(key => {
                        if (!(key in this.constants)) {
                            this.$emit('globalVariableUpdate', true)
                            return true
                        }
                    })
                }

                this.setConstants(constants)
            },
            onConfirm () {
                const selectedInputForms = this.$refs.inputParams ? this.$refs.inputParams.filter((item, index) => {
                    return this.subflowForms[index].checked
                }) : []
                if (selectedInputForms.every(item => item.validate())) {
                    this.subflowForms.filter(item => item.checked).forEach(item => {
                        const activity = tools.deepClone(this.activities[item.id])
                        activity.version = item.latestForm.version
                        Object.keys(activity.constants).forEach(key => {
                            const varItem = activity.constants[key]
                            varItem.value = item.latestForm.inputsValue[key]
                        })
                        this.setActivities({ type: 'edit', location: activity })
                        this.setSubprocessUpdated({
                            subprocess_node_id: item.id
                        })
                    })
                    this.handleVariableChange()
                    this.onCloseDialog()
                } else {
                    const errorEl = document.querySelector('.subflow-form-wrap .common-error-tip')
                    if (errorEl) {
                        errorEl.scrollIntoView()
                    }
                }
            },
            onCloseDialog () {
                this.$emit('close')
                // this.subflowForms = []
                // this.localConstants = tools.deepClone(this.$store.state.template.constants)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .batch-update-dialog-content {
        position: relative;
        height: 100%;
    }
    .header-wrapper {
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 80px 0 26px;
        height: 54px;
        line-height: 1;
        border-bottom: 1px solid #dcdee5;
        background: #ffffff;
        z-index: 1;
        & > h4 {
            margin: 0;
            font-weight: normal;
            font-size: 14px;
            color: #313238;
        }
        .legend-item {
            position: relative;
            display: inline-block;
            margin-left: 18px;
            padding-left: 20px;
            font-size: 14px;
            color: #63656e;
            line-height: 1;
            &:before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 3px;
            }
            &.delete:before {
                border: 1px solid rgba(251,133,121,0.16);
                background: #ffeeed;
            }
            &.add:before {
                border: 1px solid rgba(76,164,90,0.22);
                background: #e5ffe9;
            }
        }
        .bk-dialog-close {
            position: absolute;
            right: 20px;
            top: 16px;
            width: 26px;
            height: 26px;
            line-height: 26px;
            text-align: center;
            border-radius: 50%;
            font-size: 24px;
            font-weight: bold;
            color: #979ba5;
            cursor: pointer;
            &:hover {
                background-color: #f0f1f5;
            }
        }
    }
    .subflow-form-wrap {
        height: calc(100% - 110px);
        overflow: auto;
    }
    .subflow-item {
        border-bottom: 1px solid #ffffff;
        .header-area {
            position: relative;
            display: flex;
            align-items: center;
            padding: 14px 24px 14px 30px;
            background: #f4f4f4;
            cursor: pointer;
            & > h3 {
                margin: 0 0 0 8px;
                font-size: 14px;
                font-weight: bold;
            }
            .fold-icon {
                position: absolute;
                right: 20px;
                top: 12px;
                font-size: 24px;
                &.fold {
                    transform: rotate(180deg);
                }
            }
        }
        .form-area {
            display: flex;
            justify-content: space-between;
            overflow: hidden;
            .current-form,
            .latest-form {
                position: relative;
                width: 50%;
                padding-bottom: 38px;
                .config-section {
                    & > h4 {
                        margin: 26px 30px 20px;
                        padding-bottom: 10px;
                        color: #313238;
                        font-size: 14px;
                        font-weight: normal;
                        border-bottom: 1px solid #cacedb;
                    }
                }
                .outputs-wrapper {
                    margin: 0 30px;
                }
                /deep/ .rf-form-item {
                    margin: 0;
                    padding: 15px 20px;
                    .rf-tag-hook {
                        top: 20px;
                        right: 10px;
                    }
                }
                .version-tag {
                    position: absolute;
                    left: 0;
                    top: 0;
                    padding: 4px 7px;
                    font-size: 12px;
                    line-height: 1;
                    color: #ffffff;
                    background: #a8a8a8;
                    &:after {
                        content: '';
                        position: absolute;
                        top: 0;
                        right: -6px;
                        width: 0;
                        height: 0;
                        border-style: solid;
                        border-width: 20px 6px 0 0;
                        border-color: #a8a8a8 transparent transparent transparent;
                    }
                    &.lastest {
                        background: #1aaf41;
                        &:after {
                            border-color: #1aaf41 transparent transparent transparent;
                        }
                    }
                }
            }
            .current-form {
                background: #fcfcfc;
                .no-data-wrapper {
                    background: #fcfcfc;
                }
            }
        }
    }
    .selecte-all {
        position: absolute;
        bottom: 16px;
        left: 30px;
    }
    .action-btns {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        .selected-tips {
            margin-right: 12px;
            font-size: 14px;
            color: #313238;
        }
    }
</style>
<style lang="scss">
    .batch-update-dialog {
        .bk-dialog-tool {
            display: none;
        }
        .bk-dialog-header {
            padding: 0;
        }
        .bk-dialog-body {
            padding: 0;
        }
    }
</style>
