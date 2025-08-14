<template>
    <div :class="['http-callback-wrapper', { 'is-task-setting': !isViewMode }]">
        <div class="http-callback-address">
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
                    :name="option.name">
                </bk-option>
            </bk-select>
            <div class="http-callback-url">
                <bk-input behavior="simplicity"
                    :disabled="isViewMode"
                    :clearable="true"
                    v-model="localWebhookForm.endpoint"
                    :placeholder="$t('输入请求URL')"
                    @change="onWebhookConfigChange">
                </bk-input>
            </div>
        </div>
        <div class="http-callback-request-params">
            <bk-icon type="up-shape" class="triangle" />
            <bk-tab
                :active.sync="activeTab"
                type="unborder-card"
                @tab-change="requestTypetabChange">
                <bk-tab-panel name="params" :disabled="true">
                    <template slot="label">
                        <span class="panel-name disabled-tab-name">{{$t('参数')}}</span>
                    </template>
                </bk-tab-panel>
                <bk-tab-panel name="authentication">
                    <template slot="label">
                        <span class="panel-name">{{$t('认证')}}</span>
                        <bk-badge dot theme="success"></bk-badge>
                    </template>
                    <bk-radio-group
                        v-model="localWebhookForm.extra_info.authorization.type"
                        @change="onWebhookConfigChange"
                    >
                        <bk-radio value="" :disabled="isViewMode">{{$t('无需认证')}}</bk-radio>
                        <bk-radio value="bearer" :disabled="isViewMode">Bearer Token</bk-radio>
                        <bk-radio value="basic" :disabled="isViewMode">Basic Auth</bk-radio>
                    </bk-radio-group>
                    <div class="auth-bearer-info"
                        v-if="localWebhookForm.extra_info.authorization.type === 'bearer'">
                        <p class="auth-input">Token</p>
                        <bk-input
                            v-model="localWebhookForm.extra_info.authorization.token"
                            behavior="simplicity"
                            :disabled="isViewMode"
                            :clearable="true"
                            @change="onWebhookConfigChange"></bk-input>
                    </div>
                    <div class="auth-basic-info"
                        v-if="localWebhookForm.extra_info.authorization.type === 'basic'">
                        <div class="basic-username">
                            <p class="auth-input">{{$t('用户名')}}</p>
                            <bk-input v-model="localWebhookForm.extra_info.authorization.username"
                                behavior="simplicity"
                                :disabled="isViewMode"
                                :clearable="true"
                                @change="onWebhookConfigChange"></bk-input>
                        </div>
                        <div>
                            <p class="auth-input">{{$t('密码')}}</p>
                            <bk-input v-model="localWebhookForm.extra_info.authorization.password"
                                behavior="simplicity"
                                :type="'password'"
                                :disabled="isViewMode"
                                :clearable="true"
                                @change="onWebhookConfigChange"></bk-input>
                        </div>
                    </div>
                </bk-tab-panel>
                <bk-tab-panel name="headers" :label="$t('头信息')">
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
                <bk-tab-panel name="body" :disabled="true">
                    <template slot="label">
                        <span class="panel-name disabled-tab-name">{{$t('主体')}}</span>
                        <bk-badge dot theme="success"></bk-badge>
                    </template>
                </bk-tab-panel>
                <bk-tab-panel name="settings" :label="$t('设置')">
                    <bk-form form-type="vertical" :rules="rules" ref="settingForm">
                        <bk-form-item v-for="item in settingFieldConfig" :key="item.key" :label="item.label" :property="item.key === 'retry_times' ? 'retry_times' : ''" :icon-offset="27">
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
    </div>

</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    export default {
        props: {
            webhookData: {
                type: Object,
                default: () => ({})
            },
            isViewMode: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const defaultWebhookForm = {
                method: '',
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
            return {
                methodList: [
                    {
                        id: 'POST',
                        key: 'POST',
                        name: 'POST'
                    },
                    {
                        id: 'GET',
                        key: 'GET',
                        name: 'GET'
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
                localWebhookForm,
                rules: {
                    retry_times: [
                        {
                            validator: this.checkInterval,
                            message: i18n.t('重试次数不能超过5次'),
                            trigger: 'blur'
                        }
                    ]
                }
            }
        },
        methods: {
            requestTypetabChange (tabName) {
                this.activeTab = tabName
            },
            addHeadersRow () {
                this.localWebhookForm.extra_info.headers.push({
                    key: '',
                    value: '',
                    desc: ''
                })
            },
            onWebhookConfigChange () {
                this.$emit('change', this.localWebhookForm)
            },
            checkInterval () {
                return this.localWebhookForm.extra_info.retry_times <= 5
            },
            validate () {
                return this.$refs.settingForm.validate().then(valid => valid)
            },
            delItemHeader (row, index) {
                this.localWebhookForm.extra_info.headers.splice(index, 1)
                this.onWebhookConfigChange()
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
    .http-callback-url{
        flex: 1;
        margin-left: 24px;
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
.bk-form{
    display: flex;
    .bk-form-item{
        margin-top: 0 !important;
        padding-right: 40px;
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
</style>
