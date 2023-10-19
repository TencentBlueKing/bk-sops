<template>
    <div class="control-option">
        <bk-form
            ref="pluginForm"
            form-type="vertical"
            :model="formData">
            <bk-form-item :label="$t('是否可选')">
                <bk-switcher
                    theme="primary"
                    size="small"
                    :value="formData.selectable"
                    :disabled="isViewMode"
                    @change="onSelectableChange">
                </bk-switcher>
            </bk-form-item>
            <bk-form-item v-if="!isSubFlow" :label="$t('超时控制')">
                <div class="timeout-setting-wrap">
                    <bk-switcher
                        theme="primary"
                        size="small"
                        style="margin-right: 8px;"
                        :value="formData.timeoutConfig.enable"
                        :disabled="isViewMode || formData.ignorable || formData.autoRetry.enable"
                        @change="onTimeoutChange">
                    </bk-switcher>
                    <template v-if="formData.timeoutConfig.enable">
                        {{ $t('超时') }}
                        <div class="number-input" style="margin: 0 4px;">
                            <bk-input
                                v-model.number="formData.timeoutConfig.seconds"
                                type="number"
                                style="width: 75px;"
                                :placeholder="' '"
                                :min="10"
                                :max="maxNodeExecuteTimeout"
                                :precision="0"
                                :readonly="isViewMode"
                                @change="updateData">
                            </bk-input>
                            <span class="unit">{{ $tc('秒', 0) }}</span>
                        </div>
                        {{ $t('后') }}{{ $t('，') }}{{ $t('则') }}
                        <bk-select
                            style="width: 160px; margin-left: 4px;"
                            v-model="formData.timeoutConfig.action"
                            :disabled="isViewMode"
                            :clearable="false" @change="updateData">
                            <bk-option id="forced_fail" :name="$t('强制终止')"></bk-option>
                            <bk-option id="forced_fail_and_skip" :name="$t('强制终止后跳过')"></bk-option>
                        </bk-select>
                    </template>
                </div>
                <p v-if="formData.timeoutConfig.enable" class="error-handle-tips" style="margin-top: 6px;">
                    {{ $t('该功能仅对V2引擎生效') }}
                </p>
            </bk-form-item>
            <bk-form-item :label="$t('失败处理')">
                <div class="error-handle">
                    <bk-checkbox
                        :value="formData.retryable"
                        :disabled="isViewMode || formData.ignorable || formData.autoRetry.enable"
                        @change="onErrorHandlerChange($event, 'retryable')">
                        <span class="error-handle-icon"><span class="text">MR</span></span>
                        <span class="error-handle-text" v-bk-overflow-tips>{{ $t('手动重试') }}</span>
                    </bk-checkbox>
                    <bk-checkbox
                        :value="formData.autoRetry.enable"
                        :disabled="isViewMode || formData.ignorable || formData.timeoutConfig.enable"
                        @change="onErrorHandlerChange($event, 'autoRetry')">
                        <span class="error-handle-icon"><span class="text">AR</span></span>
                        <span class="auto-retry-times" @click.stop>
                            {{ $t('自动重试') }}
                            <div class="number-input retry-times-input" style=" margin-left: 4px;">
                                <bk-input
                                    v-model.number="formData.autoRetry.times"
                                    type="number"
                                    :placeholder="' '"
                                    :disabled="isViewMode || !formData.autoRetry.enable"
                                    :max="10"
                                    :min="1"
                                    :precision="0"
                                    @change="updateData">
                                    <template slot="append">
                                        <div class="group-append-text">{{ $t('次') }}</div>
                                    </template>
                                </bk-input>
                            </div>
                            <span class="error-handle-text" v-bk-overflow-tips>{{ $t('，') }}{{ $t('间隔') }}</span>
                            <div class="number-input interval-input" style="margin: 0 4px;">
                                <bk-input
                                    v-model.number="formData.autoRetry.interval"
                                    type="number"
                                    :placeholder="' '"
                                    :disabled="isViewMode || !formData.autoRetry.enable"
                                    :max="10"
                                    :min="0"
                                    :precision="0"
                                    @change="updateData">
                                    <template slot="append">
                                        <div class="group-append-text">{{ $t('error_handle_秒') }}</div>
                                    </template>
                                </bk-input>
                            </div>
                        </span>
                    </bk-checkbox>
                </div>
                <div class="error-handle">
                    <bk-checkbox
                        :value="formData.skippable"
                        :disabled="isViewMode || formData.ignorable"
                        @change="onErrorHandlerChange($event, 'skippable')">
                        <span class="error-handle-icon"><span class="text">MS</span></span>
                        <span class="error-handle-text" v-bk-overflow-tips>{{ $t('手动跳过') }}</span>
                    </bk-checkbox>
                    <bk-checkbox
                        :value="formData.ignorable"
                        :disabled="isViewMode || formData.autoRetry.enable || formData.timeoutConfig.enable"
                        @change="onErrorHandlerChange($event, 'ignorable')">
                        <span class="error-handle-icon"><span class="text">AS</span></span>
                        <span class="error-handle-text" v-bk-overflow-tips>{{ $t('自动跳过') }}</span>
                    </bk-checkbox>
                </div>
                <p
                    v-if="!formData.ignorable && !formData.skippable && !formData.retryable && !formData.autoRetry.enable"
                    class="error-handle-tips">
                    {{ $t('未选择失败处理方式，标准插件节点如果执行失败，会导致任务中断后不可继续') }}
                </p>
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    import { mapState } from 'vuex'
    export default {
        name: 'ControlOption',
        component: {},
        props: {
            isViewMode: Boolean,
            nodeId: String
        },
        data () {
            return {
                formData: {},
                maxNodeExecuteTimeout: window.MAX_NODE_EXECUTE_TIMEOUT
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities
            }),
            isSubFlow () {
                const nodeConfig = this.activities[this.nodeId] || {}
                return nodeConfig.type !== 'ServiceActivity'
            }
        },
        created () {
            this.initFormData()
        },
        methods: {
            initFormData () {
                const {
                    error_ignorable, can_retry, retryable, isSkipped, skippable, optional,
                    auto_retry, timeout_config
                } = this.activities[this.nodeId] || {}

                this.formData = {
                    ignorable: error_ignorable,
                    // isSkipped 和 can_retry 为旧数据字段，后来分别变更为 skippable、retryable，节点点开编辑保存后会删掉旧字段
                    // 这里取值做兼容处理，新旧数据不可能同时存在，优先取旧数据字段
                    skippable: isSkipped === undefined ? skippable : isSkipped,
                    retryable: can_retry === undefined ? retryable : can_retry,
                    selectable: optional,
                    autoRetry: Object.assign({}, { enable: false, interval: 0, times: 1 }, auto_retry),
                    timeoutConfig: timeout_config || { enable: false, seconds: 10, action: 'forced_fail' }
                }
            },
            onErrorHandlerChange (val, type) {
                this.formData.autoRetry.interval = 0
                this.formData.autoRetry.times = 1
                if (type === 'autoRetry') {
                    this.formData.autoRetry.enable = val
                    this.formData.retryable = true
                } else {
                    if (type === 'retryable') {
                        this.formData.autoRetry.enable = false
                        this.formData.autoRetry.interval = 0
                        this.formData.autoRetry.times = 1
                    }
                    if (type === 'ignorable' && val) {
                        this.formData.skippable = false
                        this.formData.retryable = false
                        this.formData.autoRetry.enable = false
                    }
                    this.formData[type] = val
                }
                if (val && ['autoRetry', 'ignorable'].includes(type)) {
                    this.formData.timeoutConfig = {
                        enable: false,
                        seconds: 10,
                        action: 'forced_fail'
                    }
                }
                this.updateData()
            },
            onTimeoutChange (val) {
                this.formData.timeoutConfig = {
                    enable: val,
                    seconds: 10,
                    action: 'forced_fail'
                }
                if (val) {
                    this.formData.ignorable = false
                    this.formData.autoRetry.enable = false
                }
                this.updateData()
            },
            onSelectableChange (val) {
                this.formData.selectable = val
                this.updateData()
            },
            onClosePanel () {
                this.$emit('close')
            },
            updateData () {
                const { ignorable, skippable, retryable, selectable, autoRetry, timeoutConfig } = this.formData
                let data
                if (this.isSubFlow) {
                    data = { selectable, latestVersion: this.version, retryable, autoRetry, timeoutConfig, skippable, ignorable }
                } else {
                    data = { ignorable, skippable, retryable, selectable, autoRetry, timeoutConfig }
                }
                this.$emit('update', data)
            }
        }
    }
</script>

<style lang="scss" scoped>
.control-option {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 126px);
    padding: 8px 0 32px;
    .bk-form {
        flex: 1;
        padding: 0 40px;
    }
    .btn-footer {
        width: 100%;
        padding: 8px 24px;
        background: #fafbfd;
        box-shadow: 0 -1px 0 0 #dcdee5;
        z-index: 10;
    }
}
.error-handle-label {
    top: -8px !important;
}
.error-handle {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    &:not(:first-of-type) {
        margin-top: 8px;
    }
    /deep/.bk-checkbox-text {
        display: flex;
        align-items: center;
    }
    .error-handle-icon {
        display: inline-block;
        line-height: 12px;
        color: #ffffff;
        background: #979ba5;
        border-radius: 2px;
        margin-right: 5px;
        .text {
            display: inline-block;
            font-size: 12px;
            transform: scale(0.8);
        }
    }
    .error-handle-text {
        font-size: 12px;
        color: #63656e;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        word-break: break-all;
    }
    .auto-retry-times {
        display: inline-flex;
        align-items: center;
        margin-left: 4px;
        height: 32px;
        font-size: 12px;
        color: #63656e;
    }
    
    /deep/ .bk-form-checkbox {
        display: flex;
        align-items: center;
        &:not(:last-of-type) {
            margin-right: 50px;
        }
        &.is-disabled .bk-checkbox-text {
            color: #c4c6cc;
        }
        &.is-checked .bk-checkbox-text {
            color: #63656e;
        }
    }
}
.error-handle-tips {
    font-size: 12px;
    line-height: 1;
    color: #ffb400;
    margin-top: 2px;
}
.timeout-setting-wrap {
    display: flex;
    align-items: center;
    height: 32px;
    font-size: 12px;
    color: #63656e;
}
.number-input {
    position: relative;
    .unit {
        position: absolute;
        right: 8px;
        top: 1px;
        height: 30px;
        line-height: 30px;
        color: #999999;
        background: transparent;
    }
}
.retry-times-input,
.interval-input {
    /deep/.bk-input-number {
        width: 50px;
        .bk-form-input {
            padding-right: 5px !important;
        }
    }
    /deep/.group-append {
        display: flex;
        align-items: center;
        margin-left: -1px;
        background: #e1ecff;
        border: 1px solid #c4c6cc !important;
        border-left: none !important;
        background: #fff !important;
        transition: border .2s linear;
        .group-append-text {
            font-size: 12px;
            padding-right: 5px;
        }
    }
    .control-active {
        /deep/.group-append {
            border-color: #3a84ff !important;
        }
    }
    .control-disable {
        /deep/.group-append {
            background-color: #fafbfd !important;
            border-color: #dcdee5 !important;
        }
    }
}
.retry-times-input {
    /deep/.bk-input-number {
        width: 45px;
    }
}
.auto-retry-times,
.timeout-setting-wrap {
    /deep/ .bk-input-number .input-number-option {
        display: none;
    }
}
</style>
