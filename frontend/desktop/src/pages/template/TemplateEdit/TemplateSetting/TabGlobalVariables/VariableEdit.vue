<template>
    <div class="variable-edit">
        <div class="variable-edit-content">
            <section class="form-section">
                <h3>{{ $t('基础信息') }}</h3>
                <!-- 名称 -->
                <div class="form-item clearfix">
                    <label class="required">{{ $t('名称') }}</label>
                    <div class="form-content">
                        <bk-input
                            name="variableName"
                            v-model="theEditingData.name"
                            v-validate="variableNameRule"
                            :readonly="isViewMode || isInternalVal"
                            :maxlength="stringLength.VARIABLE_NAME_MAX_LENGTH"
                            :show-word-limit="true">
                        </bk-input>
                        <span v-show="veeErrors.has('variableName')" class="common-error-tip error-msg">{{ veeErrors.first('variableName') }}</span>
                    </div>
                </div>
                <!-- key -->
                <div class="form-item clearfix">
                    <label class="required">Key</label>
                    <div class="form-content">
                        <bk-input
                            name="variableKey"
                            v-model="theEditingData.key"
                            v-validate="variableKeyRule"
                            :readonly="isViewMode || isInternalVal"
                            :disabled="isHookedVar && variableData.key !== ''">
                        </bk-input>
                        <span v-show="veeErrors.has('variableKey')" class="common-error-tip error-msg">{{ veeErrors.first('variableKey') }}</span>
                    </div>
                </div>
                <!-- 类型 -->
                <div class="form-item variable-type clearfix" v-if="!isInternalVal">
                    <label>{{ $t('类型') }}</label>
                    <div class="form-content">
                        <bk-select
                            v-model="currentValType"
                            :disabled="isViewMode || isHookedVar"
                            :clearable="false"
                            @change="onValTypeChange">
                            <template v-if="isHookedVar">
                                <bk-option
                                    v-for="(option, optionIndex) in varTypeList"
                                    :key="optionIndex"
                                    :id="option.code"
                                    :name="option.name">
                                </bk-option>
                            </template>
                            <template v-else>
                                <bk-option-group
                                    v-for="(group, groupIndex) in varTypeList"
                                    :key="groupIndex"
                                    :name="group.name">
                                    <bk-option
                                        v-for="(option, optionIndex) in group.children"
                                        :key="optionIndex"
                                        :id="option.code"
                                        :name="option.name">
                                    </bk-option>
                                </bk-option-group>
                            </template>
                        </bk-select>
                        <div class="phase-tag" v-if="varPhase">{{ varPhase }}</div>
                    </div>
                    <pre class="variable-type-desc" v-if="variableDesc">{{ variableDesc }}</pre>
                </div>
                <!-- 验证规则 -->
                <div v-show="['input', 'textarea'].includes(theEditingData.custom_type) && !isInternalVal" class="form-item clearfix">
                    <label class="form-label">{{ $t('正则校验') }}</label>
                    <div class="form-content">
                        <bk-input
                            name="valueValidation"
                            v-model="theEditingData.validation"
                            v-validate="validationRule"
                            :readonly="isViewMode"
                            @blur="onBlurValidation">
                        </bk-input>
                        <span v-show="veeErrors.has('valueValidation')" class="common-error-tip error-msg">{{veeErrors.first('valueValidation')}}</span>
                    </div>
                </div>
                <!-- 显示/隐藏 -->
                <div class="form-item clearfix" v-if="!isInternalVal">
                    <label class="form-label ">
                        <span v-bk-tooltips.top="$t('配置为「显示」可在执行时做为任务入参使用，配置为「隐藏」则仅能在流程内部使用')" class="condition-tip">{{ $t('执行时显示')}}</span>
                    </label>
                    <div class="form-content">
                        <bk-select
                            v-model="theEditingData.show_type"
                            :disabled="isViewMode || theEditingData.source_type === 'component_outputs'"
                            :clearable="false"
                            @change="onToggleShowType">
                            <bk-option
                                v-for="(option, index) in showTypeList"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                </div>
                <!-- 自动隐藏 -->
                <div class="form-item clearfix" v-if="theEditingData.show_type === 'show' && !isInternalVal">
                    <label class="form-label ">
                        <span v-bk-tooltips.top="$t('当满足条件时，原本做为入参的变量会隐藏起来无需录入')" class="condition-tip">{{ $t('“显示参数”条件隐藏')}}</span>
                    </label>
                    <div class="form-content">
                        <bk-select
                            v-model="theEditingData.is_condition_hide"
                            :disabled="isViewMode || theEditingData.source_type === 'component_outputs'"
                            :clearable="false"
                            @change="onToggleHideCond">
                            <bk-option id="true" :name="$t('开启')"></bk-option>
                            <bk-option id="false" :name="$t('关闭')"></bk-option>
                        </bk-select>
                    </div>
                </div>
                <!-- 触发条件 -->
                <div
                    class="form-item clearfix"
                    v-if="theEditingData.show_type === 'show' && theEditingData.is_condition_hide === 'true'">
                    <label class="form-label">
                        <span v-bk-tooltips.top="$t('所有变量值都会以字符串类型进行记录和判断，会忽略类型差异')" class="condition-tip">{{ $t('触发条件')}}</span>
                    </label>
                    <div class="trigger-condition" @click="isShowErrorMsg = false">
                        <div class="condition-item" v-for="(item, index) in hideConditionList" :key="index">
                            <bk-select
                                ext-cls="select-variable"
                                v-model="item.constant_key"
                                :disabled="isViewMode">
                                <bk-option
                                    v-for="variable in variableList"
                                    :key="variable.key"
                                    :id="variable.key"
                                    :name="variable.name">
                                </bk-option>
                            </bk-select>
                            <bk-select
                                ext-cls="select-operator"
                                v-model="item.operator"
                                :disabled="isViewMode">
                                <bk-option id="=" name="="></bk-option>
                                <bk-option id="!=" name="!="></bk-option>
                            </bk-select>
                            <bk-input
                                ext-cls="variable-value"
                                v-model="item.value"
                                :readonly="isViewMode">
                            </bk-input>
                            <div class="icon-operat">
                                <i class="bk-icon icon-plus-circle-shape" @click="addHideCondition"></i>
                                <i class="bk-icon icon-minus-circle-shape" @click="deleteHideCondition(index)"></i>
                            </div>
                        </div>
                        <p class="warning-msg">{{ $t('注意：如果命中条件，变量会保留填参页面的输入值并隐藏。如果变量为表单必填参数且输入值为空，可能会导致任务执行失败') }}</p>
                        <p class="common-error-tip error-msg" v-if="isShowErrorMsg">{{ errorMsgText }}</p>
                    </div>
                </div>
                <!-- 模板预渲染 -->
                <div class="form-item clearfix" v-if="!isInternalVal">
                    <label class="form-label required">
                        <span v-bk-tooltips.top="$t('常量在任务启动就完成变量值的计算，使用变量时不再重新计算保持值不变')" class="condition-tip">{{ $t('常量')}}</span>
                    </label>
                    <div class="form-content">
                        <bk-select
                            :value="String(theEditingData.pre_render_mako)"
                            :clearable="false"
                            :disabled="isViewMode"
                            name="preRenderMakoRule"
                            v-validate="{ required: true }"
                            @selected="onSelectPreRenderMako">
                            <bk-option
                                v-for="(option, index) in preRenderList"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                        <span v-show="veeErrors.has('preRenderMakoRule')" class="common-error-tip error-msg">{{ veeErrors.first('preRenderMakoRule') }}</span>
                    </div>
                </div>
                <!-- 描述 -->
                <div class="form-item clearfix">
                    <label class="form-label">{{ $t('提示文本') }}</label>
                    <div class="form-content" :class="['textarea-wrap', { 'readonly': isViewMode || isInternalVal }]">
                        <textarea
                            class="label_desc"
                            type="textarea"
                            v-model="theEditingData.desc"
                            :placeholder="isInternalVal ? ' ' : $t('请输入变量提示文本，不超过500个字符')"
                            :maxlength="500"
                            :readonly="isViewMode || isInternalVal">
                        </textarea>
                        <p class="limit-box"><span class="strong">{{ theEditingData.desc.length }}</span>/<span>500</span></p>
                    </div>
                </div>
            </section>
            <section v-if="!['component_outputs', 'system'].includes(theEditingData.source_type)" class="form-section">
                <h3>{{ theEditingData.is_meta ? $t('配置') : $t('默认值') }}</h3>
                <!-- 项目变量 -->
                <div class="form-item clearfix" v-if="theEditingData.source_type === 'project'">
                    <label>{{ $t('输入框') }}</label>
                    <div class="form-content">
                        <bk-input v-model="theEditingData.value" :readonly="true"></bk-input>
                    </div>
                </div>
                <!-- 默认值 -->
                <div class="form-item value-form clearfix" v-else>
                    <div class="form-content" v-bkloading="{ isLoading: atomConfigLoading, opacity: 1, zIndex: 100 }">
                        <template v-if="!atomConfigLoading && renderConfig.length">
                            <RenderForm
                                ref="renderForm"
                                :constants="constants"
                                :scheme="renderConfig"
                                :form-option="renderOption"
                                v-model="renderData">
                            </RenderForm>
                        </template>
                    </div>
                </div>
            </section>
        </div>
        <div class="btn-wrap">
            <template v-if="!isInternalVal">
                <bk-button v-if="!isViewMode" theme="primary" :disabled="atomConfigLoading || varTypeListLoading" @click="onSaveVariable">{{ $t('确定') }}</bk-button>
                <bk-button @click="$emit('closeEditingPanel')">{{ isViewMode ? $t('关闭') : $t('取消') }}</bk-button>
            </template>
            <bk-button v-else @click="$emit('closeEditingPanel')">{{ $t('关闭') }}</bk-button>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState, mapMutations } from 'vuex'
    import { Validator } from 'vee-validate'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import formSchema from '@/utils/formSchema.js'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'

    export default {
        name: 'VariableEdit',
        components: {
            RenderForm
        },
        props: {
            variableData: Object,
            common: [String, Number],
            isViewMode: Boolean
        },
        data () {
            const theEditingData = tools.deepClone(this.variableData)
            const { source_type, custom_type, hide_condition: hideCondition } = theEditingData
            const isHookedVar = ['component_inputs', 'component_outputs'].includes(source_type)
            const currentValType = isHookedVar ? source_type : custom_type
            const hideConditionList = hideCondition && hideCondition.length ? hideCondition : [{ constant_key: '', operator: '', value: '' }]

            return {
                theEditingData,
                isHookedVar, // 是否为勾选生成的变量
                currentValType,
                showTypeList: [
                    { id: 'show', name: i18n.t('显示（入参）') },
                    { id: 'hide', name: i18n.t('隐藏（非入参）') }
                ],
                hideConditionList,
                isShowErrorMsg: false,
                variableList: [],
                errorMsgText: '',
                preRenderList: [ // 下拉框组件选项 id 不支持传布尔值
                    { id: 'true', name: i18n.t('是') },
                    { id: 'false', name: i18n.t('否') }
                ],
                metaTag: undefined, // 元变量tag名称
                renderData: {},
                renderConfig: [],
                renderOption: {
                    showHook: false,
                    showGroup: false,
                    showLabel: true,
                    showVarList: true,
                    validateSet: ['custom', 'regex'],
                    formEdit: !this.isViewMode
                },
                varTypeListLoading: false,
                varTypeList: [], // 变量类型，input、textarea、datetime 等
                varTypeData: {},
                varRegexpData: { // input，textarea类型正则
                    input: '^.+$',
                    textarea: '^[\\s\\S]+$'
                },
                atomConfigLoading: false,
                atomTypeKey: '',
                stringLength: STRING_LENGTH,
                // 变量名称校验规则
                variableNameRule: {
                    required: true,
                    max: STRING_LENGTH.VARIABLE_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                // 正则校验规则
                validationRule: {
                    validReg: true
                }
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable,
                'outputs': state => state.template.outputs,
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            ...mapState('project', {
                'project_id': state => state.project_id
            }),
            // 是否为内置变量
            isInternalVal () {
                const keys = Object.keys(this.internalVariable)
                return keys.some(key => key === this.variableData.key)
            },
            /**
             * 变量配置项code
             */
            atomType () {
                const { custom_type, source_tag, source_type } = this.theEditingData

                if (source_type === 'component_inputs') {
                    return custom_type || source_tag.split('.')[0]
                } else {
                    return custom_type
                }
            },
            // 变量生命周期
            varPhase () {
                let phaseStr = ''
                const phaseMap = {
                    '1': i18n.t('即将下线'),
                    '2': i18n.t('已下线')
                }
                if (!['component_inputs', 'component_outputs'].includes(this.currentValType) && this.varTypeList.length) {
                    this.varTypeList.some(group => {
                        return group.children.some(item => {
                            if (item.code === this.currentValType) {
                                phaseStr = phaseMap[item.phase]
                                return true
                            }
                        })
                    })
                }
                return phaseStr
            },
            // 变量 Key 校验规则
            variableKeyRule () {
                const rule = {
                    required: true,
                    regex: /(^\${(?!_env_|_system\.)[a-zA-Z_]\w*}$)|(^(?!_env_|_system\.)[a-zA-Z_]\w*$)/, // 合法变量key正则，eg:${fsdf_f32sd},fsdf_f32sd
                    keyLength: true,
                    keyRepeat: true
                }
                // 勾选的变量编辑时不做长度校验
                if (this.isHookedVar && this.variableData.key !== '') {
                    delete rule.max
                }
                return rule
            },
            // 当前选中类型变量配置描述
            variableDesc () {
                let desc = ''
                if (this.isHookedVar) {
                    const item = this.varTypeList.find(i => i.code === this.currentValType)
                    if (item) {
                        desc = item.description
                    }
                } else {
                    this.varTypeList.some(group => {
                        const option = group.children.find(item => item.code === this.currentValType)
                        if (option) {
                            desc = option.description
                            return true
                        }
                    })
                }
                return desc
            }
        },
        created () {
            this.extendFormValidate()
        },
        async mounted () {
            const { is_meta, custom_type, source_tag, source_type } = this.theEditingData

            if (this.isHookedVar) {
                this.varTypeList = [
                    { code: 'component_inputs', name: i18n.t('节点输入') },
                    { code: 'component_outputs', name: i18n.t('节点输出') }
                ]
            } else {
                await this.getVarTypeList()
                // 若当前编辑变量为自定义变量类型的元变量，则取meta_tag
                if (is_meta && source_type === 'custom') {
                    const metaList = this.varTypeList.find(item => item.type === 'meta')
                    metaList.children.some(item => {
                        if (item.code === custom_type) {
                            this.metaTag = item.meta_tag
                            return true
                        }
                    })
                }
            }
            // 非输出参数勾选变量和系统内置变量(目前有自定义变量和输入参数勾选变量)需要加载标准插件配置项
            if (!['component_outputs', 'system'].includes(this.theEditingData.source_type)) {
                if (this.theEditingData.hasOwnProperty('value')) {
                    const sourceTag = (is_meta && source_type === 'custom') ? this.metaTag : source_tag
                    const tagCode = sourceTag.split('.')[1]
                    this.renderData = {
                        [tagCode]: this.theEditingData.value
                    }
                }
                this.getAtomConfig()
            }
            this.setTriggerCondInfo()
        },
        methods: {
            ...mapActions('template/', [
                'loadCustomVarCollection',
                'checkKey'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            ...mapMutations('template/', [
                'addVariable',
                'editVariable',
                'setOutputs'
            ]),
            // 获取触发条件数据
            setTriggerCondInfo () {
                if (!this.theEditingData.is_condition_hide) return
                const variableList = Object.values(this.constants).filter(item => {
                    return this.variableData.key !== item.key && item.source_type !== 'component_outputs'
                })
                const variableKeys = variableList.map(item => item.key)
                const list = []
                this.hideConditionList.forEach((item, index) => {
                    if (item.constant_key && !variableKeys.includes(item.constant_key)) {
                        list.push(item.constant_key)
                        this.hideConditionList.splice(index, 1)
                    }
                })
                let text = list.join(',')
                if (text) {
                    text = text + this.$t('变量未找到')
                } else {
                    text = this.$t('关系组内的数据不能为空')
                }
                this.variableList = variableList
                this.errorMsgText = text
                this.isShowErrorMsg = Boolean(list.length)
            },
            // 获取变量类型
            async getVarTypeList () {
                this.varTypeListLoading = true
                try {
                    const customVarCollection = await this.loadCustomVarCollection()
                    const listData = [
                        {
                            name: i18n.t('普通变量'),
                            type: 'general',
                            children: []
                        },
                        {
                            name: i18n.t('动态变量'),
                            type: 'dynamic',
                            children: []
                        },
                        {
                            name: i18n.t('元变量'),
                            type: 'meta',
                            children: []
                        }
                    ]
                    customVarCollection.forEach(item => {
                        if (item.type === 'general') {
                            listData[0].children.push(item)
                        } else if (item.type === 'dynamic') {
                            listData[1].children.push(item)
                        } else {
                            listData[2].children.push(item)
                        }
                    })
                    this.varTypeList = listData
                } catch (e) {
                    console.log(e)
                } finally {
                    this.varTypeListLoading = false
                }
            },
            /**
             * 加载表单标准插件配置文件
             */
            async getAtomConfig () {
                const { source_tag, custom_type, version = 'legacy', plugin_code } = this.theEditingData
                const tagStr = this.metaTag ? this.metaTag : source_tag

                // 兼容旧数据自定义变量勾选为输入参数 source_tag 为空
                const atom = tagStr.split('.')[0] || custom_type
                let classify = ''
                this.atomConfigLoading = true
                this.atomTypeKey = atom
                if (this.theEditingData.custom_type) {
                    classify = 'variable'
                } else {
                    classify = 'component'
                }
                if (atomFilter.isConfigExists(atom, version, this.atomFormConfig)) {
                    this.getRenderConfig()
                    this.$nextTick(() => {
                        this.atomConfigLoading = false
                    })
                    return
                }

                try {
                    // 第三方插件变量
                    if (plugin_code) {
                        const resp = await this.loadPluginServiceDetail({
                            plugin_code,
                            plugin_version: version,
                            with_app_detail: true
                        })
                        if (!resp.result) return
                        // 设置host
                        const { origin } = window.location
                        const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${plugin_code}/`
                        $.context.bk_plugin_api_host[plugin_code] = hostUrl
                        // 输入参数
                        $.atoms[plugin_code] = {}
                        const renderFrom = resp.data.forms.renderform
                        /* eslint-disable-next-line */
                        eval(renderFrom)
                        const config = $.atoms[plugin_code]
                        const { source_tag } = this.theEditingData
                        const tag = source_tag.split('.')[1]
                        this.renderConfig = tools.deepClone([config.find(item => item.tag_code === tag)])
                        return
                    }
                    await this.loadAtomConfig({
                        classify,
                        name: this.atomType,
                        project_id: this.common ? undefined : this.project_id,
                        version,
                        atom
                    })
                    this.getRenderConfig()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.atomConfigLoading = false
                }
            },
            getRenderConfig () {
                const { source_tag, custom_type, source_type, is_meta, meta, version = 'legacy' } = this.theEditingData
                const tagStr = this.metaTag || source_tag
                let [atom, tag] = tagStr.split('.')
                // 兼容旧数据自定义变量勾选为输入参数 source_tag 为空
                if (custom_type) {
                    atom = atom || custom_type
                    tag = tag || custom_type
                }
                const atomConfig = this.atomFormConfig[atom][version]
                let config = tools.deepClone(atomFilter.formFilter(tag, atomConfig))
                if (is_meta && source_type === 'component_inputs' && config.meta_transform) {
                    config = config.meta_transform(meta)
                }
                if (['input', 'textarea'].includes(custom_type)) {
                    config.attrs.validation.push({
                        type: 'regex',
                        args: this.getInputDefaultValueValidation(),
                        error_message: i18n.t('默认值不符合正则规则')
                    })
                }

                this.renderConfig = [config]
                if (!this.variableData.key) { // 新建变量
                    this.theEditingData.value = atomFilter.getFormItemDefaultValue(this.renderConfig)
                }
            },
            // 注册表单校验规则
            extendFormValidate () {
                this.validator = new Validator({})
                // 注册变量 key 是否重复校验规则
                this.validator.extend('keyRepeat', (value) => {
                    value = /^\$\{\w+\}$/.test(value) ? value : '${' + value + '}'
                    if (this.variableData.key === value) {
                        return true
                    }
                    if (value in this.constants || value in this.internalVariable) {
                        return false
                    }
                    return true
                })
                // 注册变量 key 长度规则
                this.validator.extend('keyLength', (value) => {
                    const reqLenth = /^\$\{\w+\}$/.test(value) ? (STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH + 3) : STRING_LENGTH.VARIABLE_KEY_MAX_LENGTH
                    return value.length <= reqLenth
                })
                // 注册正则表达式校验规则
                this.validator.extend('validReg', (value) => {
                    try {
                        /* eslint-disable */
                        new RegExp(value)
                        /* eslint-enable */
                    } catch (e) {
                        console.error(e)
                        return false
                    }
                    return true
                })
                // 注册默认值校验规则
                this.validator.extend('customValueCheck', (value) => {
                    try {
                        const reg = new RegExp(this.theEditingData.validation)
                        if (!reg.test(value)) {
                            return false
                        }
                        return true
                    } catch (e) {
                        console.error(e)
                        return false
                    }
                })
            },
            getValidateSet () {
                const { show_type, custom_type } = this.theEditingData
                const validateSet = ['required', 'custom', 'regex']

                // 隐藏状态下，默认值为必填项
                // 输入框显示类型为隐藏时，按照正则规则校验，去掉必填项校验
                if (show_type === 'show' || (show_type === 'hide' && ['input', 'textarea'].includes(custom_type))) {
                    return validateSet.slice(1)
                } else {
                    return validateSet
                }
            },
            // input 表单默认校验规则
            getInputDefaultValueValidation () {
                let validation = this.theEditingData.validation
                if (this.theEditingData.show_type === 'show') {
                    validation = validation ? `(^$)|(${validation})` : ''
                }
                return validation
            },
            // 变量类型切换
            onValTypeChange (val, oldValue) {
                // 将上一个类型的填写的数据存起来("集群模块IP选择器"的code与"ip选择器"code相同,需要单独处理)
                const valData = oldValue === 'set_module_ip_selector'
                    ? { set_module_ip_selector: tools.deepClone(this.renderData['ip_selector']) }
                    : tools.deepClone(this.renderData)
                Object.assign(this.varTypeData, valData)
                // 将input textarea类型正则存起来
                if (['input', 'textarea'].includes(oldValue)) {
                    this.varRegexpData[oldValue] = this.theEditingData.validation
                }
                let data
                this.varTypeList.some(group => {
                    const option = group.children.find(item => item.code === val)
                    if (option) {
                        data = option
                        return true
                    }
                })
                if (val in this.varTypeData) {
                    const value = this.varTypeData[val]
                    this.renderData = { [val === 'set_module_ip_selector' ? 'ip_selector' : val]: value }
                } else {
                    this.renderData = {}
                }
                // input textarea类型需要正则校验
                if (['input', 'textarea'].includes(val)) {
                    this.theEditingData.validation = this.varRegexpData[val]
                } else {
                    this.theEditingData.validation = ''
                }
                this.theEditingData.custom_type = data.code
                this.theEditingData.source_tag = data.tag
                this.theEditingData.is_meta = data.type === 'meta'
                this.metaTag = data.meta_tag

                const validateSet = this.getValidateSet()
                this.$set(this.renderOption, 'validateSet', validateSet)
                this.getAtomConfig()
            },
            // 校验正则规则是否合法
            onBlurValidation () {
                const config = tools.deepClone(this.renderConfig[0])
                const regValidate = config.attrs.validation.find(item => item.type === 'regex')
                if (!this.veeErrors.has('valueValidation')) {
                    regValidate.args = this.getInputDefaultValueValidation()
                } else {
                    regValidate.args = ''
                }
                this.$set(this.renderConfig, 0, config)
                this.$nextTick(() => {
                    this.$refs.renderForm.validate()
                })
            },
            /**
             * 变量显示/隐藏切换
             */
            onToggleShowType (showType, data) {
                this.theEditingData.show_type = showType
                // 预渲染功能发布前的模板主动修改变量的【显示类型】，预渲染默认值为false
                const variableData = this.variableData
                if (!variableData.hasOwnProperty('pre_render_mako')) {
                    this.theEditingData.pre_render_mako = false
                }
                const validateSet = this.getValidateSet()
                this.$set(this.renderOption, 'validateSet', validateSet)

                if (['input', 'textarea'].includes(this.theEditingData.custom_type)) {
                    const config = tools.deepClone(this.renderConfig[0])
                    const regValidate = config.attrs.validation.find(item => item.type === 'regex')
                    regValidate.args = this.getInputDefaultValueValidation()
                    this.$set(this.renderConfig, 0, config)
                    this.$nextTick(() => {
                        this.$refs.renderForm.validate()
                    })
                }
            },
            /**
             * 变量自动显示/隐藏切换
             */
            onToggleHideCond (val) {
                if (val === 'true' && !this.errorMsgText) {
                    this.setTriggerCondInfo()
                }
                this.theEditingData.is_condition_hide = val
                this.isShowErrorMsg = false
            },
            // 添加触发条件
            addHideCondition () {
                const condition = {
                    constant_key: '',
                    operator: '',
                    value: ''
                }
                this.hideConditionList.push(condition)
            },
            // 删除触发条件
            deleteHideCondition (index) {
                const length = this.hideConditionList.length
                if (length === 1) {
                    this.$bkMessage({
                        message: this.$t('至少保留一条触发条件'),
                        theme: 'warning'
                    })
                } else {
                    this.hideConditionList.splice(index, 1)
                }
            },
            // 选择是否为模板预渲染
            onSelectPreRenderMako (val) {
                this.theEditingData.pre_render_mako = val === 'true'
            },
            handleMaskClick () {
                if (!this.variableData.key) {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        confirmFn: () => {
                            this.$emit('closeEditingPanel')
                        }
                    })
                } else {
                    const editingVariable = tools.deepClone(this.theEditingData)
                    editingVariable.key = /^\$\{\w+\}$/.test(editingVariable.key) ? editingVariable.key : '${' + editingVariable.key + '}'
                    if (this.renderConfig.length > 0) {
                        const tagCode = this.renderConfig[0].tag_code
                        editingVariable.value = this.renderData[tagCode]
                    }

                    if (tools.isDataEqual(editingVariable, this.variableData)) {
                        this.$emit('closeEditingPanel')
                    } else {
                        this.$bkInfo({
                            ...this.infoBasicConfig,
                            confirmFn: () => {
                                this.$emit('closeEditingPanel')
                            }
                        })
                    }
                }
            },
            // 保存变量数据
            onSaveVariable () {
                return this.$validator.validateAll().then(async (result) => {
                    let formValid = true
                    const variable = this.theEditingData
                    variable.name = variable.name.trim()

                    // 触发条件
                    if (variable.show_type === 'show' && variable.is_condition_hide === 'true') {
                        const isTrue = this.hideConditionList.every(condition => {
                            return Object.values(condition).every(val => val)
                        })
                        this.isShowErrorMsg = !isTrue
                        if (!isTrue) return
                        variable.hide_condition = this.hideConditionList
                    } else {
                        variable.hide_condition = undefined
                    }
                    // 变量预渲染
                    if (variable.pre_render_mako) {
                        variable.pre_render_mako = Boolean(variable.pre_render_mako)
                    }
                    // renderform表单校验
                    if (this.renderConfig.length > 0) {
                        const tagCode = this.renderConfig[0].tag_code
    
                        if (this.$refs.renderForm) {
                            // 默认值执行校验的逻辑
                            // 1.表单设置为隐藏
                            // 2.表单设置为显示，但是默认值编辑后的当前值与已保存的值有差异，主要处理子流程勾选的变量如果有校验，但是不想修改值情况下无法保存的场景
                            if (variable.show_type === 'hide' || !tools.isDataEqual(variable.value, this.renderData[tagCode])) {
                                formValid = this.$refs.renderForm.validate()
                            }
                        }

                        if (!formValid) {
                            return false
                        } else {
                            variable.value = this.renderData[tagCode]
                        }
                    }

                    if (!result) {
                        return false
                    }

                    // 变量key值格式统一
                    if (!/^\$\{\w+\}$/.test(variable.key)) {
                        variable.key = '${' + variable.key + '}'
                    }

                    const checkKeyResult = await this.checkKey({ key: this.theEditingData.key })
                    if (!checkKeyResult.result) {
                        this.$bkMessage({
                            message: i18n.t('变量KEY为特殊标志符变量，请修改'),
                            theme: 'warning'
                        })
                        return
                    }

                    if (!this.variableData.key) { // 新增变量
                        if (!this.isHookedVar) { // 自定义变量
                            variable.version = 'legacy'
                            variable.form_schema = formSchema.getSchema(
                                variable.custom_type,
                                this.atomFormConfig[this.atomTypeKey][variable.version]
                            )
                        }
                        this.$emit('setNewCloneKeys', variable.key)
                        this.addVariable(tools.deepClone(variable))
                    } else { // 编辑变量
                        this.editVariable({ key: this.variableData.key, variable })
                        // 如果全局变量有被勾选为输出，修改变量 key 后需要更新 outputs 字段
                        if (this.variableData.key !== this.theEditingData.key && this.outputs.includes(this.variableData.key)) {
                            this.setOutputs({ changeType: 'edit', key: this.variableData.key, newKey: this.theEditingData.key })
                        }
                    }
                    this.$emit('onSaveEditing')
                    return true
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
    .variable-edit {
        height: 100%;
    }
    .variable-edit-content {
        padding: 20px 20px 40px;
        height: calc(100% - 49px);
        overflow-y: auto;
    }
    .form-section {
        margin-bottom: 30px;
        & > h3 {
            margin: 0;
            padding-bottom: 10px;
            color: #313238;
            font-size: 14px;
            font-weight: bold;
            border-bottom: 1px solid #cacedb;
        }
    }
    .form-item {
        margin: 15px 0;
        &:first-child {
            margin-top: 0;
        }
        label {
            position: relative;
            float: left;
            width: 120px;
            margin-top: 8px;
            font-size: 12px;
            color: #666666;
            text-align: right;
            word-wrap: break-word;
            word-break: break-all;
            &.required:before {
                content: '*';
                position: absolute;
                top: 2px;
                right: -10px;
                color: #ff2602;
                font-family: "SimSun";
            }
        }
        &.value-form {
            .form-content {
                margin-left: 0;
            }
        }
    }
    .form-content {
        margin-left: 140px;
        min-height: 36px;
        /deep/ {
            .bk-select {
                background: #ffffff;
                &.is-disabled {
                    background-color: #fafbfd !important;
                    border-color: #dcdee5 !important;
                }
            }
            .el-input {
                .el-input__inner {
                    padding: 0 10px;
                    height: 36px;
                    line-height: 36px;
                }
            }
            .tag-form {
                margin-left: 0;
            }
            .rf-tag-label {
                width: 120px;
            }
            .show-label > .rf-tag-form {
                margin-left: 140px;
            }
        }
    }
    .condition-tip {
        position: relative;
        line-height: 21px;
        &::after {
            content: '';
            position: absolute;
            left: 0;
            bottom: -3px;
            border-top: 1px dashed #979ba5;
            width: 100%
        }
    }
    .trigger-condition {
        margin-left: 140px;
        min-height: 36px;
        .condition-item {
            display: flex;
            align-items: center;
            margin-top: 10px;
            .select-variable {
                width: 200px;
                margin-right: 10px;
            }
            .select-operator {
                width: 105px;
                margin-right: 10px;
            }
            .variable-value {
                width: 220px;
                margin-right: 10px;
            }
            .icon-operat {
                line-height: 32px;
                margin-left: 16px;
                font-size: 18px;
                .bk-icon {
                    color: #c4c6cc;
                    margin-right: 6px;
                    cursor: pointer;
                    &:hover {
                        color: #979ba5;
                    }
                    &:last-child {
                        margin-right: 0;
                    }
                }
            }
            &:first-child {
                margin-top: 0;
            }
        }
    }
    .warning-msg {
        font-size: 12px;
        color: #ff9c01;
        margin-top: 10px;
    }
    .error-msg {
        margin-top: 10px;
    }
    .variable-type {
        position: relative;
        .phase-tag {
            position: absolute;
            right: 30px;
            top: 4px;
            padding: 3px 6px;
            border-radius: 10px;
            border-bottom-left-radius: 0;
            font-size: 12px;
            color: #ffffff;
            background: #b8b8b8;
        }
        .variable-type-desc {
            margin: 0 0 0 140px;
            font-size: 12px;
            color: #666;
            word-break: break-all;
            white-space: pre-wrap;
            font-family: 'Microsoft YaHei','PingFang SC','Hiragino Sans GB','SimSun','sans-serif';
        }
    }
    .btn-wrap {
        padding: 8px 30px;
        border-top: 1px solid #cacedb;
        .bk-button {
            margin-right: 10px;
            padding: 0 25px;
        }

    }
    .textarea-wrap {
        height: 88px;
        position: relative;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        &:focus-within {
            border-color: #3a84ff;
        }
        &.readonly {
            color: #aaaaaa;
            background: #fafbfd;
            border-color: #dedee5;
            cursor: not-allowed;
            .label_desc {
                background: #fafbfd;
            }
        }
        .label_desc {
            width: 100%;
            min-height: 70px;
            font-size: 12px;
            padding: 5px 10px;
            line-height: 1.5;
            margin-bottom: 16px;
            color: #63656e;
            border: none;
            resize: none;
            outline: none;
            border-radius: inherit;
            &::-webkit-input-placeholder {
                color: #c4c6cc;
            }
            &::-webkit-scrollbar {
                width: 4px;
                height: 4px;
                &-thumb {
                    border-radius: 20px;
                    background: #a5a5a5;
                    box-shadow: inset 0 0 6px hsla(0,0%,80%,.3);
                }
            }
        }
        .limit-box {
            position: absolute;
            bottom: 2px;
            right: 7px;
            font-size: 12px;
            margin: 0;
            padding: 0;
            color: #979ba5;
            transform: scale(0.8);
        }
    }
    /deep/ .variable-confirm-dialog-content {
        padding: 40px 0;
        text-align: center;
        .leave-tips {
            font-size: 24px;
            margin-bottom: 20px;
        }
        .action-wrapper .bk-button {
            margin-right: 6px;
        }
    }
</style>
