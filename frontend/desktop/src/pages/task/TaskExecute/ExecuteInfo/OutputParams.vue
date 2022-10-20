<template>
    <section class="info-section outputs-section" data-test-id="taskExecute_form_outputParams">
        <h4 class="outputs-label">{{ $t('输出参数') }}</h4>
        <div class="origin-value" v-if="!adminView">
            <bk-switcher size="small" @change="outputSwitcher" v-model="isShowOutputOrigin"></bk-switcher>
            {{ $t('原始值') }}
        </div>
        <template v-if="!adminView">
            <table class="operation-table outputs-table" v-if="!isShowOutputOrigin">
                <thead>
                    <tr>
                        <th class="output-name">{{ $t('参数名') }}</th>
                        <th class="output-key">{{ $t('参数Key') }}</th>
                        <th class="output-value">{{ $t('参数值') }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(output, index) in outputsInfo" :key="index">
                        <td class="output-name">{{ getOutputName(output) }}</td>
                        <td class="output-key">{{ output.key }}</td>
                        <td v-if="isUrl(output.value) || Array.isArray(output.value)" class="output-value" v-html="getOutputValue(output)"></td>
                        <td v-else class="output-value">{{ getOutputValue(output) }}</td>
                    </tr>
                    <tr v-if="Object.keys(outputsInfo).length === 0">
                        <td colspan="3"><no-data></no-data></td>
                    </tr>
                </tbody>
            </table>
            <full-code-editor v-else :value="outputsInfo"></full-code-editor>
        </template>
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
                } else if (Array.isArray(output.value)) {
                    if (!output.value.length) return '--'
                    return output.value.reduce((acc, cur) => {
                        let str = cur
                        if (this.isUrl(cur)) {
                            str = `<a class="info-link" target="_blank" href="${cur}">${cur}</a>`
                        }
                        acc = acc ? acc + ',' + str : str
                        return acc
                    }, '')
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

<style lang="scss" scoped>
    .outputs-section {
        display: flex;
        position: relative;
    }
    .outputs-section .operation-table {
        flex: 1;
        margin-left: 24px;
        padding-top: 18px;
        border: none;
        border-collapse: initial;
        th, td {
            width: 30%;
            padding: 16px 13px;
            color: #313238;
            background: #f5f7fa;
            border: none;
            border-bottom: 1px solid #dcdee5;
        }
        td {
            color: #63656e;
        }
        .output-value {
            width: 50%;
        }
    }
</style>
