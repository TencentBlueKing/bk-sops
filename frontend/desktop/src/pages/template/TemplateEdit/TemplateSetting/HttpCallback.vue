<template>
    <div :class="['http-callback-wrapper', { 'is-task-setting': !isViewMode }]">
        <div class="http-callaback-switch">
            <span>{{$t('是否开启')}}</span>
            <bk-switcher
                v-model="isEnable"
                :disabled="isViewMode"
                @change="onEnableWebhookChange">
            </bk-switcher>
        </div>
        <div class="http-callback-address">
            <bk-form :rules="addrFormRules" ref="addrForm" :model="localWebhookForm">
                <bk-form-item property="method" :icon-offset="8" :label-width="0" class="form-item-select">
                    <bk-select
                        :disabled="isViewMode"
                        v-model="localWebhookForm.method"
                        ext-cls="select-custom"
                        behavior="simplicity"
                        ext-popover-cls="select-popover-custom"
                        class="http-callback-method-select"
                        @change="onWebhookConfigChange">
                        <bk-option v-for="option in methodList"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name"
                            :disabled="option.isDisabled">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item property="endpoint" :icon-offset="8" :label-width="0">
                    <bk-input behavior="simplicity"
                        :disabled="isViewMode"
                        :clearable="true"
                        v-model="localWebhookForm.endpoint"
                        :placeholder="$t('输入请求URL')"
                        class="http-callback-url-input"
                        @change="onWebhookConfigChange">
                    </bk-input>
                </bk-form-item>
            </bk-form>
        </div>
        <div class="http-callback-request-params">
            <bk-icon type="up-shape" class="triangle" />
            <bk-tab
                :active.sync="activeTab"
                type="unborder-card"
                @tab-change="requestTypetabChange">
                <bk-tab-panel name="params">
                    <template slot="label">
                        <span class="panel-name disabled-tab-name">{{$t('回调内容示例')}}</span>
                    </template>
                    <div style="height: 300px">
                        <full-code-editor
                            class="scroll-editor"
                            :value="callbackExample">
                        </full-code-editor>
                    </div>
                </bk-tab-panel>
                <bk-tab-panel name="authentication" :render-label="renderLabel">
                    <bk-radio-group
                        v-model="localWebhookForm.extra_info.authorization.type"
                        @change="onAuthConfigChange"
                    >
                        <bk-radio value="" :disabled="isViewMode">{{$t('无需认证')}}</bk-radio>
                        <bk-radio value="bearer" :disabled="isViewMode">Bearer Token</bk-radio>
                        <bk-radio value="basic" :disabled="isViewMode">Basic Auth</bk-radio>
                    </bk-radio-group>
                    <div class="auth-bearer-info"
                        v-if="localWebhookForm.extra_info.authorization.type === 'bearer'">
                        <bk-form form-type="vertical" :rules="tokenFormRules" ref="tokenForm" :model="localWebhookForm.extra_info.authorization">
                            <bk-form-item label="Token" property="token" :icon-offset="15" :label-width="500">
                                <bk-input v-model="localWebhookForm.extra_info.authorization.token"
                                    behavior="simplicity"
                                    :disabled="isViewMode"
                                    :clearable="true"
                                    @change="onWebhookConfigChange">
                                </bk-input>
                            </bk-form-item>
                        </bk-form>
                    </div>
                    <div class="auth-basic-info"
                        v-if="localWebhookForm.extra_info.authorization.type === 'basic'">
                        <bk-form form-type="vertical" :rules="basicFormRules" ref="basicForm" :model="localWebhookForm.extra_info.authorization">
                            <bk-form-item :label="$t('用户名')" property="username" :icon-offset="15" :label-width="300">
                                <div class="from-item-content">
                                    <bk-input v-model="localWebhookForm.extra_info.authorization.username"
                                        behavior="simplicity"
                                        :disabled="isViewMode"
                                        :clearable="true"
                                        @change="onWebhookConfigChange">
                                    </bk-input>
                                </div>
                            </bk-form-item>
                            <bk-form-item :label="$t('密码')" property="password" :icon-offset="15" :label-width="300">
                                <div class="from-item-content">
                                    <bk-input v-model="localWebhookForm.extra_info.authorization.password"
                                        behavior="simplicity"
                                        type="password"
                                        :disabled="isViewMode"
                                        :clearable="true"
                                        @change="onWebhookConfigChange">
                                    </bk-input>
                                </div>
                            </bk-form-item>
                        </bk-form>
                    </div>
                </bk-tab-panel>
                <bk-tab-panel name="headers" :render-label="renderLabel">
                    <bk-table style="margin-top: 15px;"
                        :data="localWebhookForm.extra_info.headers">
                        <bk-table-column v-for="item in headerFields" :key="item.id" :label="item.name">
                            <template slot-scope="{ row }">
                                <bk-input v-model="row[headerFieldConfig[item.id]]"
                                    behavior="simplicity"
                                    :disabled="isViewMode"
                                    :clearable="true"
                                    @change="onWebhookConfigChange">
                                </bk-input>
                            </template>
                        </bk-table-column>
                        <bk-table-column label="操作" width="80">
                            <template slot-scope="props">
                                <bk-button theme="primary" text @click="delItemHeader(props.row,props.$index)" :disabled="isViewMode">删除</bk-button>
                            </template>
                        </bk-table-column>
                        <template slot="append">
                            <div class="header-table-bottom">
                                <div @click="isViewMode ? null : addHeadersRow()" :class="['add-header', { 'add-header-disabled': isViewMode }]">
                                    <bk-icon type="plus" />
                                </div>
                            </div>
                        </template>
   
                    </bk-table>
                </bk-tab-panel>
                <bk-tab-panel name="settings" :render-label="renderLabel">
                    <bk-form form-type="vertical" :rules="settingFormRules" ref="settingForm" :model="localWebhookForm.extra_info">
                        <bk-form-item v-for="item in settingFieldConfig" :key="item.key" :label="item.label" :property="item.key" :icon-offset="27">
                            <div class="from-item-content">
                                <bk-input v-model="localWebhookForm.extra_info[item.key]"
                                    :disabled="isViewMode"
                                    @change="onWebhookConfigChange">
                                </bk-input>
                                <span class="unit" v-if="item.key !== 'retry_times'">s</span>
                                <span class="unit" v-else>{{$t('次')}}</span>

                            </div>
                        </bk-form-item>
                    </bk-form>
                </bk-tab-panel>
            </bk-tab>
        </div>
        <div class="debug-btn">
            <bk-button theme="primary" :outline="true"
                @click="debugMock"
                :disabled="isViewMode || !localWebhookForm.method || !localWebhookForm.endpoint">
                {{$t('调试')}}
            </bk-button>
        </div>
    </div>

</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'
    import { mapActions } from 'vuex'

    export default {
        components: {
            FullCodeEditor
        },
        props: {
            webhookData: {
                type: Object,
                default: () => ({})
            },
            isViewMode: {
                type: Boolean,
                default: false
            },
            enableWebhook: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const defaultWebhookForm = {
                method: 'POST',
                endpoint: '',
                extra_info: {
                    authorization: {
                        type: '',
                        token: '',
                        username: '',
                        password: ''
                    },
                    headers: [
                        {
                            key: '',
                            value: '',
                            desc: ''
                        }
                    ],
                    timeout: 10,
                    retry_times: 2,
                    interval: 5
                }
            }
            const sourceExtraInfo = this.webhookData?.extra_info ? tools.deepClone(this.webhookData.extra_info) : defaultWebhookForm.extra_info
            const { authorization, headers, timeout, retry_times, interval } = sourceExtraInfo
            const localWebhookForm = {
                method: this.webhookData.method || defaultWebhookForm.method,
                endpoint: this.webhookData.endpoint || defaultWebhookForm.endpoint,
                extra_info: {
                    authorization,
                    headers,
                    timeout,
                    retry_times,
                    interval
                }
            }
            const successExample = {
                'executor': 'user',
                'finish_time': 1756459237,
                'outputs': {
                    '${_result}': true,
                    '${test}': '123'
                },
                'start_time': 1756459237,
                'task_id': 109,
                'task_name': 'new20250814161131_20250829172031'
            }
            const errorExample = {
                'executor': 'user',
                'extra_data': {
                    'failed_message': '仅允许访问域名(.)下的URL',
                    'failed_node': 'nccda40ad8b1378eba49351a60a48b87',
                    'failed_node_name': 'HTTP 请求'
                },
                'finish_time': '',
                'start_time': 1756463165,
                'task_id': 118,
                'task_name': 'new20250814161131_20250829182603'
            }
            const callbackExample = `# 成功\n${JSON.stringify(successExample, null, 2)}\n\n# 失败\n${JSON.stringify(errorExample, null, 2)}`
            return {
                callbackExample,
                localWebhookForm,
                isEnable: this.enableWebhook,
                methodList: [
                    {
                        id: 'POST',
                        key: 'POST',
                        name: 'POST',
                        isDisabled: false
                    },
                    {
                        id: 'GET',
                        key: 'GET',
                        name: 'GET',
                        isDisabled: true
                    }
                ],
                headerFields: [
                    {
                        id: 'fieldName',
                        name: i18n.t('字段名')
                    },
                    {
                        id: 'value',
                        name: i18n.t('值')
                    },
                    {
                        id: 'desc',
                        name: i18n.t('描述')
                    }
                ],
                headerFieldConfig: {
                    fieldName: 'key',
                    value: 'value',
                    desc: 'desc'
                },
                settingFieldConfig: [
                    {
                        label: i18n.t('请求超时'),
                        key: 'timeout'
                    },
                    {
                        label: i18n.t('重试间隔'),
                        key: 'interval'
                    },
                    {
                        label: i18n.t('重试次数'),
                        key: 'retry_times'
                    }
                ],
                activeTab: 'authentication',
                settingFormRules: {
                    retry_times: [
                        {
                            validator: this.checkInterval,
                            message: i18n.t('重试次数不能超过5次'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                return this.checkData(val, true)
                            },
                            message: i18n.t('请输入重试次数'),
                            trigger: 'blur'
                        }
                    ],
                    timeout: [
                        {
                            validator: (val) => {
                                return this.checkData(val, true)
                            },
                            message: i18n.t('请输入请求超时时间'),
                            trigger: 'blur'
                        }
                    ],
                    interval: [
                        {
                            validator: (val) => {
                                return this.checkData(val, true)
                            },
                            message: i18n.t('请输入重试间隔'),
                            trigger: 'blur'
                        }
                    ]
                },
                addrFormRules: {
                    endpoint: [
                        {
                            validator: (val) => {
                                return this.checkData(val)
                            },
                            message: i18n.t('请输入请求URL'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                const regex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w.-]*)*\/?$/i
                                return regex.test(val)
                            },
                            message: i18n.t('请输入正确的请求URL'),
                            trigger: 'blur'
                        }
                    ],
                    method: [
                        {
                            validator: (val) => {
                                return this.checkData(val)
                            },
                            message: i18n.t('请选择请求方法'),
                            trigger: 'blur'
                        }
                    ]
                },
                tokenFormRules: {
                    token: [
                        {
                            validator: (val) => {
                                return this.checkData(val)
                            },
                            message: i18n.t('请输入token'),
                            trigger: 'blur'
                        }
                    ]
                },
                basicFormRules: {
                    username: [
                        {
                            validator: (val) => {
                                return this.checkData(val)
                            },
                            message: i18n.t('请输入用户名'),
                            trigger: 'blur'
                        }
                    ],
                    password: [
                        {
                            validator: (val) => {
                                return this.checkData(val)
                            },
                            message: i18n.t('请输入密码'),
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        computed: {
            isAccessAuth () {
                const { authorization } = this.localWebhookForm.extra_info
                if (authorization.type) {
                    if (authorization.type === 'basic') {
                        return authorization.username !== '' && authorization.password !== ''
                    } else {
                        return authorization.token !== ''
                    }
                }
                return true
            },
            isAccessHeaders () {
                const { headers } = this.localWebhookForm.extra_info
                return headers.length <= 0 ? true : headers.every(item => (item.key === '') === (item.value === ''))
            },
            isAccessSettings () {
                const { timeout, retry_times, interval } = this.localWebhookForm.extra_info
                return /^[0-9]+$/.test(timeout) && /^[0-9]+$/.test(retry_times) && /^[0-9]+$/.test(interval)
            }
        },
        methods: {
            ...mapActions('template', [
                'debugWebhook'
            ]),
            renderLabel (h, name) {
                return h('div', { class: 'tab-name-badge' }, [
                    h('div', { class: 'panel-name' }, [
                        name === 'headers' ? this.$t('头信息') : (name === 'settings' ? this.$t('设置') : this.$t('认证'))
                    ]),
                    h('div', {
                        class: ['badge', (name === 'headers' ? this.isAccessHeaders : (name === 'settings' ? this.isAccessSettings : this.isAccessAuth)) ? 'badge-success' : 'badge-error']
                    })
                ])
            },
            requestTypetabChange (tabName) {
                // 清除对表单的校验
                this.$refs.settingForm && this.$refs.settingForm.clearError()
                this.$refs.basicForm && this.$refs.basicForm.clearError()
                this.$refs.tokenForm && this.$refs.tokenForm.clearError()
                this.activeTab = tabName
            },
            addHeadersRow () {
                this.localWebhookForm.extra_info.headers.push({
                    key: '',
                    value: '',
                    desc: ''
                })
            },
            onEnableWebhookChange (row) {
                this.$emit('change', row, true)
            },
            onAuthConfigChange (val) {
                this.onWebhookConfigChange()
                this.$nextTick(() => {
                    this.$refs.basicForm && this.$refs.basicForm.clearError()
                    this.$refs.tokenForm && this.$refs.tokenForm.clearError()
                })
            },
            onWebhookConfigChange () {
                this.$emit('change', this.localWebhookForm)
            },
            checkInterval () {
                return this.localWebhookForm.extra_info.retry_times <= 5
            },
            checkData (val) {
                if (this.isEnable) {
                    return val !== ''
                }
                return true
            },
            validate () {
                if (this.isEnable) {
                    const { type } = this.localWebhookForm.extra_info?.authorization || ''
                    const validations = [
                        this.$refs.settingForm.validate(),
                        this.$refs.addrForm.validate()
                    ]
                    if (type === 'basic') {
                        validations.push(this.$refs.basicForm.validate())
                    } else if (type === 'bearer') {
                        validations.push(this.$refs.tokenForm.validate())
                    }
                    validations.push(this.isAccessHeaders)
                    return Promise.all(validations).then(results => {
                        return results.every(valid => valid)
                    }).catch(() => {
                        return false
                    })
                }
                return true
            },
            delItemHeader (row, index) {
                this.localWebhookForm.extra_info.headers.splice(index, 1)
                this.onWebhookConfigChange()
            },
            async debugMock () {
                const { authorization, headers, timeout, retry_times, interval } = this.localWebhookForm.extra_info
                const basicAuth = {}
                if (authorization.type === 'basic') {
                    const username = authorization.username.trim()
                    const password = authorization.password.trim()
                    basicAuth.type = 'basic'
                    basicAuth.token = {
                        username,
                        password
                    }
                }
                const params = {
                    method: this.localWebhookForm.method,
                    endpoint: this.localWebhookForm.endpoint,
                    authorization: authorization.type === 'basic' ? basicAuth : authorization,
                    headers,
                    timeout,
                    retry_times,
                    interval
                }
                const res = await this.debugWebhook(params)
                if (res.result) {
                    this.$bkNotify({
                        type: 'success',
                        title: i18n.t('调试结果'),
                        message: i18n.t('请求发送成功'),
                        theme: 'success'
                    })
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
.http-callback-address{
    display: flex;
    padding-bottom: 10px;
    .http-callback-method-select{
        width: 80px;
    }
    .http-callback-url-input{
        width: 592px;
    }
    .form-item-select{
        padding-right: 24px !important;
    }

}
.http-callback-request-params{
    background-color: #f5f6fa;
    margin-top: 5px;
    position: relative;
    .triangle{
        color: #f5f6fa;
        position: absolute;
        top: -13px;
        left: 135px;
    }
}
.disabled-tab-name{
    color: #63656e;
}
.bk-form-radio{
    margin-right: 40px;
}
::v-deep .bk-form{
    display: flex;
    .bk-form-item{
        margin-top: 0 !important;
        padding-right: 40px;
        .bk-form-content{
            margin-left: 0px !important;
        }
        .from-item-content{
            display: flex;
            .unit{
                margin-left: 5px;
                min-height: 32px;
                font-size: 14px;
                font-weight: 400;
                color: #63656e;
            }
        }
        .bk-label{
            margin-top: 10px;
            font-size: 14px;
            font-weight: 400;
            color: #63656e;
        }
    }
}
.auth-input{
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 14px;
    font-weight: 400;
    color: #63656e;
}
::v-deep .bk-tab-section{
    padding: 10px 20px;
}
.header-table-bottom{
    padding: 10px 0px;
    display: flex;
    justify-content: space-around;
    background-color: #ffffff;
    .add-header{
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 1px solid #c4c6cc;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 18px;
    }
    .add-header-disabled{
        cursor: not-allowed;
    }
}
.is-task-setting{
    padding-left: 35px;
}
.disabled-cursor {
    cursor: not-allowed;
    opacity: 0.6;
}
.auth-basic-info {
    margin-bottom: 10px;
    display: flex;
    width: 100%;
    .basic-username, > div {
        flex: 1;
        margin-right: 10px;
    }
}
.auth-bearer-info{
    margin-bottom: 15px;
}
.debug-btn{
    margin-top: 10px;
}
.http-callaback-switch{
    span{
      line-height: 32px;
      font-size: 14px;
      font-weight: 400;
      color: #63656e;
    }
}
::v-deep .tab-name-badge{
    display: flex;
    align-items: center;
}
::v-deep .badge{
    border: 2px solid #fff;
    color: #fff;
    border-width: 1px;
    width: 8px;
    height: 8px;
    min-width: 8px;
    margin-left: 4px;
    border-radius: 18px;
}
::v-deep .badge-success{
    background-color: #2dcb56;
}
::v-deep .badge-error{
    background-color: #ff5656;
}
</style>
