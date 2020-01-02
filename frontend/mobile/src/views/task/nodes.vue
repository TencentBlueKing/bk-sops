/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <!-- 信息 -->
        <section class="bk-block">
            <van-cell>
                <template slot="title">
                    <div class="bk-text">{{ nodeDetail.name }}</div>
                </template>
                <div class="status">
                    <StatusIcon v-if="!loadingIcon" :status="status" :show-text="true"></StatusIcon>
                </div>
            </van-cell>
        </section>
        <!-- 执行信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.executeInfo }}</h2>
            <div class="bk-text-list">
                <van-cell :title="i18n.startTime" :value="nodeDetail.start_time || '--'" />
                <van-cell :title="i18n.endTime" :value="nodeDetail.finish_time || '--'" />
                <van-cell :title="i18n.costTime" :value="getLastTime(nodeDetail.elapsed_time)" />
                <van-cell :title="i18n.skipped" :value="nodeDetail.skip ? i18n.yes : i18n.no" />
                <van-cell :title="i18n.ignore" :value="nodeDetail.error_ignorable ? i18n.yes : i18n.no" />
                <van-cell :title="i18n.retryTimes" :value="nodeDetail.retry" />
            </div>
        </section>
        <!-- 输入参数 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.inputParameter }}</h2>
            <VueJsonPretty
                class="parameter-info"
                :data="nodeDetail.inputs">
            </VueJsonPretty>
        </section>
        <!-- 输出参数 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.outputParameter }}</h2>
            <div class="bk-text-list">
                <template v-if="nodeDetail.outputs && nodeDetail.outputs.length">
                    <van-cell
                        v-for="item in nodeDetail.outputs"
                        :key="item.index"
                        :title="item.name"
                        :is-link="isOutputValueLink(item.value)"
                        :url="isOutputValueLink(item.value) ? item.value : ''"
                        :value="getOutputValue(item)" />
                </template>
                <template v-else>
                    <no-data />
                </template>
            </div>
        </section>
        <!-- 异常信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.errorInfo }}</h2>
            <div class="bk-text-list">
                <van-cell v-if="nodeDetail.ex_data" :value="transformFailInfo(nodeDetail.ex_data)" />
                <no-data v-else />
            </div>
        </section>
        <!-- 执行记录 -->
        <section
            class="bk-block"
            v-for="history in nodeDetail.histories"
            :key="history.index">
            <h2 class="bk-text-title">{{ i18n.executeHistory }}</h2>
            <div class="bk-text-list">
                <van-cell :title="i18n.startTime" :value="history.start_time || '--'" />
                <van-cell :title="i18n.endTime" :value="history.finish_time || '--'" />
                <van-cell :title="i18n.costTime" :value="getLastTime(history.elapsed_time)" />
            </div>
        </section>
    </div>
</template>
<script>
    import { URL_REG } from '@/constants/index.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import tools from '@/utils/tools.js'
    import NoData from '@/components/NoData/index.vue'
    import StatusIcon from '@/components/MobileStatusIcon/index.vue'
    import VueJsonPretty from 'vue-json-pretty'
    import { mapActions, mapState } from 'vuex'

    export default {
        name: 'TaskNodes',
        components: {
            VueJsonPretty,
            NoData,
            StatusIcon
        },
        data () {
            return {
                nodeDetail: { 'inputs': {} },
                status: '',
                showText: true,
                loadingIcon: true,
                i18n: {
                    loading: window.gettext('加载中...'),
                    executeInfo: window.gettext('执行信息'),
                    startTime: window.gettext('开始时间'),
                    endTime: window.gettext('结束时间'),
                    costTime: window.gettext('耗时(S)'),
                    skipped: window.gettext('失败后跳过'),
                    yes: window.gettext('是'),
                    no: window.gettext('否'),
                    ignore: window.gettext('失败后自动忽略'),
                    retryTimes: window.gettext('重试次数'),
                    inputParameter: window.gettext('输入参数'),
                    outputParameter: window.gettext('输出参数'),
                    errorInfo: window.gettext('异常信息'),
                    executeHistory: window.gettext('执行记录')
                }
            }
        },
        computed: {
            ...mapState({
                taskId: state => state.taskId,
                node: state => state.node
            })
        },
        created () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getTask',
                'getTaskStatus',
                'getNodeDetail'
            ]),

            async loadData () {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const params = {
                    taskId: this.taskId,
                    nodeId: this.node.id,
                    componentCode: this.node.componentCode
                }
                this.loadingIcon = true
                Promise.all([
                    this.getNodeDetail(params),
                    this.getTaskStatus({ id: this.taskId }),
                    this.getTask({ id: this.taskId })
                ]).then(values => {
                    if (values[0].result) {
                        this.nodeDetail = values[0].data
                        this.filterNodeInfo()
                    }
                    this.status = values[1].data.state
                    this.nodeDetail.name = values[2].name
                    this.loadingIcon = false
                    this.$toast.clear()
                }).catch(e => {
                    errorHandler(e, this)
                    this.loadingIcon = false
                    this.$toast.clear()
                })
            },

            filterNodeInfo () {
                if (this.node.component_code === 'job_execute_task') {
                    this.nodeDetail.outputs = this.nodeDetail.outputs.filter(output => {
                        const outputIndex = this.nodeDetail.inputs['job_global_var'].findIndex(prop => prop.name === output.key)
                        if (!output.preset && outputIndex === -1) {
                            return false
                        }
                        return true
                    })
                } else {
                    this.nodeDetail.outputs = this.nodeDetail.outputs.filter(output => output.preset)
                }
            },

            getLastTime (time) {
                return tools.timeTransform(time)
            },

            getOutputValue (output) {
                if (output.value === 'undefined' || output.value === '') {
                    return '--'
                } else {
                    return String(output.value)
                }
            },

            isOutputValueLink (value) {
                return URL_REG.test(value)
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
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/var.scss';
    .bk-block .status{
        .task-icon{
            vertical-align: middle;
        }
        .text{
            margin-left: 5px;
            font-size: $fs-12;
            color: $text-color-light;
        }
    }
    .parameter-info{
        background: #313238;
        color: $white;
        font-size: $fs-14;
        padding: 0 25px;
        overflow: hidden;
    }
    .view-btn{
        display: block;
        background: none;
        border-radius: 0;
        margin: 15px 25px 0 25px;
        width: calc(100% - 50px);
        font-size: $fs-14;
    }
</style>
