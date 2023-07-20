<template>
    <section class="info-section input-section" data-test-id="taskExecute_form_inputParams">
        <h4 class="common-section-title">{{ $t('输入参数') }}</h4>
        <div class="origin-value" v-if="!adminView">
            <bk-switcher size="small" @change="inputSwitcher" v-model="isShowInputOrigin"></bk-switcher>
            {{ 'Code' }}
        </div>
        <template v-if="!adminView">
            <div class="input-table" v-if="!isShowInputOrigin">
                <div class="table-header">
                    <span class="input-name">{{ $t('参数名') }}</span>
                    <span class="input-key">{{ $t('参数值') }}</span>
                </div>
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
        </template>
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
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'
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
                type: [Array, Object]
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
                    showRequired: false,
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
                deep: true,
                immediate: true
            }
        },
        mounted () {
            $.context.exec_env = 'NODE_EXEC_DETAIL'
        },
        beforeDestroy () {
            $.context.exec_env = ''
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

<style lang="scss" scoped>
    .input-section .input-table {
        flex: 1;
        display: flex;
        flex-direction: column;
        max-width: 682px;
        border: 1px solid #dcdee5;
        border-bottom: none;
        border-radius: 2px;
        .table-header {
            display: flex;
            align-items: center;
            height: 42px;
            color: #313238;
            border-bottom: 1px solid #dcdee5;
            background: #fafbfd;
            > span {
                padding: 10px 13px;
            }
            .input-name {
                line-height: 20px;
                width: 30%;
            }
        }
        /deep/.render-form {
            >.rf-form-item,
            .form-item-group >.rf-form-item {
                margin: 0;
                padding: 5px 0;
                width: 100% !important;
                border-bottom: 1px solid #dcdee5;
                label {
                    width: 30%;
                    text-align: left;
                    padding-left: 13px;
                    color: #63656e;
                    &::before {
                        content: initial;
                    }
                }
                >.rf-tag-form {
                    margin-left: 30%;
                    padding-left: 13px;
                    padding-right: 15px;
                }
                .el-table {
                    tr,
                    .el-table__cell {
                        height: 42px;
                        padding: 0;
                        background-color: initial;
                    }
                    .cell {
                        height: auto;
                        line-height: 20px;
                    }
                }
            }
            .tag-set-allocation-wrap,
            .tag-ip-selector-wrap,
            .tag-host-allocation-wrap {
                background: #f5f7fa;
            }
        }
        /deep/.bk-schema-form {
            .bk-form-item {
                margin: 0;
                padding: 5px 0;
                width: 100% !important;
                border-bottom: 1px solid #dcdee5;
                label {
                    width: 30% !important;
                    text-align: left;
                    padding-left: 13px;
                    color: #63656e;
                    &::before {
                        content: initial;
                    }
                }
                >.bk-form-content {
                    margin-left: 30% !important;
                    padding-left: 13px;
                    padding-right: 15px;
                }
                .el-table {
                    tr,
                    .el-table__cell {
                        height: 42px;
                        padding: 0;
                        background-color: initial;
                    }
                    .cell {
                        height: auto;
                        line-height: 20px;
                    }
                }
            }
        }
        .no-data-wrapper {
            padding: 16px 13px;
            border-bottom: 1px solid #dcdee5;
        }
    }
    .input-section .full-code-editor {
        height: 400px;
    }
</style>
