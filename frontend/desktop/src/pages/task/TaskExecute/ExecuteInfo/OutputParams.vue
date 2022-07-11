<template>
    <section class="info-section" data-test-id="taskExecute_form_outputParams">
        <div class="common-section-title output-parameter">
            <div class="output-title">{{ $t('输出参数') }}</div>
            <div class="origin-value" v-if="!adminView">
                <bk-switcher @change="outputSwitcher" v-model="isShowOutputOrigin"></bk-switcher>
                {{ $t('原始值') }}
            </div>
        </div>
        <div v-if="!adminView">
            <table class="operation-table outputs-table" v-if="!isShowOutputOrigin">
                <thead>
                    <tr>
                        <th class="output-name">{{ $t('参数名') }}</th>
                        <th class="output-value">{{ $t('参数值') }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="output in outputsInfo" :key="output.name">
                        <td class="output-name">{{ getOutputName(output) }}</td>
                        <td v-if="isUrl(output.value)" class="output-value" v-html="getOutputValue(output)"></td>
                        <td v-else class="output-value">{{ getOutputValue(output) }}</td>
                    </tr>
                    <tr v-if="Object.keys(outputsInfo).length === 0">
                        <td colspan="2"><no-data></no-data></td>
                    </tr>
                </tbody>
            </table>
            <full-code-editor v-else :value="outputsInfo"></full-code-editor>
        </div>
        <div class="code-block-wrap" v-else>
            <VueJsonPretty :data="outputsInfo" v-if="outputsInfo"></VueJsonPretty>
            <NoData v-else></NoData>
        </div>
    </section>
</template>

<script>
    import VueJsonPretty from 'vue-json-pretty'
    import NoData from '@/components/common/base/NoData.vue'
    import FullCodeEditor from '../FullCodeEditor.vue'
    import { URL_REG } from '@/constants/index.js'
    import tools from '@/utils/tools.js'
    export default {
        components: {
            VueJsonPretty,
            NoData,
            FullCodeEditor
        },
        props: {
            adminView: {
                type: Boolean,
                default: false
            },
            outputs: {
                type: Array,
                default: () => ([])
            },
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                isShowOutputOrigin: false,
                outputsInfo: null
            }
        },
        watch: {
            outputs: {
                handler (val) {
                    this.outputsInfo = tools.deepClone(val)
                },
                immediate: true
            }
        },
        methods: {
            outputSwitcher () {
                if (!this.isShowOutputOrigin) {
                    this.outputsInfo = JSON.parse(this.outputsInfo)
                } else {
                    this.outputsInfo = JSON.stringify(this.outputsInfo, null, 4)
                }
            },
            getOutputName (output) {
                if (this.nodeDetailConfig.component_code === 'job_execute_task' && output.perset) {
                    return output.key
                }
                return output.name
            },
            isUrl (val) {
                return typeof val === 'string' && URL_REG.test(val)
            },
            getOutputValue (output) {
                if (output.value === 'undefined' || output.value === '') {
                    return '--'
                } else if (!output.preset && this.nodeDetailConfig.component_code === 'job_execute_task') {
                    return output.value
                } else {
                    if (this.isUrl(output.value)) {
                        return `<a class="info-link" target="_blank" href="${output.value}">${output.value}</a>`
                    }
                    return output.value
                }
            }
        }
    }
</script>

<style>

</style>