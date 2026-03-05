<template>
    <div class="ai-analysis-notify-wrapper">
        <bk-form
            ref="aiAnalysisForm"
            class="ai-analysis-form-area"
            :model="formData"
            :label-width="labelWidth"
            :rules="rules">
            <!-- AI分析通知 -->
            <bk-form-item
                property="aiAnalysisNotifyType"
                :label="$t('执行者通知')"
                data-test-id="aiAnalysisNotifyConfig_form_aiAnalysisNotifyType">
                <bk-table
                    class="ai-analysis-table"
                    :data="formData.aiAnalysisNotifyType"
                    :col-border="true"
                    v-bkloading="{ isLoading: aiAnalysisLoading, opacity: 1, zIndex: 100 }">
                    <bk-table-column
                        v-for="(col, index) in aiNotifyList"
                        :key="index"
                        :min-width="85"
                        :render-header="getAiAnalysisTypeHeader">
                        <template slot-scope="{ row , $index }">
                            <template v-if="col.type">
                                <bk-checkbox
                                    :disabled="isViewMode"
                                    :value="row.value.includes(col.type)"
                                    @change="onSelectAiAnalysisType($index, col.type, $event)">
                                </bk-checkbox>
                            </template>
                            <span v-else>{{ row.key === 'success' ? $t('成功') : $t('失败') }}</span>
                        </template>
                    </bk-table-column>
                </bk-table>
            </bk-form-item>

            <!-- AI分析群聊通知 -->
            <bk-form-item
                property="aiAnalysisNotifyGroup"
                :label="$t('群聊通知')"
                data-test-id="aiAnalysisNotifyConfig_form_aiAnalysisNotifyGroup">
                <bk-table
                    class="ai-chat-notify-table"
                    :data="formData.aiAnalysisNotifyGroup"
                    :col-border="true"
                    :outer-border="true"
                    v-bkloading="{ isLoading: aiAnalysisLoading, opacity: 1, zIndex: 100 }">
                    <bk-table-column
                        prop="type"
                        :label="$t('状态')"
                        width="80"
                        fixed="left">
                        <template slot-scope="{ row }">
                            <span class="status-text">{{ row.type === 'success' ? $t('成功') : $t('失败') }}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column
                        prop="chat_id"
                        :label="$t('群聊ID')"
                        min-width="200">
                        <template slot-scope="{ row, $index }">
                            <bk-input
                                class="table-input"
                                :placeholder="$t('请输入群聊ID')"
                                :disabled="isViewMode"
                                :maxlength="32"
                                :clearable="true"
                                :show-word-limit="true"
                                type="text"
                                v-bk-tooltips="{ content: row.chat_id }"
                                :value="row.chat_id"
                                @change="onAiChatConfigChange($index, 'chat_id', $event)">
                            </bk-input>
                        </template>
                    </bk-table-column>
                    <bk-table-column
                        prop="web_hook"
                        label="Webhook"
                        min-width="300">
                        <template slot-scope="{ row, $index }">
                            <bk-input
                                class="table-input"
                                :placeholder="$t('请输入群聊机器人webhook')"
                                :disabled="isViewMode"
                                v-bk-tooltips="{ content: row.web_hook }"
                                :clearable="true"
                                :value="row.web_hook"
                                @change="onAiChatConfigChange($index, 'web_hook', $event)">
                            </bk-input>
                        </template>
                    </bk-table-column>
                    <bk-table-column
                        prop="mentioned_member_list"
                        :label="$t('需要@的人')"
                        min-width="200">
                        <template slot-scope="{ row, $index }">
                            <bk-input
                                class="table-input"
                                :placeholder="$t('请输入需要@的人')"
                                :disabled="isViewMode"
                                v-bk-tooltips="{ content: row.mentioned_member_list }"
                                :clearable="true"
                                :value="row.mentioned_member_list"
                                @change="onAiChatConfigChange($index, 'mentioned_member_list', $event)">
                            </bk-input>
                        </template>
                    </bk-table-column>
                </bk-table>
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'

    export default {
        name: 'AiAnalysisNotifyConfig',
        props: {
            aiAnalysisNotifyType: {
                type: Object,
                default: () => ({})
            },
            aiAnalysisNotifyGroup: {
                type: Object,
                default: () => ({})
            },
            notifyTypeList: {
                type: Array,
                default: () => []
            },
            labelWidth: {
                type: Number,
                default: 100
            },
            rules: {
                type: Object,
                default: () => ({})
            },
            isViewMode: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const formatNotifyPerson = []
            const formatNotifyGroup = []
            const notifyTypeClone = tools.deepClone(this.aiAnalysisNotifyType)
            const keys = Object.keys(notifyTypeClone)
            
            // 确保 success 始终在数组第一位
            if (keys.includes('success')) {
                formatNotifyPerson.push({
                    key: 'success',
                    value: notifyTypeClone.success
                })
            }
            for (const key of keys) {
                if (key !== 'success') {
                    const item = {}
                    item.key = key
                    item.value = notifyTypeClone[key]
                    formatNotifyPerson.push(item)
                }
            }
            
            if (formatNotifyPerson.length === 0) {
                formatNotifyPerson.push(
                    { key: 'success', value: [] },
                    { key: 'fail', value: [] }
                )
            }
            
            const notifyGroupClone = tools.deepClone(this.aiAnalysisNotifyGroup)
            const groupKeys = Object.keys(notifyGroupClone)
            
            // 确保 success 始终在数组第一位
            if (groupKeys.includes('success')) {
                const item = { ...notifyGroupClone.success }
                item.type = 'success'
                formatNotifyGroup.push(item)
            }
            for (const key of groupKeys) {
                if (key !== 'success') {
                    const item = { ...notifyGroupClone[key] }
                    item.type = key
                    formatNotifyGroup.push(item)
                }
            }
            
            if (formatNotifyGroup.length === 0) {
                formatNotifyGroup.push(
                    {
                        type: 'success',
                        chat_id: '',
                        web_hook: '',
                        mentioned_member_list: ''
                    },
                    {
                        type: 'fail',
                        chat_id: '',
                        web_hook: '',
                        mentioned_member_list: ''
                    }
                )
            }
            
            const formData = {
                aiAnalysisNotifyType: formatNotifyPerson,
                aiAnalysisNotifyGroup: formatNotifyGroup
            }
            
            return {
                formData,
                aiNotifyList: [],
                aiAnalysisLoading: false
            }
        },
        watch: {
            notifyTypeList: {
                handler (val) {
                    if (val && val.length > 0) {
                        this.initAiNotifyList()
                    }
                },
                immediate: true
            }
        },
        methods: {
            initAiNotifyList () {
                this.aiNotifyList = [{ text: i18n.t('任务状态') }]
                const companyWechat = this.notifyTypeList.filter(item => item.type === 'rtx')
                if (companyWechat.length > 0) {
                    this.aiNotifyList.push(...companyWechat)
                }
            },
            getAiAnalysisTypeHeader (h, data) {
                const col = this.aiNotifyList[data.$index]
                if (!col) {
                    return null
                }
                if (col.type) {
                    return h('div', { 'class': 'notify-table-heder' }, [
                        h('img', { 'class': 'notify-icon', attrs: { src: `data:image/png;base64,${col.icon}` } }, []),
                        h('p', {
                            class: 'label-text',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [
                            col.label
                        ])
                    ])
                } else {
                    return h('p', {
                        class: 'label-text',
                        style: {
                            textAlign: 'center',
                            margin: 0
                        },
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [
                        col.text
                    ])
                }
            },
            onSelectAiAnalysisType (row, type, val) {
                const data = this.formData.aiAnalysisNotifyType[row]
                if (val) {
                    if (!data.value.includes(type)) {
                        data.value.push(type)
                    }
                } else {
                    const index = data.value.findIndex(item => item === type)
                    if (index > -1) {
                        data.value.splice(index, 1)
                    }
                }
                this.$emit('change', this.formData)
            },
            onAiChatConfigChange (index, field, value) {
                this.formData.aiAnalysisNotifyGroup[index][field] = value
                this.$emit('change', this.formData)
            },
            validate () {
                return this.$validator.validateAll().then(valid => valid)
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import "@/scss/config.scss";
    @import '@/scss/mixins/scrollbar.scss';
    
    .ai-analysis-notify-wrapper {
        width: 100%;
    }
    
    // 表格样式
    .ai-analysis-table,
    .ai-chat-notify-table {
        min-height: 86px;
        ::v-deep .bk-table-header-label {
            width: 100%;

            .notify-table-heder,
            .ai-analysis-table-header {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
                
                .notify-icon {
                    margin-right: 4px;
                    width: 18px;
                }
            }
        }
        ::v-deep .bk-table-fixed {
            height: 100% !important;
        }
        ::v-deep .bk-table-body-wrapper {
            @include scrollbar;
            .cell {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 6px 15px;
                
                .table-input {
                    width: 100%;
                }
            }
        }
    }
</style>
