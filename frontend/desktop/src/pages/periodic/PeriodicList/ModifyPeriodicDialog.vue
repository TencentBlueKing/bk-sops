/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <bk-dialog
        width="600"
        :ext-cls="'common-dialog'"
        :theme="'primary'"
        :mask-close="false"
        :header-position="'left'"
        :title="i18n.modifyTask"
        :value="isModifyDialogShow"
        @confirm="onModifyPeriodicConfirm"
        @cancel="onModifyPeriodicCancel">
        <div v-bkloading="{ isLoading: loading, opacity: 1 }">
            <div class="periodic-info">
                <h3 class="local-section-title">{{ i18n.periodicInfo }}</h3>
                <div class="common-form-item">
                    <LoopRuleSelect
                        ref="loopRuleSelect"
                        class="loop-rule"
                        :manual-input-value="periodicCron" />
                </div>
                <div
                    v-if="!loading"
                    class="param-info">
                    <h3 class="local-section-title">{{ i18n.paramsInfo }}</h3>
                    <div class="common-form-content">
                        <NoData v-if="isVariableEmpty"></NoData>
                        <TaskParamEdit
                            v-else
                            ref="TaskParamEdit"
                            class="task-param-edit"
                            :constants="constants">
                        </TaskParamEdit>
                    </div>
                </div>
            </div>
        </div>
        <DialogLoadingBtn
            slot="footer"
            :dialog-footer-data="dialogFooterData"
            @onConfirm="onModifyPeriodicConfirm"
            @onCancel="onModifyPeriodicCancel">
        </DialogLoadingBtn>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { PERIODIC_REG } from '@/constants/index.js'
    import LoopRuleSelect from '@/components/common/Individualization/loopRuleSelect.vue'
    import TaskParamEdit from '@/pages/task/TaskParamEdit.vue'
    import { errorHandler } from '@/utils/errorHandler.js'
    import DialogLoadingBtn from '@/components/common/base/DialogLoadingBtn.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'ModifyPeriodicDialog',
        components: {
            TaskParamEdit,
            NoData,
            LoopRuleSelect,
            DialogLoadingBtn
        },
        props: ['isModifyDialogShow', 'taskId', 'cron', 'constants', 'loading'],
        data () {
            return {
                i18n: {
                    periodicInfo: gettext('周期信息'),
                    modifyTask: gettext('修改周期任务'),
                    periodicRule: gettext('周期规则'),
                    paramsInfo: gettext('参数信息'),
                    errorPicture: gettext('图片出错')
                },
                periodicRule: {
                    required: true,
                    regex: PERIODIC_REG
                },
                periodicCronImg: require('@/assets/images/' + gettext('task-zh') + '.png'),
                periodicCron: this.cron,
                dialogFooterData: [
                    {
                        type: 'primary',
                        loading: false,
                        btnText: gettext('确认'),
                        click: 'onConfirm'
                    }, {
                        btnText: gettext('取消'),
                        click: 'onCancel'
                    }
                ]
            }
        },
        computed: {
            isVariableEmpty () {
                return Object.keys(this.constants).length === 0
            }
        },
        methods: {
            ...mapActions('periodic/', [
                'modifyPeriodicCron',
                'modifyPeriodicConstants'
            ]),
            onModifyPeriodicCancel () {
                this.$emit('onModifyPeriodicCancel')
            },
            onModifyPeriodicConfirm () {
                const loopRule = this.$refs.loopRuleSelect.validationExpression()
                if (!loopRule.check) return
                this.dialogFooterData[0].loading = true
                const paramEditComp = this.$refs.TaskParamEdit
                this.$validator.validateAll().then((result) => {
                    let formValid = true
                    let periodicConstants = ''
                    if (paramEditComp) {
                        const formData = paramEditComp.getVariableData()
                        periodicConstants = formData
                        formValid = paramEditComp.validate()
                    }
                    const cronArray = loopRule.rule.split(' ')
                    if (cronArray.length !== 5) {
                        this.$bkMessage({
                            'message': gettext('输入周期表达式非法，请校验'),
                            'theme': 'error'
                        })
                        return
                    }
                    if (!result || !formValid) {
                        return
                    }
                    const jsonCron = JSON.stringify({
                        'minute': cronArray[0],
                        'hour': cronArray[1],
                        'day_of_week': cronArray[2],
                        'day_of_month': cronArray[3],
                        'month_of_year': cronArray[4]
                    })
                    const cronData = {
                        'taskId': this.taskId,
                        'cron': jsonCron
                    }
                    if (this.cron === loopRule.rule && periodicConstants === '') {
                        // 没有改变表达式，且没有ramdomform内容
                        this.$emit('onModifyPeriodicCancel')
                    } else if (periodicConstants === '') {
                        this.modifyCron(cronData)
                    } else {
                        const constants = {}
                        for (const key in periodicConstants) {
                            constants[key] = periodicConstants[key]['value']
                        }
                        const constantsData = {
                            'taskId': this.taskId,
                            'constants': JSON.stringify(constants)
                        }
                        this.modifyPeriodic(cronData, constantsData)
                    }
                })
            },
            modifyPeriodic (cronData, constantsData) {
                try {
                    Promise.all([this.modifyPeriodicConstants(constantsData), this.modifyPeriodicCron(cronData)]).then((values) => {
                        if (values[0].result && values[1].result) {
                            this.$bkMessage({
                                'message': gettext('修改周期任务信息成功'),
                                'theme': 'success'
                            })
                        } else if (values[0].result) {
                            this.$bkMessage({
                                'message': gettext('修改周期任务参数成功，但表达式修改未成功，请重试'),
                                'theme': 'warning'
                            })
                        } else if (values[1].result) {
                            this.$bkMessage({
                                'message': gettext('修改周期任务表达式成功，但任务参数未修改成功，请重试'),
                                'theme': 'warning'
                            })
                        } else {
                            this.$bkMessage({
                                'message': gettext('修改周期任务失败，请联系管理员'),
                                'theme': 'error'
                            })
                        }
                        this.dialogFooterData[0].loading = false
                        this.$emit('onModifyPeriodicConfirm')
                    })
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async modifyCron (cronData) {
                const result = await this.modifyPeriodicCron(cronData)
                if (result.result) {
                    this.$bkMessage({
                        'message': gettext('修改周期任务表达式成功'),
                        'theme': 'success'
                    })
                } else {
                    this.$bkMessage({
                        'message': gettext('修改周期任务失败，请联系管理员'),
                        'theme': 'error'
                    })
                }
                this.dialogFooterData.confirmBtnPending = false
                this.$emit('onModifyPeriodicConfirm')
            }
        }
    }
</script>

<style lang='scss' scoped>
@import '@/scss/config.scss';
/deep/ .bk-dialog-body {
    height: 420px;
    overflow-y: auto;
}
.periodic-info {
    padding: 20px;
}
.local-section-title {
    font-size: 14px;
    line-height: 32px;
    font-weight: 600;
    color: #313238;
    border-bottom: 1px solid #cacedb;
    margin-bottom: 30px;
}
.periodic-img-tooltip {
    float: right;
    position: relative;
    right: -25px;
    top: -27px;
    font-size: 14px;
    &:hover {
        color: $yellowBg;
    }
    /deep/ .bk-tooltip-arrow {
        display: none;
    }
}
.common-form-content {
    position: relative;
    margin-right: 30px;
    /deep/ .bk-tooltip-inner {
        max-width: 480px;
        background-color: initial;
    }
    img {
        width: 460px;
        border: 1px solid #dddddd;
        background-color: $whiteDefault;
    }
}
</style>
