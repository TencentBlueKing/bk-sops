<template>
    <section class="info-section outputs-section" data-test-id="taskExecute_form_outputParams">
        <div class="section-title-wrap">
            <i
                class="trigger common-icon-next-triangle-shape"
                :class="{ 'is-expand': isExpand }"
                @click="isExpand = !isExpand"></i>
            {{ $t('输出参数') }}
            <div class="origin-value" v-if="isExecuted && !adminView">
                <bk-switcher size="small" @change="outputSwitcher" v-model="isShowOutputOrigin"></bk-switcher>
                {{ 'Code' }}
            </div>
        </div>
        <NoData v-if="!isExecuted && isExpand" :message="$t('暂无输出')"></NoData>
        <template v-else-if="!adminView && isExpand">
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
                        <td
                            v-if="isUrl(output.value) || Array.isArray(output.value)"
                            class="output-value"
                            v-bk-overflow-tips
                            v-html="getOutputValue(output)">
                        </td>
                        <td v-else class="output-value" v-bk-overflow-tips>{{ getOutputValue(output) }}</td>
                    </tr>
                    <tr v-if="Object.keys(outputsInfo).length === 0">
                        <td colspan="3"><no-data></no-data></td>
                    </tr>
                </tbody>
            </table>
            <full-code-editor v-else :value="outputsInfo"></full-code-editor>
        </template>
        <div class="code-block-wrap" v-else-if="isExpand">
            <VueJsonPretty :data="outputsInfo" v-if="outputsInfo"></VueJsonPretty>
            <NoData v-else></NoData>
        </div>
    </section>
</template>

<script>
    import VueJsonPretty from 'vue-json-pretty'
    import NoData from '@/components/common/base/NoData.vue'
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'
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
            },
            isExecuted: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                isShowOutputOrigin: false,
                outputsInfo: null,
                isExpand: true
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
                    return this.filterXSS(JSON.stringify(output.value))
                } else if (Array.isArray(output.value)) {
                    if (!output.value.length) return '--'
                    return output.value.reduce((acc, cur) => {
                        let str = this.filterXSS(cur)
                        if (this.isUrl(cur)) {
                            str = `<a style="color: #3a84ff; word-break: break-all;" target="_blank" href="${cur}">${cur}</a>`
                        }
                        acc = acc ? acc + '</br>' + str : str
                        return acc
                    }, '')
                } else {
                    if (this.isUrl(output.value)) {
                        return `<a style="color: #3a84ff; word-break: break-all;" target="_blank" href="${output.value}">${output.value}</a>`
                    }
                    return this.filterXSS(JSON.stringify(output.value))
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .outputs-section .operation-table {
        flex: 1;
        table-layout: fixed;
        width: calc(100% - 24px);
        margin: 13px 12px 0;
        th, td {
            width: 30%;
            padding: 16px 13px;
            font-weight: normal;
            color: #313238;
            background: #f5f7fa;
            border: none;
            border-bottom: 1px solid #dcdee5;
        }
        td {
            color: #63656e;
            background: #fff;
        }
        .output-value {
            width: 50%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            word-break: break-all;
        }
    }
    .outputs-section .full-code-editor {
        height: 400px;
        margin: 13px 12px 0;
    }
    .no-data-wrapper {
        margin-top: 32px;
    }
</style>
