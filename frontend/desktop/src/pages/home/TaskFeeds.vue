/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="task-feeds-content">
        <h3 class="title">{{i18n.feeds}}</h3>
        <router-link class="view-more-task" :to="`/taskflow/home/${cc_id}/`">{{i18n.viewMore}}</router-link>
        <div v-if="topThreeTaskFeeds.length" class="feed-container">
            <ul class="feed-list">
                <li v-for="(item, index) in topThreeTaskFeeds" :key="item.id" class="feed-item">
                    <div class="item-mark-icon">
                        <i class="common-icon-clock"></i>
                    </div>
                    <div :class="['task-status', feedsStatus[index].cls]">
                        <i :class="[feedsStatus[index].icon, 'status-icon']"></i>
                        <span class="status-name">
                            {{feedsStatus[index].text}}
                        </span>
                    </div>
                    <div class="action-title">
                        <p>{{getActionTitle(item)}}</p>
                    </div>
                    <div class="action-detail">
                        [{{item.finish_time || item.create_time}}]{{item.name}}, {{i18n.time}} {{getLastTime(item)}}
                    </div>
                    <router-link class="goto-task-detail" :to="`/taskflow/execute/${cc_id}/?instance_id=${item.id}`">{{i18n.detail}}</router-link>
                </li>
                <li class="feed-item feed-end">
                    <div class="item-mark-icon">
                        <i class="common-icon-clock"></i>
                    </div>
                </li>
            </ul>
        </div>
        <div class="feeds-empty" v-else>
            <NoData></NoData>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import NoData from '@/components/common/base/NoData.vue'
    import tools from '@/utils/tools.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    export default {
        name: 'TaskFeeds',
        components: {
            NoData
        },
        props: ['topThreeTaskFeeds', 'cc_id'],
        data () {
            return {
                feedsStatus: this.getTaskStatus(),
                i18n: {
                    feeds: gettext('业务动态'),
                    viewMore: gettext('查看更多'),
                    detail: gettext('查看详情'),
                    time: gettext('耗时')
                }
            }
        },
        methods: {
            ...mapActions('task/', [
                'getInstanceStatus'
            ]),
            getActionTitle (task) {
                let action
                if (!task.is_started) {
                    action = gettext('创建了一个')
                } else {
                    action = gettext('执行了一个')
                }
                const type = gettext(task.category_name)
                const i18n_task = gettext('任务')
                return `${task.executor_name || task.creator_name} ${action} ${type} ${i18n_task}`
            },
            getLastTime (task) {
                return tools.timeTransform(task.elapsed_time)
            },
            getTaskStatus () {
                return this.topThreeTaskFeeds.map((item, index) => {
                    const status = {}
                    if (item.is_finished) {
                        status.cls = 'finished'
                        status.icon = 'bk-icon icon-check-circle-shape'
                        status.text = gettext('完成')
                    } else if (item.is_started) {
                        status.cls = 'execute'
                        status.icon = 'common-icon-loading'
                        this.getExecuteDetail(item, index)
                    } else {
                        status.cls = 'created'
                        status.icon = 'common-icon-dark-circle-shape'
                        status.text = gettext('未执行')
                    }
                    return status
                })
            },
            async getExecuteDetail (task, index) {
                const data = {
                    instance_id: task.id,
                    cc_id: task.business.cc_id
                }
                try {
                    const detailInfo = await this.getInstanceStatus(data)
                    if (detailInfo.result) {
                        const state = detailInfo.data.state
                        const status = {}
                        switch (state) {
                            case 'RUNNING':
                            case 'BLOCKED':
                                status.cls = 'running'
                                status.icon = 'common-icon-dark-circle-ellipsis'
                                status.text = gettext('执行中')
                                break
                            case 'SUSPENDED':
                                status.cls = 'execute'
                                status.icon = 'common-icon-dark-circle-pause'
                                status.text = gettext('暂停')
                                break
                            case 'NODE_SUSPENDED':
                                status.cls = 'execute'
                                status.icon = 'common-icon-dark-circle-pause'
                                status.text = gettext('节点暂停')
                                break
                            case 'FAILED':
                                status.cls = 'failed'
                                status.icon = 'common-icon-dark-circle-close'
                                status.text = gettext('失败')
                                break
                            case 'REVOKED':
                                status.cls = 'revoke'
                                status.icon = 'common-icon-dark-circle-shape'
                                status.text = gettext('撤销')
                                break
                            default:
                                status.text = gettext('未知')
                        }
                        this.feedsStatus.splice(index, 1, status)
                    } else {
                        errorHandler(detailInfo, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/config.scss';
.task-feeds-content {
    position: relative;
    padding: 20px 0 20px 20px;
    height: 100%;
    overflow-y: auto;
    @include scrollbar;
    .title {
        margin: 0;
        padding: 4px 0;
        width: 100px;
        font-size: 16px;
        color: $whiteDefault;
        background: $blueDefault;
        text-align: center;
    }
    .view-more-task {
        position: absolute;
        right: 20px;
        top: 20px;
        font-size: 12px;
        color: #4b9aff;
    }
    .feeds-empty {
        margin-top: 140px;
    }
    .feed-list {
        margin-left: 30px;
        padding: 14px 30px;
        font-size: 14px;
        border-left: 4px solid $commonBorderColor;
        .action-detail {
            word-break: break-all;
        }
    }
    .feed-item {
        position: relative;
        margin-bottom: 20px;
        &:last-child {
            margin-bottom: 0;
        }
    }
    .feed-end {
        .item-mark-icon {
            background: #f4f4f4;
        }
    }
    .item-mark-icon {
        position: absolute;
        top: 2px;
        left: -46px;
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        background: $blueDefault;
        border-radius: 50%;
        & > i {
            font-size: 12px;
            color: $whiteDefault;
            vertical-align: middle;
        }
    }
    .task-status {
        position: absolute;
        right: 0;
        top: 6px;
        font-size: 12px;
        color: $yellowDefault;
        &.created {
            color: #979ba5;
        }
        &.running {
            color: $blueDefault;
        }
        &.finished {
            color: $greenDefault;
        }
        &.failed {
            color: $redDefault;
        }
        &.revoke {
            color: $blueDisable;
        }
        .status-icon {
            display: inline-block;
        }
        .common-icon-loading {
            animation: bk-button-loading 1.4s infinite linear;
        }
        @keyframes bk-button-loading {
            from {
                -webkit-transform: rotate(0);
                transform: rotate(0); }
            to {
                -webkit-transform: rotate(360deg);
                transform: rotate(360deg);
            }
        }
    }
    .action-title {
        font-size: 12px;
        font-weight: bold;
        line-height: 28px;
        border-bottom: 1px solid $commonBorderColor;
    }
    .action-detail {
        margin: 10px 0;
        color: #888888;
        word-break: break-all;
    }
    .goto-task-detail {
        color: #4b9aff;
    }
}
</style>
