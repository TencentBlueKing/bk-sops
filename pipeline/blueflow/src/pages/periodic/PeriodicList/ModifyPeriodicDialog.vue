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
        :quick-close="false"
        :has-header="true"
        :ext-cls="'common-dialog'"
        :title="i18n.modifyTask"
        width="600"
        :is-show.sync="isModifyDialogShow"
        @confirm="onModifyPeriodicConfirm"
        @cancel="onModifyPeriodicCancel">
        <div slot="content" v-bkloading="{isLoading: loading, opacity: 1}">
            <div class="periodic-info">
                <h3 class="common-section-title">{{ i18n.periodicInfo }}</h3>
                <div class="common-form-item">
                    <label class="required">{{i18n.periodicRule}}</label>
                    <div class="common-form-content">
                        <BaseInput
                            name="periodicCron"
                            v-model="periodicCron"
                            v-validate="periodicRule"/>
                        <span v-show="errors.has('periodicCron')" class="common-error-tip error-msg">{{ errors.first('periodicCron') }}</span>
                        <bk-tooltip placement="bottom-start" class="periodic-img-tooltip">
                            <i class="bk-icon icon-info-circle"></i>
                            <div slot="content">
                                <img :src="periodicCronImg" alt="i18n.errorPicture">
                            </div>
                        </bk-tooltip>
                    </div>
                </div>
                <div class="param-info" v-if="!loading">
                    <h3 class="common-section-title">{{ i18n.paramsInfo }}</h3>
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
    </bk-dialog>
</template>
<script>
import '@/utils/i18n.js'
import { mapMutations, mapActions } from 'vuex'
import { PERIODIC_REG } from '@/constants/index.js'
import BaseInput from '@/components/common/base/BaseInput.vue'
import TaskParamEdit from '@/pages/task/TaskParamEdit.vue'
import { errorHandler } from '@/utils/errorHandler.js'
import NoData from '@/components/common/base/NoData.vue'

export default {
    name: 'ModifyPeriodicDialog',
    components: {
        BaseInput,
        TaskParamEdit,
        NoData
    },
    props: ['isModifyDialogShow', 'taskId', 'cron', 'constants', 'loading'],
    data () {
        return {
            i18n: {
                periodicInfo: gettext('周期信息'),
                modifyTask: gettext('修改周期任务'),
                periodicRule: gettext('周期规则'),
                paramsInfo: gettext("参数信息"),
                errorPicture: gettext('图片出错')
            },
            periodicRule: {
                required: true,
                regex: PERIODIC_REG
            },
            periodicCronImg: require('@/assets/images/' + gettext('task-zh') + '.png'),
            periodicCron: this.cron
        }
    },
    computed: {
        isVariableEmpty () {
            return Object.keys(this.constants).length === 0
        }
    },
    methods: {
        ...mapActions('periodic/',[
            'modifyPeriodicCron',
            'modifyPeriodicConstants'
        ]),
        onModifyPeriodicCancel () {
            this.$emit('onModifyPeriodicCancel')
        },
        onModifyPeriodicConfirm () {
            const paramEditComp = this.$refs.TaskParamEdit
            this.$validator.validateAll().then((result) => {
                let formValid = true
                let periodicConstants = ''
                if (paramEditComp) {
                    const formData = paramEditComp.getVariableData()
                    periodicConstants = formData
                    formValid = paramEditComp.validate()
                }
                const cronArray = this.periodicCron.split(' ')
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
                if (this.cron === this.periodicCron && periodicConstants === '') {
                    // 没有改变表达式，且没有ramdomform内容
                    this.$emit('onModifyPeriodicCancel')
                } else if (periodicConstants === '') {
                    this.modifyCron(cronData)
                } else {
                    const constants = {}
                    for (let key in periodicConstants){
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
                    this.$emit('onModifyPeriodicConfirm')
                })
            }
            catch (e) {
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
    padding-bottom: 40px;
}
.common-section-title {
    margin-bottom: 24px;
    padding-left: 16px;
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
