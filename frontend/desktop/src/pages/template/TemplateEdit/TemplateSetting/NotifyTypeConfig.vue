<template>
    <div class="notify-type-wrapper">
        <bk-form
            ref="notifyConfigForm"
            class="notify-form-area"
            :model="formData"
            :label-width="labelWidth"
            :rules="rules">
            <bk-form-item property="notifyType" :label="notifyTypeLabel" data-test-id="notifyTypeConfig_form_notifyType">
                <bk-table
                    class="notify-type-table"
                    :style="{ width: tableWidth ? `${tableWidth}px` : '100%' }"
                    :data="formData.notifyType"
                    :col-border="true"
                    v-bkloading="{ isLoading: notifyTypeLoading, opacity: 1, zIndex: 100 }">
                    <bk-table-column
                        v-for="(col, index) in allNotifyTypeList"
                        :key="index"
                        :fixed="col.type ? false : 'left'"
                        :min-width="col.type === 'bkchat' ? 300 : 85"
                        :render-header="getNotifyTypeHeader">
                        <template slot-scope="{ row, $index }">
                            <template v-if="col.type">
                                <bk-checkbox
                                    :disabled="isViewMode"
                                    :value="row.includes(col.type)"
                                    @change="onSelectNotifyType($index, col.type, $event)">
                                </bk-checkbox>
                                <bk-input
                                    v-if="col.type === 'bkchat'"
                                    :name="`chat_group_id_${$index}`"
                                    :class="['ml10', { 'vee-error': veeErrors.has(`chat_group_id_${$index}`) }]"
                                    v-validate="{ required: row.includes(col.type) }"
                                    :disabled="isViewMode || !row.includes(col.type)"
                                    :placeholder="$t('请输入群 ID，多个 ID 以逗号隔开')"
                                    :value="getChatNotifyTypeValue($index)"
                                    @change="onChatNotifyTypeChange($index, $event)">
                                </bk-input>
                                <span
                                    v-if="col.type === 'bkchat' && veeErrors.has(`chat_group_id_${$index}`)"
                                    v-bk-tooltips="veeErrors.first(`chat_group_id_${$index}`)"
                                    class="bk-icon icon-exclamation-circle-shape error-msg" />
                            </template>
                            <span v-else>{{ $index === 0 ? $t('成功') : $t('失败') }}</span>
                        </template>
                        <div class="empty-data" slot="empty">
                            <NoData></NoData>
                        </div>
                    </bk-table-column>
                </bk-table>
            </bk-form-item>
            <!-- AI分析通知 -->
            <bk-form-item v-if="enableAiNotification && isTemplateConfig"
                property="aiAnalysisNotifyPerson"
                :label="$t('AI分析通知')"
                data-test-id="notifyTypeConfig_form_aiAnalysisNotifyPerson">
                <bk-table
                    class="ai-analysis-table"
                    :data="formData.aiAnalysisNotifyPerson"
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

            <bk-form-item property="notifyGroup" :label="notifyGroupLabel" data-test-id="notifyTypeConfig_form_notifyGroup">
                <bk-checkbox-group
                    class="bk-checkbox-group"
                    :value="formData.receiverGroup"
                    v-bkloading="{ isLoading: notifyGroupLoading, opacity: 1, zIndex: 100 }"
                    @change="onReceiverGroup">
                    <bk-checkbox
                        v-for="item in notifyGroup"
                        :key="item.id"
                        :disabled="isViewMode"
                        :value="item.id">
                        {{item.name}}
                    </bk-checkbox>
                </bk-checkbox-group>
            </bk-form-item>
            
            <!-- AI分析群聊通知 -->
            <bk-form-item v-if="enableAiNotification && isTemplateConfig"
                property="aiAnalysisNotifyPersonGroup"
                :label="$t('AI分析群聊通知')"
                data-test-id="notifyTypeConfig_form_aiAnalysisNotifyPersonGroup">
                <bk-table
                    class="ai-chat-notify-table"
                    :data="formData.aiAnalysisNotifyPersonGroup"
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
                        prop="ai_analysis_notify_group_chat_id"
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
                                v-bk-tooltips="{ content: row.ai_analysis_notify_group_chat_id }"
                                :value="row.ai_analysis_notify_group_chat_id"
                                @change="onAiChatConfigChange($index, 'ai_analysis_notify_group_chat_id', $event)">
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
    import { mapState, mapActions, mapMutations } from 'vuex'
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'
    
    export default {
        components: {
            NoData
        },
        props: {
            notifyTypeLabel: {
                type: String,
                default: i18n.t('通知方式')
            },
            notifyGroupLabel: {
                type: String,
                default: i18n.t('通知分组')
            },
            notifyType: {
                type: Array,
                default: () => [[]]
            },
            notifyTypeList: {
                type: Array,
                default: () => []
            },
            notifyTypeExtraInfo: {
                type: Object,
                default: () => ({})
            },
            receiverGroup: {
                type: Array,
                default: () => []
            },
            aiAnalysisNotifyPerson: {
                type: Object,
                default: () => ({})
            },
            aiAnalysisNotifyPersonGroup: {
                type: Object,
                default: () => ({})
            },
            tableWidth: {
                type: Number,
                default: 0
            },
            labelWidth: {
                type: Number,
                default: 100
            },
            rules: {
                type: Object,
                default: () => ({})
            },
            common: [String, Number],
            isViewMode: {
                type: Boolean,
                default: false
            },
            project_id: [String, Number],
            isTemplateConfig: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const formatNotifyPerson = []
            const formatNotifyGroup = []
            for (const key in tools.deepClone(this.aiAnalysisNotifyPerson)) {
                const item = {}
                item.key = key
                item.value = this.aiAnalysisNotifyPerson[key]
                formatNotifyPerson.push(item)
            }
            if (formatNotifyPerson.length === 0) {
                formatNotifyPerson.push(
                    { key: 'success', value: [] },
                    { key: 'fail', value: [] }
                )
            }
            for (const key in tools.deepClone(this.aiAnalysisNotifyPersonGroup)) {
                const item = { ...this.aiAnalysisNotifyPersonGroup[key] }
                item.type = key
                formatNotifyGroup.push(item)
            }
            if (formatNotifyGroup.length === 0) {
                formatNotifyGroup.push(
                    {
                        type: 'success',
                        ai_analysis_notify_group_chat_id: '',
                        web_hook: '',
                        mentioned_member_list: ''
                    },
                    {
                        type: 'fail',
                        ai_analysis_notify_group_chat_id: '',
                        web_hook: '',
                        mentioned_member_list: ''
                    }
                )
            }
            const formData = {
                notifyType: tools.deepClone(this.notifyType),
                notifyTypeExtraInfo: tools.deepClone(this.notifyTypeExtraInfo),
                receiverGroup: tools.deepClone(this.receiverGroup),
                aiAnalysisNotifyPerson: formatNotifyPerson,
                aiAnalysisNotifyPersonGroup: formatNotifyGroup
            }
            return {
                formData,
                notifyTypeLoading: false,
                allNotifyTypeList: [],
                aiNotifyList: [], // ai分析通知类型
                notifyGroupLoading: false,
                projectNotifyGroup: [],
                aiAnalysisLoading: false,
                enableAiNotification: window.ENABLE_AI_NOTIFICATION
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo
            }),
            notifyGroup () {
                let list = []
                if (this.projectBaseInfo.notify_group) {
                    const defaultList = list.concat(this.projectBaseInfo.notify_group.map(item => {
                        return {
                            id: item.value,
                            name: item.text
                        }
                    }))
                    list = defaultList.concat(this.projectNotifyGroup)
                }
                return list
            }
        },
        created () {
            this.getNotifyTypeList()
            if (!this.common) {
                this.getProjectNotifyGroup()
            }
        },
        methods: {
            ...mapActions([
                'getNotifyTypes',
                'getNotifyGroup'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            async getNotifyTypeList () {
                try {
                    this.notifyTypeLoading = true
                    const res = await this.getNotifyTypes()
                    this.allNotifyTypeList = [].concat(this.notifyTypeList, res.data)
                    this.aiNotifyList = [{ text: i18n.t('任务状态') }]
                    const compannyWechat = this.allNotifyTypeList.filter(item => item.type === 'rtx')
                    if (compannyWechat) {
                        this.aiNotifyList.push(...compannyWechat)
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.notifyTypeLoading = false
                }
            },
            getNotifyTypeHeader (h, data) {
                const col = this.allNotifyTypeList[data.$index]
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
                        ]),
                        col.tips ? h('i', {
                            class: 'bk-icon icon-exclamation-circle ml5',
                            style: { 'font-size': '14px' },
                            directives: [{
                                name: 'bk-tooltips',
                                value: { content: col.tips, allowHTML: true }
                            }]
                        }) : ''
                    ])
                } else {
                    return h('p', {
                        class: 'label-text',
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [
                        col.text
                    ])
                }
            },
            getAiAnalysisTypeHeader (h, data) {
                const col = this.aiNotifyList[data.$index]
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
                        ]),
                        col.tips ? h('i', {
                            class: 'bk-icon icon-exclamation-circle ml5',
                            style: { 'font-size': '14px' },
                            directives: [{
                                name: 'bk-tooltips',
                                value: { content: col.tips, allowHTML: true }
                            }]
                        }) : ''
                    ])
                } else {
                    return h('p', {
                        class: 'label-text',
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [
                        col.text
                    ])
                }
            },
            getChatNotifyTypeValue (index) {
                const { notifyTypeExtraInfo } = this.formData
                if (!notifyTypeExtraInfo.bkchat) {
                    notifyTypeExtraInfo.bkchat = { success: '', fail: '' }
                }
                return notifyTypeExtraInfo.bkchat[index === 0 ? 'success' : 'fail']
            },
            onChatNotifyTypeChange (index, val) {
                const { bkchat } = this.formData.notifyTypeExtraInfo
                bkchat[index === 0 ? 'success' : 'fail'] = val
                this.$emit('change', this.formData)
            },
            onSelectNotifyType (row, type, val) {
                const data = this.formData.notifyType[row]
                if (val) {
                    data.push(type)
                } else {
                    const index = data.findIndex(item => item === type)
                    if (index > -1) {
                        data.splice(index, 1)
                    }
                }
                // bkchat同时方式取消勾选时需要情况群id
                if (!val && type === 'bkchat') {
                    const { bkchat } = this.formData.notifyTypeExtraInfo
                    bkchat[row === 0 ? 'success' : 'fail'] = ''
                }
                this.$emit('change', this.formData)
            },
            onSelectAiAnalysisType (row, type, val) {
                const data = this.formData.aiAnalysisNotifyPerson[row]
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
                this.formData.aiAnalysisNotifyPersonGroup[index][field] = value
                this.$emit('change', this.formData)
            },
            onReceiverGroup (val) {
                this.formData.receiverGroup = val
                this.$emit('change', this.formData)
            },
            async getProjectNotifyGroup () {
                try {
                    this.notifyGroupLoading = true
                    if (!this.projectBaseInfo.notify_group) {
                        const resp = await this.loadProjectBaseInfo()
                        this.setProjectBaseInfo(resp.data)
                    }
                    const res = await this.getNotifyGroup({ project_id: this.project_id })
                    this.projectNotifyGroup = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.notifyGroupLoading = false
                }
            },
            // 校验
            validate () {
                return this.$validator.validateAll().then(valid => valid)
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import "@/scss/config.scss";
    @import '@/scss/mixins/scrollbar.scss';
    .notify-type {
        width: 100%;
    }
    .bk-form-checkbox {
        margin-right: 20px;
        margin-top: 6px;
        min-width: 96px;
        ::v-deep .bk-checkbox-text {
            color: $greyDefault;
            font-size: 12px;
        }
        &.is-disabled ::v-deep .bk-checkbox-text {
            color: #c4c6cc;
        }
        &.is-checked ::v-deep .bk-checkbox-text  {
            color: #606266;
        }
    }
    ::v-deep .bk-checkbox-text {
        display: inline-flex;
        align-items: center;
        width: 100px;
    }
    // 表格样式
    .notify-type-table,
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
                .bk-form-checkbox {
                    margin: 0;
                    min-width: 0;
                    flex-shrink: 0;
                }
                
                .table-input {
                    width: 100%;
                }
            }
            .vee-error .bk-textarea-wrapper {
                border-color: #ea3636;
            }
            .error-msg {
                font-size: 14px;
                margin-left: -14px;
                transform: translateX(-10px);
                color: #ea3636;
            }
        }
    }
    
    // AI分析通知样式
    .ai-analysis-item {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        
        .analysis-method {
            font-size: 12px;
            color: #63656e;
            margin-right: 16px;
            min-width: 60px;
        }
        
        .analysis-icons {
            display: flex;
            gap: 8px;
            
            .icon-item {
                display: flex;
                align-items: center;
                gap: 4px;
                padding: 4px 8px;
                background: #f0f1f5;
                border-radius: 2px;
                
                .bk-icon {
                    font-size: 14px;
                    color: #3a84ff;
                }
                
                span {
                    font-size: 12px;
                    color: #63656e;
                }
            }
        }
    }

</style>
