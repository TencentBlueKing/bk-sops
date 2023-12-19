/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <page-header class="operation-header">
        <div class="head-left-area">
            <i class="bk-icon icon-arrows-left back-icon" @click="onBack"></i>
            <bk-popover theme="light" placement="bottom-start" :disabled="!isStateDetailShow" ext-cls="state-detail-tips">
                <span v-if="stateStr" :class="['task-state', state]">
                    {{ stateStr }}
                    <i v-if="isStateDetailShow" class="common-icon-info"></i>
                </span>
                <dl slot="content" class="task-state-detail" id="task-state-detail">
                    <dt>{{$t('状态明细')}}</dt>
                    <template v-if="pendingNodes.length">
                        <dd
                            v-for="item in pendingNodes"
                            :key="item.id">
                            <i class="bk-icon icon-circle"></i>
                            <span class="node-name" v-bk-overflow-tips @click="$emit('moveNodeToView', item.id)">{{ item.name }}</span>
                            <span class="task-state">{{ item.statusText }}</span>
                        </dd>
                    </template>
                    <dd v-else>{{ '--' }}</dd>
                </dl>
            </bk-popover>
            <div class="bread-crumbs-wrapper">
                <span
                    class="path-item name-ellipsis"
                    v-for="(path, index) in nodeNav"
                    :key="path.id"
                    v-bk-overflow-tips
                    :title="showNodeList.includes(index) ? path.name : ''">
                    <span v-if="!!index && showNodeList.includes(index) || index === 1">/</span>
                    <span v-if="showNodeList.includes(index)" class="node-name" :title="path.name" @click="onSelectSubflow(path.id)">
                        {{path.name}}
                    </span>
                    <span class="node-ellipsis" v-else-if="index === 1">...</span>
                </span>
            </div>
            <div class="task-operation-btns" v-show="state !== 'FINISHED'">
                <div
                    v-for="operation in taskOperationBtns"
                    :key="operation.action"
                    class="operation-btn">
                    <bk-button
                        :class="[
                            { 're-execute-btn': operation.action === 'reExecute' },
                            { 'revoke-btn': operation.action === 'revoke' }
                        ]"
                        :theme="['execute', 'pause', 'resume'].includes(operation.action) ? 'primary' : 'default'"
                        :icon="'common-icon ' + operation.icon"
                        :key="operation.action"
                        :loading="operation.loading"
                        :disabled="operation.disabled"
                        v-cursor="{ active: !hasOperatePerm(operation) }"
                        :data-test-id="`taskExecute_form_${operation.action}Btn`"
                        @click="onOperationClick(operation.action)">
                        {{ operation.text }}
                    </bk-button>
                </div>
            </div>
        </div>
        <div class="operation-container" slot="expand">
            <div class="tab-operate" @click="onViewFlow">
                <i class="common-icon-jump-link"></i>
                {{$t('查看流程')}}
            </div>
            <div class="tab-operate" @click="onTaskParamsClick('modifyParams', $t('任务入参'))">
                <i class="common-icon-enter-config"></i>
                {{$t('任务入参')}}
            </div>
            <div class="tab-operate" @click="onTaskParamsClick('operateFlow', $t('操作记录'))">
                <i class="common-icon-enter-config"></i>
                {{$t('操作记录')}}
            </div>
            <bk-popover placement="bottom-left" theme="light" ext-cls="operate-tip">
                <i class="bk-icon icon-more drop-icon-ellipsis"></i>
                <template slot="content">
                    <p v-if="state !== 'CREATED'" class="operate-item" @click="onTaskParamsClick('globalVariable', $t('全局变量'))">
                        {{ $t('全局变量') }}
                    </p>
                    <p class="operate-item" @click="onTaskParamsClick('templateData', 'Code')">
                        {{ 'Code' }}
                    </p>
                    <p v-if="adminView && engineVer === 1" class="operate-item" @click="onTaskParamsClick('taskExecuteInfo')">
                        {{ $t('流程信息') }}
                    </p>
                    <p v-if="adminView && engineVer === 2" class="operate-item" @click="$emit('onInjectGlobalVariable')">
                        {{ $t('注入全局变量') }}
                    </p>
                </template>
            </bk-popover>
        </div>
    </page-header>
</template>
<script>
    import permission from '@/mixins/permission.js'
    import PageHeader from '@/components/layout/PageHeader.vue'
    import { mapState } from 'vuex'

    export default {
        name: 'TaskOperationHeader',
        components: {
            PageHeader
        },
        mixins: [permission],
        props: [
            'nodeInfoType',
            'templateSource',
            'project_id',
            'template_id',
            'primitiveTplId',
            'primitiveTplSource',
            'nodeNav',
            'instanceActions',
            'taskOperationBtns',
            'adminView',
            'engineVer',
            'state',
            'stateStr',
            'isBreadcrumbShow',
            'isShowViewProcess',
            'paramsCanBeModify',
            'pendingNodes'
        ],
        data () {
            return {
                showNodeList: [0, 1, 2]
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode
            }),
            isStateDetailShow () {
                return ['FAILED', 'PENDING_PROCESSING'].includes(this.state)
            }
        },
        watch: {
            nodeNav (val) {
                if (val.length > 3) {
                    this.showNodeList = [0, val.length - 1, val.length - 2]
                } else {
                    this.showNodeList = [0, 1, 2]
                }
            }
        },
        methods: {
            getTplURL () {
                let routerData = ''
                const templateId = this.primitiveTplId || this.template_id
                // business 兼容老数据
                if (this.primitiveTplSource === 'business' || this.primitiveTplSource === 'project') {
                    routerData = `/template/view/${this.project_id}/?template_id=${templateId}`
                } else if (this.primitiveTplSource === 'common') {
                    routerData = `/template/common/view/${this.project_id}/?template_id=${templateId}&common=1`
                }
                return routerData
            },
            onViewFlow () {
                const url = this.getTplURL()
                window.open(url, '_blank')
            },
            onSelectSubflow (id) {
                this.$emit('onSelectSubflow', id)
            },
            onOperationClick (action) {
                this.$emit('onOperationClick', action)
            },
            onTaskParamsClick (type, name) {
                this.$emit('onTaskParamsClick', type, name)
            },
            onBack () {
                if (this.view_mode === 'appmaker') {
                    return this.$router.push({
                        name: 'appmakerTaskHome',
                        params: { type: 'edit', app_id: this.$route.params.app_id, project_id: this.project_id },
                        query: { template_id: this.$route.query.template_id }
                    })
                }
                if (this.$route.path.indexOf('/function') === 0) {
                    return this.$router.push({
                        name: 'functionHome'
                    })
                }
                if (this.$route.path.indexOf('/audit') === 0) {
                    return this.$router.push({
                        name: 'auditHome'
                    })
                }
                // 当任务执行页由创建任务路由过来时，应该返回到任务列表页
                const isFromCreate = this.$route.query.from === 'create'
                if (!isFromCreate && this.$route.name === 'taskExecute' && window.history.length > 2) {
                    return this.$router.back()
                }
                this.$router.push({
                    name: 'taskList',
                    params: { project_id: this.project_id }
                })
            },
            hasOperatePerm (operation) {
                const requestPerm = operation.action !== 'reExecute' ? 'task_operate' : this.templateSource === 'project' ? 'flow_create_task' : 'common_flow_create_task'
                return this.hasPermission([requestPerm], this.instanceActions)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';

.operation-header {
    display: flex;
    justify-content: space-between;
    padding: 0 20px 0 10px;
    .head-left-area {
        display: flex;
        align-items: center;
        .back-icon {
            font-size: 28px;
            color: #3a84ff;
            cursor: pointer;
        }
    }
    .bread-crumbs-wrapper {
        font-size: 0;
        .path-item {
            display: inline-block;
            font-size: 14px;
            overflow: hidden;
            &.name-ellipsis {
                max-width: 700px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
            .node-name {
                margin: 0 4px;
                font-size: 14px;
                color: #3a84ff;
                cursor: pointer;
            }
            .node-ellipsis {
                margin-right: 4px;
            }
            &:first-child {
                .node-name {
                    margin-left: 0px;
                }
            }
            &:last-child {
                .node-name {
                    &:last-child {
                        color: #313238;
                        cursor: text;
                    }
                }
            }
        }
    }
    .task-state {
        flex-shrink: 0;
        display: inline-block;
        margin: 0 8px;
        padding: 0 8px;
        line-height: 22px;
        font-size: 12px;
        color: #63656e;
        border-radius: 11px;
        background-color: #dcdee5;
        &.EXPIRED,
        &.CREATED {
            color: #63656e;
        }
        &.FINISHED {
            background-color: #cceed9;
            color: #2dcb56;
        }
        &.RUNNING,
        &.READY {
            background-color: #cfdffb;
            color: #3a84ff;
        }
        &.SUSPENDED, &.NODE_SUSPENDED {
            background-color: #ffe8c3;
            color: #d78300;
        }
        &.PENDING_PROCESSING {
            color: #fe9c00;
            background: #fff1db;
            i {
                font-size: 14px;
                color: #ff9c01;
            }
        }
        &.FAILED {
            background-color: #f2d0d3;
            color: #ea3636;
            i {
                font-size: 14px;
                color: #ea3636;
            }
        }
        &.REVOKED {
            background-color: #f2d0d3;
            color: #ea3636;
        }
    }
    .task-operation-btns {
        display: flex;
        align-items: center;
        .operation-btn {
            width: 108px;
            margin-left: 8px;
            /deep/.bk-button {
                width: 108px;
                font-size: 14px;
                i {
                    top: -1px;
                    font-size: 14px;
                    margin-right: 2px;
                }
                .icon-play-shape,
                .common-icon-pause {
                    font-size: 12px;
                }
                .common-icon-terminate {
                    color: #ff5656;
                }
            }
            .re-execute-btn {
                color: #3a84ff;
                border-color: #3a84ff;
            }
            &:first-child {
                margin-left: 15px;
            }
        }
    }
    .operation-container {
        display: flex;
        align-items: center;
        height: 100%;
        .tab-operate {
            display: flex;
            align-items: center;
            position: relative;
            font-size: 14px;
            line-height: 22px;
            margin-right: 33px;
            color: #63656e;
            cursor: pointer;
            i {
                font-size: 14px;
                color: #979ba5;
                margin: 2px 6px 0 0;
            }
            &:hover {
                color: #3a84ff;
                i {
                    color: #3a84ff;
                }
            }
            &::after {
                content: '';
                display: block;
                position: absolute;
                top: 3px;
                right: -16px;
                width: 1px;
                height: 16px;
                background: #dcdee5;
            }
        }
        .drop-icon-ellipsis {
            font-size: 18px;
            font-weight: 600;
            color: #979ba5;
            cursor: pointer;
            &:hover {
                color: #63656e;
            }
        }
    }
}
</style>
<style lang="scss">
.operate-tip {
    .tippy-tooltip {
        padding: 4px 0;
    }
    .operate-item {
        width: 160px;
        height: 40px;
        display: block;
        line-height: 40px;
        padding-left: 10px;
        color: #313238;
        font-size: 12px;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
            background: #eaf3ff;
        }
    }
}
.state-detail-tips {
    .tippy-tooltip {
        padding: 14px 16px 16px;
        border: 1px solid #DCDEE5;
        box-shadow: 0 2px 6px 0 #0000001a;
    }
    dt {
        font-size: 16px;
        color: #313238;
        line-height: 24px;
        margin-bottom: 16px;
    }
    dd {
        display: flex;
        align-items: center;
        font-size: 12px;
        line-height: 20px;
        margin-bottom: 8px;
        color: #3a84ff;
        i {
            flex-shrink: 0;
            margin: 2px 8px 0 0;
        }
        .node-name {
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            cursor: pointer;
        }
        .task-state {
            flex-shrink: 0;
            padding: 0 8px;
            margin-left: 8px;
            color: #979ba5;
            border-radius: 10px;
            background-color: #f0f1f5;
        }
        &:last-child {
            margin-bottom: 0;
        }
    }
}
</style>
