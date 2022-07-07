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
                <RenderForm
                    v-if="!isEmptyParams && !loading"
                    :scheme="renderConfig"
                    :form-option="renderOption"
                    v-model="inputRenderDate">
                </RenderForm>
                <NoData v-else></NoData>
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
    import FullCodeEditor from '../FullCodeEditor.vue'
    import tools from '@/utils/tools.js'
    export default {
        components: {
            VueJsonPretty,
            NoData,
            RenderForm,
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
            renderData: {
                handler (val) {
                    this.inputRenderDate = tools.deepClone(val)
                },
                immediate: true
            }
        },
        methods: {
            inputSwitcher () {
                if (!this.isShowInputOrigin) {
                    this.inputsInfo = JSON.parse(this.inputsInfo)
                } else {
                    this.inputsInfo = JSON.stringify(this.inputsInfo, null, 4)
                }
            }
        }
    }
</script>

<style>

</style>
