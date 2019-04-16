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
    <div class="execute-info" v-bkloading="{isLoading: loading, opacity: 1}">
        <h3 class="panel-title">{{ i18n.execute_detail }}</h3>
        <section class="info-section">
            <h4 class="common-section-title">{{ i18n.execute_info }}</h4>
            <table class="operation-table">
                <thead>
                    <tr>
                        <th class="start-time">{{ i18n.start_time }}</th>
                        <th class="finish-time">{{ i18n.finish_time }}</th>
                        <th class="last-time">{{ i18n.last_time}}</th>
                        <th class="task-skipped">{{ i18n.task_skipped}}</th>
                        <th class="error_ignorable">{{i18n.error_ignorable}}</th>
                        <th class="manually-retry">{{i18n.manuallyRetry}}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="start-time">{{nodeInfo.start_time}}</td>
                        <td class="finish-time">{{nodeInfo.finish_time}}</td>
                        <td class="last-time">{{getLastTime(nodeInfo.elapsed_time)}}</td>
                        <td class="task-skipped">{{nodeInfo.skip ? i18n.yes : i18n.no}}</td>
                        <td class="error_ignorable">{{nodeInfo.error_ignorable ? i18n.yes : i18n.no}}</td>
                        <td class="manually-retry">{{nodeInfo.retry > 0 ? i18n.yes : i18n.no}}</td>
                    </tr>
                </tbody>
            </table>
        </section>
        <section class="info-section" v-show="isSingleAtom">
            <h4 class="common-section-title">{{ i18n.inputs_params }}</h4>
            <div class="">
                <RenderForm
                    v-if="!isEmptyParams && !loading"
                    :scheme="renderConfig"
                    :formOption="renderOption"
                    v-model="renderData">
                </RenderForm>
                <NoData v-else></NoData>
            </div>
        </section>
        <section class="info-section" v-show="isSingleAtom">
            <h4 class="common-section-title">{{ i18n.outputs_params }}</h4>
            <table class="operation-table outputs-table">
                <thead>
                    <tr>
                        <th class="output-name">{{ i18n.name }}</th>
                        <th class="output-value">{{ i18n.value }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="output in nodeInfo.outputs" :key="output.name">
                        <td class="output-name">{{getOutputName(output)}}</td>
                        <td class="output-value" v-html="getOutputValue(output)"></td>
                    </tr>
                </tbody>
            </table>
        </section>
        <section class="info-section" v-if="nodeInfo && nodeInfo.ex_data">
            <h4 class="common-section-title">{{ i18n.exception }}</h4>
            <div v-html="failInfo"></div>
            <IpLogContent
                v-if="nodeInfo.ex_data.show_ip_log"
                :nodeInfo="nodeInfo">
            </IpLogContent>
        </section>
        <section class="info-section" v-if="nodeInfo && nodeInfo.histories && nodeInfo.histories.length">
            <h4 class="common-section-title">{{ i18n.retries }}</h4>
            <el-table
                border
                class="retry-table"
                :data="nodeInfo.histories">
                <el-table-column type="expand">
                    <template slot-scope="props">
                        <div class="common-form-item">
                            <label>{{ i18n.inputs_params }}</label>
                            <div class="common-form-content">
                                <VueJsonPretty
                                    :data="props.row.inputs">
                                </VueJsonPretty>
                            </div>
                        </div>
                        <div class="common-form-item">
                            <label>{{ i18n.outputs_params }}</label>
                            <div class="common-form-content">
                                <VueJsonPretty
                                    :data="props.row.outputs">
                                </VueJsonPretty>
                            </div>
                        </div>
                        <div class="common-form-item">
                            <label>{{ i18n.exception }}</label>
                            <div class="common-form-content">
                                <div v-html="props.row.ex_data"></div>
                            </div>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column :label="i18n.index" :width="'70'">
                    <template slot-scope="props">
                        {{props.$index + 1}}
                    </template>
                </el-table-column>
                <el-table-column
                    :label="i18n.start_time"
                    prop="start_time">
                </el-table-column>
                <el-table-column
                    :label="i18n.finish_time"
                    prop="finish_time">
                </el-table-column>
                <el-table-column
                    :width="'100'"
                    :label="i18n.last_time"
                    prop="last_time">
                </el-table-column>
            </el-table>
        </section>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import VueJsonPretty from 'vue-json-pretty'
import tools from '@/utils/tools.js'
import { URL_REG } from '@/constants/index.js'
import { errorHandler } from '@/utils/errorHandler.js'
import { checkDataType } from '@/utils/checkDataType.js'
import NoData from '@/components/common/base/NoData.vue'
import BaseCollapse from '@/components/common/base/BaseCollapse.vue'
import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
import IpLogContent from '@/components/common/Individualization/IpLogContent.vue'
export default {
    name: 'ExecuteInfo',
    components: {
        VueJsonPretty,
        RenderForm,
        NoData,
        BaseCollapse,
        IpLogContent
    },
    props: ['nodeDetailConfig'],
    data () {
        return {
            i18n: {
                execute_detail: gettext("执行详情"),
                execute_info: gettext("执行信息"),
                start_time: gettext("开始时间"),
                finish_time: gettext("结束时间"),
                last_time: gettext("耗时"),
                task_skipped: gettext("失败后跳过"),
                error_ignorable: gettext("失败自动忽略"),
                inputs_params: gettext("输入参数"),
                outputs_params: gettext("输出参数"),
                name: gettext("参数名"),
                value: gettext("参数值"),
                exception: gettext("异常信息"),
                retries: gettext("执行记录"),
                index: gettext("序号"),
                yes: gettext("是"),
                no: gettext("否"),
                manuallyRetry: gettext('手动重试')
            },
            loading: true,
            bkMessageInstance: null,
            nodeInfo: {},
            failInfo: '',
            renderOption: {
                showGroup: false,
                showLabel: true,
                showHook: false,
                formEdit: false,
                formMode: false
            },
            renderConfig: [],
            renderData: {}
        }
    },
    computed: {
        ...mapState({
            'atomFormConfig': state => state.atomForm.config
        }),
        isSingleAtom () {
            return !!this.nodeDetailConfig.component_code
        },
        isEmptyParams () {
            return this.renderConfig && this.renderConfig.length === 0
        }
    },
    watch: {
        'nodeDetailConfig.node_id' (val) {
            if (val !== undefined) {
                this.loadNodeInfo()
            }
        }
    },
    mounted () {
        this.loadNodeInfo()
    },
    methods: {
        ...mapActions('task/', [
            'getNodeActDetail'
        ]),
        ...mapActions('atomForm/', [
            'loadAtomConfig'
        ]),
        ...mapMutations ('atomForm/', [
            'setAtomConfig'
        ]),
        async loadNodeInfo () {
            this.loading = true
            try {
                const nodeDetailRes = await this.getNodeActDetail(this.nodeDetailConfig)
                if (this.isSingleAtom) {
                    this.renderConfig = await this.getNodeConfig(this.nodeDetailConfig.component_code)
                }
                if (nodeDetailRes.result) {
                    this.nodeInfo = nodeDetailRes.data
                    this.nodeInfo.histories.forEach(item => {
                        item.last_time = this.getLastTime(item.elapsed_time)
                    })
                    for ( let key in this.nodeInfo.inputs) {
                        this.$set(this.renderData, key, this.nodeInfo.inputs[key])
                    }
                    if (this.nodeDetailConfig.component_code === 'job_execute_task') {
                        this.nodeInfo.outputs = this.nodeInfo.outputs.filter(output => {
                            const outputIndex = this.nodeInfo.inputs['job_global_var'].findIndex(prop => prop.name === output.key)
                            if (!output.preset && outputIndex === -1) {
                                return false
                            }
                            return true
                        })
                    } else {
                        this.nodeInfo.outputs = this.nodeInfo.outputs.filter(output => output.preset)
                    }
                    this.failInfo = this.transformFailInfo(this.nodeInfo.ex_data)
                    
                    if (this.nodeInfo.ex_data && this.nodeInfo.ex_data.show_ip_log){
                        this.failInfo = this.transformFailInfo(this.nodeInfo.ex_data.exception_msg)
                    } else {
                        this.failInfo = this.transformFailInfo(this.nodeInfo.ex_data)
                    }
                } else {
                    errorHandler(nodeDetailRes, this)
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.loading = false
            }
        },
        async getNodeConfig (type) {
            if (this.atomFormConfig[type]) {
                return this.atomFormConfig[type]
            } else {
                try {
                    await this.loadAtomConfig({atomType: type})
                    this.setAtomConfig({atomType: type, configData: $.atoms[type]})
                    return this.atomFormConfig[type]
                } catch (e) {
                    this.$bkMessage({
                        message: e,
                        theme: 'error'
                    })
                }
            }
        },
        getOutputValue (output) {
            if (output.value === 'undefined' || output.value === '') {
                return '--'
            } else if (!output.preset && this.nodeDetailConfig.component_code === 'job_execute_task') {
                return output.value
            } else {
                if (URL_REG.test(output.value)) {
                    return `<a class="info-link" target="_blank" href="${output.value}">${output.value}</a>`
                }
                return output.value
            }

        },
        transformFailInfo (data) {
            if (!data) {
                return ''
            }
            if (typeof data === 'string') {
                const info = data.replace(/\n/g, '<br>')
                return info
            } else {
                return data
            }
        },
        getLastTime (time) {
            return tools.timeTransform(time)
        },
        getOutputName (output) {
            if (this.nodeDetailConfig.component_code === 'job_execute_task' && output.perset) {
                return output.key
            }
            return output.name
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/config.scss';
.execute-info {
    padding: 30px 20px;
    height: 100%;
    overflow-y: auto;
    @include scrollbar;
    .panel-title {
        margin: 0;
        font-size: 22px;
        font-weight: normal;
    }
    .info-section {
        margin: 30px 0;
        word-wrap: break-word;
        word-break: break-all;
        /deep/ a {
            color: #4b9aff;
        }
    }
    .common-section-title {
        margin-bottom: 20px;
    }
    .operation-table {
        table-layout: fixed;
        .start-time,
        .finish-time {
            width: 210px;
        }
        .last-time {
            width: 80px;
        }
        .output-name {
            width: 35%;
        }
    }
    .retry-table {
        .common-form-item {
            & > label {
                margin-top: 0;
                width: 60px;
            }
            .commont-form-content {
                margin-left: 100px;
            }
        }
    }
    /deep/ .el-table {
        .el-table__header {
            tr, th {
                background: $whiteNodeBg;
                color: $greyDefault;
            }
        }
        .el-table__row.expanded {
            background: $blueStatus;
        }
        .el-table__expanded-cell {
            background: $whiteThinBg;
        }
    }
}
</style>
