<template>
    <bk-sideslider
        :width="800"
        ext-cls="edit-scheduled-sideslider"
        :is-show.sync="isShowSideslider"
        :quick-close="true">
        <div slot="header">{{ title }}</div>
        <template slot="content">
            <section class="config-section">
                <p class="title">{{$t('基础信息')}}</p>
                <bk-form
                    :label-width="90"
                    :model="formData"
                    :rules="rules">
                    <bk-form-item :label="$t('计划名称')" :required="true" property="planName">
                        <bk-input v-model="formData.plan_name" :disabled="true"></bk-input>
                    </bk-form-item>
                    <bk-form-item :label="$t('流程模板')" :required="true" property="processTemp">
                        <bk-select v-model="formData.process_temp" :disabled="true"></bk-select>
                    </bk-form-item>
                    <bk-form-item :label="$t('任务实例')" :required="true" property="taskInstace">
                        <bk-select v-model="formData.task_instance" :disabled="true"></bk-select>
                    </bk-form-item>
                    <bk-form-item :label="$t('启动时间')" :required="true" property="startTime">
                        <bk-date-picker
                            v-model="formData.start_time"
                            :placeholder="`${$t('请输入启动时间')}`"
                            :type="'datetime'">
                        </bk-date-picker>
                    </bk-form-item>
                </bk-form>
            </section>
            <section class="config-section">
                <p class="title">{{$t('执行参数')}}</p>
                <TaskParamEdit
                    class="task-param-wrapper"
                    ref="TaskParamEdit"
                    :constants="constants">
                </TaskParamEdit>
            </section>
            <div class="btn-footer">
                <bk-button theme="primary" :disabled="saveLoading" @click="onSaveConfig">{{ $t('保存') }}</bk-button>
                <bk-button theme="default" @click="onCloseConfig()">{{ $t('取消') }}</bk-button>
            </div>
        </template>
    </bk-sideslider>
</template>

<script>
    import TaskParamEdit from '../TaskParamEdit.vue'
    export default {
        components: {
            TaskParamEdit
        },
        props: {
            title: {
                type: String,
                default: ''
            },
            isShowSideslider: {
                type: Boolean,
                default: false
            },
            formData: {
                type: Object,
                default: () => ({
                    plan_name: '',
                    process_temp: '',
                    task_instance: '',
                    start_time: ''
                })
            },
            constants: {
                type: Object,
                default: () => {}
            },
            saveLoading: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const initStartTime = this.formData.start_time
            return {
                rules: {
                    startTime: [
                        {
                            required: true,
                            message: this.$t('请输入启动时间'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                const initTimeStamp = new Date().getTime(initStartTime)
                                const curTimcStamp = new Date().getTime(val)
                                return initTimeStamp > curTimcStamp
                            },
                            message: '不能小于初始值',
                            trigger: 'blur'
                        }
                    ]
                },
                initStartTime: ''
            }
        },
        methods: {
            onSaveConfig () {
                this.$emit('onSaveConfig')
            },
            onCloseConfig () {
                this.$emit('onCloseConfig')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
/deep/.bk-sideslider-content {
    height: calc(100% - 60px);
    position: relative;
    padding: 0 31px 48px 28px;
    overflow-y: auto;
    @include scrollbar;
}
/deep/.bk-sideslider-title {
    color: #313238;
    font-size: 16px;
    font-weight: normal;
}
.config-section {
    .title {
        color: #313238;
        font-size: 14px;
        line-height: 19px;
        padding: 18px 0 11px;
        margin-bottom: 24px;
        border-bottom: 1px solid #cacedb;
    }
    /deep/.bk-form {
        .bk-label {
            font-size: 12px;
            color: #63656e;
        }
        .bk-form-input,
        .bk-select,
        .bk-date-picker {
            width: 598px;
        }
        margin-bottom: 17px;
    }
}
/deep/.no-data-wrapper {
    margin: 150px 0;
}
.btn-footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #fafbfd;
    padding: 8px 0;
    .bk-button {
        margin-right: 10px;
        padding: 0 25px;
    }
}
</style>
