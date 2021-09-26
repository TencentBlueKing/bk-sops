<template>
    <div class="edit-clocked-task">
        <bk-sideslider
            :width="800"
            ext-cls="edit-clocked-sideslider"
            :is-show.sync="isShowSideslider"
            :quick-close="true"
            :before-close="onCloseConfig">
            <div slot="header">{{ title }}</div>
            <template slot="content">
                <section class="config-section">
                    <p class="title">{{$t('基础信息')}}</p>
                    <bk-form
                        :label-width="90"
                        ref="basicConfigForm"
                        :model="formData"
                        :rules="rules">
                        <bk-form-item :label="$t('计划名称')" :required="true" property="planName">
                            <bk-input v-model="formData.task_name" :disabled="true"></bk-input>
                        </bk-form-item>
                        <bk-form-item :label="$t('流程模板')" :required="true" property="processTemp">
                            <div class="select-wrapper">
                                <bk-input v-model="formData.template_name" :disabled="true"></bk-input>
                                <i class="bk-icon icon-angle-down"></i>
                            </div>
                        </bk-form-item>
                        <bk-form-item :label="$t('启动时间')" :required="true" property="startTime">
                            <bk-date-picker
                                v-model="formData.plan_start_time"
                                :placeholder="`${$t('请选择启动时间')}`"
                                :options="pickerOptions"
                                :clearable="false"
                                :type="'datetime'">
                            </bk-date-picker>
                        </bk-form-item>
                    </bk-form>
                </section>
                <section class="config-section">
                    <p class="title">{{$t('执行参数')}}</p>
                    <TaskParamEdit
                        v-bkloading="{ isLoading: isLoading, opacity: 1, zIndex: 100 }"
                        class="task-param-wrapper"
                        ref="TaskParamEdit"
                        :constants="constants">
                    </TaskParamEdit>
                </section>
                <div class="btn-footer">
                    <bk-button theme="primary" :loading="saveLoading" @click="onSaveConfig">{{ $t('保存') }}</bk-button>
                    <bk-button theme="default" :disabled="saveLoading" @click="onCloseConfig">{{ $t('取消') }}</bk-button>
                </div>
            </template>
        </bk-sideslider>
        <bk-dialog
            width="400"
            ext-cls="edit-clocked-dialog"
            :theme="'primary'"
            :mask-close="false"
            :show-footer="false"
            :value="isShowDialog"
            @cancel="isShowDialog = false">
            <div class="edit-clocked-dialog">
                <div class="save-tips">{{ $t('保存已修改的信息吗？') }}</div>
                <div class="action-wrapper">
                    <bk-button theme="primary" :loading="saveLoading" @click="onSaveConfig">{{ $t('保存') }}</bk-button>
                    <bk-button theme="default" :disabled="saveLoading" @click="onCancelSave">{{ $t('不保存') }}</bk-button>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
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
            curRow: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                isLoading: false,
                formData: {
                    template_name: '',
                    task_name: '',
                    plan_start_time: ''
                },
                initPlanStartTime: '',
                pickerOptions: {
                    disabledDate (date) {
                        return date.getTime() + 86400000 < Date.now()
                    }
                },
                rules: {
                    startTime: [
                        {
                            required: true,
                            message: this.$t('请选择启动时间'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                const timeStamp = new Date(this.formData.plan_start_time).getTime()
                                return timeStamp > new Date().getTime()
                            },
                            message: this.$t('启动时间不能小于当前时间'),
                            trigger: 'blur'
                        }
                    ]
                },
                saveLoading: false,
                constants: {},
                isShowDialog: false
            }
        },
        computed: {
            sameTimeStamp () {
                const initTimeStamp = new Date(this.initPlanStartTime).getTime()
                const curTimcStamp = new Date(this.formData.plan_start_time).getTime()
                return initTimeStamp === curTimcStamp
            }
        },
        watch: {
            isShowSideslider (val) {
                if (val) {
                    this.formData = tools.deepClone(this.curRow)
                    this.initPlanStartTime = this.formData.plan_start_time
                    this.getTemplateRenderFrom()
                }
            }
        },
        methods: {
            ...mapActions('task/', [
                'loadPreviewNodeData'
            ]),
            ...mapActions('clocked/', [
                'updateClocked'
            ]),
            async getTemplateRenderFrom () {
                try {
                    this.isLoading = true
                    const { template_id, project_id, task_parameters: taskParams } = this.curRow
                    const params = {
                        templateId: template_id,
                        excludeTaskNodesId: taskParams.exclude_task_nodes_id || [],
                        project_id,
                        template_source: 'project'
                    }
                    const resp = await this.loadPreviewNodeData(params)
                    this.constants = resp.data.pipeline_tree.constants
                    Object.values(this.constants).forEach(item => {
                        item.value = taskParams.constants[item.key] || item.value
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isLoading = false
                }
            },
            onSaveConfig () {
                try {
                    this.$refs.basicConfigForm.validate().then(async (result) => {
                        if (!result) return
                        this.saveLoading = true
                        const { id, plan_start_time: time, task_parameters: taskParams } = this.formData
                        const taskParamEdit = this.$refs.TaskParamEdit
                        const params = {
                            id,
                            plan_start_time: this.sameTimeStamp ? undefined : time,
                            task_parameters: {
                                constants: taskParamEdit ? taskParamEdit.renderData : {},
                                exclude_atsk_nodes_id: taskParams.exclude_task_nodes_id || []
                            }
                        }
                        await this.updateClocked(params)
                        this.$bkMessage({
                            'message': i18n.t('编辑计划任务成功'),
                            'theme': 'success'
                        })
                        this.isShowDialog = false
                        this.saveLoading = false
                        this.constants = {}
                        this.$emit('onSaveConfig')
                    })
                } catch (error) {
                    this.saveLoading = false
                    console.warn(error)
                }
            },
            onCloseConfig () {
                const taskParamEdit = this.$refs.TaskParamEdit
                const sameRenderData = taskParamEdit ? taskParamEdit.judgeDataEqual() : true
                if (this.sameTimeStamp && sameRenderData) {
                    this.onCancelSave()
                } else {
                    this.isShowDialog = true
                }
            },
            onCancelSave () {
                this.isShowDialog = false
                this.constants = {}
                this.$emit('onCloseConfig')
            }
        }
    }
</script>

<style lang="scss">
    .edit-clocked-dialog {
        .bk-dialog-body {
            padding: 0;
        }
        .edit-clocked-dialog {
            padding: 20px 0 40px 0;
            text-align: center;
            .save-tips {
                font-size: 24px;
                margin-bottom: 30px;
                padding: 0 10px;
            }
            .action-wrapper .bk-button {
                margin-right: 6px;
            }
        }
    }
</style>
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
        .select-wrapper,
        .bk-date-picker {
            width: 598px;
        }
        margin-bottom: 17px;
    }
    .select-wrapper {
        position: relative;
        .icon-angle-down {
            position: absolute;
            right: 7px;
            top: 7px;
            font-size: 20px;
            color: #c4c6cc;
            cursor: not-allowed;
        }
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
