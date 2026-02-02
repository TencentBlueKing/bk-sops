<template>
    <section class="info-section input-section" data-test-id="taskExecute_form_inputParams">
        <div class="section-title-wrap">
            <i
                class="trigger common-icon-next-triangle-shape"
                :class="{ 'is-expand': isExpand }"
                @click="isExpand = !isExpand"></i>
            {{ $t('输入参数') }}
            <div class="origin-value" v-if="!adminView">
                <bk-switcher size="small" @change="inputSwitcher" v-model="isShowInputOrigin"></bk-switcher>
                {{ 'Code' }}
            </div>
        </div>
        <template v-if="!adminView && isExpand">
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
                        :constants="constants"
                        v-model="inputRenderData">
                    </RenderForm>
                    <NoData v-else></NoData>
                </template>
                <template v-else>
                    <jsonschema-form
                        v-if="renderConfig && renderConfig.properties && Object.keys(renderConfig.properties).length > 0"
                        :schema="renderConfig"
                        :value="inputRenderData">
                    </jsonschema-form>
                    <no-data v-else></no-data>
                </template>
            </div>
            <full-code-editor v-else :value="inputsInfo"></full-code-editor>
        </template>
        <div class="code-block-wrap" v-else-if="isExpand">
            <VueJsonPretty :data="inputsInfo"></VueJsonPretty>
        </div>
    </section>
</template>

<script>
    import VueJsonPretty from 'vue-json-pretty'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import JsonschemaForm from '../../common/JsonschemaForm.vue'
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
                inputRenderData: {},
                isExpand: true
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
            renderData: {
                handler (val) {
                    this.renderKey = new Date().getTime()
                    const renderData = tools.deepClone(val)
                    this.inputRenderData = renderData
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
                    this.inputsInfo = JSON.parse(this.inputsInfo)
                } else {
                    this.inputsInfo = JSON.stringify(this.inputs, null, 4)
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
        border: 1px solid #dcdee5;
        border-bottom: none;
        border-radius: 2px;
        margin: 13px 12px 0;
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
                width: 20%;
            }
        }
        ::v-deep .render-form {
            >.rf-form-item,
            .form-item-group >.rf-form-item {
                margin: 0;
                padding: 5px 0;
                width: 100% !important;
                border-bottom: 1px solid #dcdee5;
                label {
                    width: 20%;
                    text-align: left;
                    padding-left: 13px;
                    color: #63656e;
                    &::before {
                        content: initial;
                    }
                }
                >.rf-tag-form {
                    margin-left: 20%;
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
        ::v-deep .bk-schema-form {
            .bk-form-item {
                margin: 0;
                padding: 5px 0;
                width: 100% !important;
                border-bottom: 1px solid #dcdee5;
                label {
                    width: 20% !important;
                    text-align: left;
                    padding-left: 13px;
                    color: #63656e;
                    &::before {
                        content: initial;
                    }
                }
                >.bk-form-content {
                    margin-left: 20% !important;
                    padding-left: 13px;
                    padding-right: 15px;
                }
                .cell {
                    >.bk-form-item {
                        border: none;
                        .bk-form-content {
                            margin: 0 !important;
                        }
                    }
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
        margin: 13px 12px 0;
    }
</style>
