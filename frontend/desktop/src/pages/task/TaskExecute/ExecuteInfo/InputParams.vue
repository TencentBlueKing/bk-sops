<template>
    <section class="info-section" data-test-id="taskExecute_form_inputParams">
        <div class="common-section-title input-parameter">
            <div class="input-title">{{ $t('输入参数') }}</div>
            <div class="origin-value" v-if="!adminView">
                <bk-switcher @change="inputSwitcher" v-model="isShowInputOrigin"></bk-switcher>
                {{ $t('原始值') }}
            </div>
        </div>
        <div v-if="!adminView">
            <div v-if="!isShowInputOrigin">
                <template v-if="Array.isArray(renderConfig)">
                    <RenderForm
                        v-if="!isEmptyParams && !loading"
                        :key="renderKey"
                        :scheme="renderConfig"
                        :form-option="renderOption"
                        :constants="inputConstants"
                        v-model="inputRenderDate">
                    </RenderForm>
                    <NoData v-else></NoData>
                </template>
                <template v-else>
                    <jsonschema-form
                        v-if="renderConfig.properties && Object.keys(renderConfig.properties).length > 0"
                        :schema="renderConfig"
                        :value="inputRenderDate">
                    </jsonschema-form>
                    <no-data v-else></no-data>
                </template>
            </div>
            <full-code-editor v-else :value="inputsInfo"></full-code-editor>
        </div>
        <div class="code-block-wrap" v-else>
            <VueJsonPretty :data="inputsInfo"></VueJsonPretty>
        </div>
    </section>
</template>

<script>
    import VueJsonPretty from 'vue-json-pretty'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import JsonschemaForm from './JsonschemaForm.vue'
    import FullCodeEditor from '../FullCodeEditor.vue'
    import tools from '@/utils/tools.js'
    export default {
        components: {
            VueJsonPretty,
            NoData,
            RenderForm,
            JsonschemaForm,
            FullCodeEditor
        },
        props: {
            adminView: {
                type: Boolean,
                default: false
            },
            loading: {
                type: Boolean,
                default: false
            },
            inputs: {
                type: Object,
                default: () => ({})
            },
            renderConfig: {
                type: Array,
                default: () => ([])
            },
            constants: {
                type: Object,
                default: () => ({})
            },
            renderData: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                isShowInputOrigin: false,
                inputsInfo: null,
                renderOption: {
                    showGroup: false,
                    showLabel: true,
                    showHook: false,
                    formEdit: false,
                    formMode: false
                },
                renderKey: null,
                inputConstants: {},
                inputRenderDate: {}
            }
        },
        computed: {
            isEmptyParams () {
                return this.renderConfig && this.renderConfig.length === 0
            }
        },
        watch: {
            inputs: {
                handler (val) {
                    this.inputsInfo = tools.deepClone(val)
                },
                immediate: true
            },
            constants: {
                handler (val) {
                    const constants = tools.deepClone(val)
                    if (constants.subflow_detail_var) {
                        // 兼容接口返回的key值和form配置的key不同
                        Object.keys(this.inputs).forEach(key => {
                            if (!(key in constants) && /^\${[^${}]+}$/.test(key)) {
                                const varKey = key.split('').slice(2, -1).join('')
                                if (varKey in constants) {
                                    constants[key] = constants[varKey]
                                    this.$delete(constants, varKey)
                                }
                            }
                        })
                    }
                    this.inputConstants = constants
                },
                deep: true
            },
            renderData: {
                handler (val) {
                    this.renderKey = new Date().getTime()
                    const renderData = tools.deepClone(val)
                    // 兼容form配置的key为变量的情况
                    if (this.constants.subflow_detail_var) {
                        Object.keys(this.renderData).forEach(key => {
                            const value = this.renderData[key]
                            if (/^\${[^${}]+}$/.test(value) && key in this.inputConstants) {
                                this.renderData[key] = this.inputConstants[key]
                            }
                        })
                    }
                    this.inputRenderDate = renderData
                },
                deep: true
            }
        },
        methods: {
            inputSwitcher () {
                if (!this.isShowInputOrigin) {
                    this.inputsInfo = this.constants.subflow_detail_var ? tools.deepClone(this.inputs) : JSON.parse(this.inputsInfo)
                } else {
                    let info = this.inputs
                    if (this.constants.subflow_detail_var) {
                        info = tools.deepClone(this.constants)
                        this.$delete(info, 'subflow_detail_var')
                    }
                    this.inputsInfo = JSON.stringify(info, null, 4)
                }
            }
        }
    }
</script>

<style>

</style>
