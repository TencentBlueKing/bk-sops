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
    <div class="operation-header clearfix">
        <div class="operation-title">{{$t('任务执行')}}</div>
        <div class="bread-crumbs-wrapper" v-if="true">
            <span
                :class="['path-item', { 'name-ellipsis': nodeNav.length > 1 }]"
                v-for="(path, index) in nodeNav"
                :key="path.id"
                :title="showNodeList.includes(index) ? path.name : ''">
                <span v-if="!!index && showNodeList.includes(index) || index === 1">/</span>
                <span v-if="showNodeList.includes(index)" class="node-name" :title="path.name" @click="onSelectSubflow(path.id)">
                    {{path.name}}
                </span>
                <span class="node-ellipsis" v-else-if="index === 1">
                    {{ellipsis}}
                </span>
            </span>
        </div>
        <div class="operation-container clearfix">
            <div class="task-operation-btns" v-show="isTaskOperationBtnsShow">
                <template v-for="operation in taskOperationBtns">
                    <bk-button
                        :class="[
                            'operation-btn',
                            operation.action === 'revoke' ? 'revoke-btn' : 'execute-btn',
                            { 'btn-permission-disable': !hasPermission(['operate'], instanceActions, instanceOperations) }
                        ]"
                        theme="default"
                        hide-text="true"
                        :icon="'common-icon ' + operation.icon"
                        :key="operation.action"
                        :loading="operation.loading"
                        :disabled="operation.disabled"
                        v-bk-tooltips="{
                            content: operation.text,
                            placements: ['bottom']
                        }"
                        v-cursor="{ active: !hasPermission(['operate'], instanceActions, instanceOperations) }"
                        @click="onOperationClick(operation.action)">
                    </bk-button>
                </template>
            </div>
            <div class="task-params-btns">
                <i
                    :class="[
                        'params-btn',
                        'solid-eye',
                        'common-icon-solid-eye',
                        {
                            actived: nodeInfoType === 'executeInfo'
                        }
                    ]"
                    v-bk-tooltips="{
                        content: $t('查看节点详情'),
                        placements: ['bottom']
                    }"
                    @click="onTaskParamsClick('executeInfo', $t('节点详情'))">
                </i>
                <i
                    :class="[
                        'params-btn',
                        'common-icon-edit',
                        {
                            actived: nodeInfoType === 'modifyParams'
                        }
                    ]"
                    v-bk-tooltips="{
                        content: $t('修改参数'),
                        placements: ['bottom']
                    }"
                    @click="onTaskParamsClick('modifyParams', $t('修改参数'))">
                </i>
                <router-link
                    v-if="isShowViewProcess"
                    class="jump-tpl-page-btn common-icon-link"
                    target="_blank"
                    v-bk-tooltips="{
                        content: $t('查看流程'),
                        placements: ['bottom']
                    }"
                    :to="getTplURL()">
                </router-link>
                <i
                    :class="[
                        'params-btn',
                        'common-icon-flow-data',
                        {
                            actived: nodeInfoType === 'templateData'
                        }
                    ]"
                    v-bk-tooltips="{
                        content: $t('流程模板数据'),
                        placements: ['bottom']
                    }"
                    @click="onTaskParamsClick('templateData', $t('流程模板数据'))">
                </i>
                <i
                    v-if="adminView"
                    :class="[
                        'params-btn',
                        'common-icon-paper',
                        {
                            actived: nodeInfoType === 'taskExecuteInfo'
                        }
                    ]"
                    v-bk-tooltips="{
                        content: $t('流程信息'),
                        placements: ['bottom']
                    }"
                    @click="onTaskParamsClick('taskExecuteInfo')">
                </i>
                <bk-button :title="$t('返回')" @click="onBack" class="back-button">
                    {{$t('返回')}}
                </bk-button>
            </div>
        </div>
    </div>
</template>
<script>
    import permission from '@/mixins/permission.js'
    import { mapState } from 'vuex'

    export default {
        name: 'TaskOperationHeader',
        mixins: [permission],
        props: [
            'nodeInfoType',
            'templateSource',
            'project_id',
            'template_id',
            'nodeNav',
            'instanceActions',
            'taskOperationBtns',
            'instanceOperations',
            'adminView',
            'isBreadcrumbShow',
            'isTaskOperationBtnsShow',
            'isShowViewProcess'
        ],
        data () {
            return {
                showNodeList: [0, 1, 2],
                ellipsis: '...'
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode
            })
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
                // business 兼容老数据
                if (this.templateSource === 'business' || this.templateSource === 'project') {
                    routerData = `/template/edit/${this.project_id}/?template_id=${this.template_id}`
                } else if (this.templateSource === 'common') {
                    routerData = `/template/common/${this.project_id}/`
                }
                return routerData
            },
            onSelectSubflow (id) {
                this.$emit('onSelectSubflow', id)
            },
            onOperationClick (action) {
                this.$emit('onOperationClick', action)
            },
            onTaskParamsClick (type, name) {
                this.$emit('onTaskParamsClick', type, true, name)
            },
            onBack () {
                if (this.view_mode === 'appmaker') {
                    return this.$router.push({
                        name: 'appmakerTaskHome',
                        params: { type: 'edit', app_id: this.$route.params.app_id, project_id: this.project_id }
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
                this.$router.push({
                    name: 'taskList',
                    params: { project_id: this.project_id }
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';

.operation-header {
    margin: 0 20px;
    height: 50px;
    line-height: 50px;
    background: #f4f7fa;
    border-top: 1px solid #cacedb;
    .operation-title {
        float: left;
        line-height: 50px;
        font-size: 14px;
        font-weight: bold;
        color: #313238;
    }
    .bread-crumbs-wrapper {
        display: inline-block;
        margin-left: 20px;
        font-size: 14px;
        height: 50px;
        .path-item {
            display: inline-block;
            overflow: hidden;
            &.name-ellipsis {
                max-width: 190px;
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
    .operation-container {
        float: right;
        .task-operation-btns,
        .task-params-btns {
            float: left;
            .bk-button {
                border: none;
                background: transparent;
                cursor: pointer;
            }
            /deep/ .bk-icon {
                float: initial;
                top: 0;
                & + span {
                    margin-left: 0;
                }
            }
        }
        .task-operation-btns {
            margin: 9px 35px 0 0;
            line-height: initial;
            border-right: 1px solid #dde4eb;
            .operation-btn {
                margin-right: 35px;
                height: 32px;
                line-height: 32px;
                font-size: 14px;
                &.btn-permission-disable {
                    background: transparent !important;
                }
            }
            .execute-btn {
                width: 140px;
                color: #ffffff;
                background: #3a84ff; // 覆盖 bk-button important 规则
                &:hover {
                    background: #699df4; // 覆盖 bk-button important 规则
                }
                &.is-disabled {
                    color: #ffffff; // 覆盖 bk-button important 规则
                    opacity: 0.4;
                    cursor: no-drop;
                }
                &.btn-permission-disable {
                    border: 1px solid #e6e6e6;
                }
                /deep/ .bk-button-loading div {
                    background: #ffffff;
                }
            }
            .revoke-btn {
                padding: 0;
                background: transparent; // 覆盖 bk-button important 规则
                color: #ea3636;
                &:hover {
                    color: #c32929;
                }
                &.is-disabled {
                    color: #d8d8d8;
                }
            }
        }
        .task-params-btns {
            .params-btn, .jump-tpl-page-btn {
                margin-right: 36px;
                padding: 0;
                color: #979ba5;
                font-size: 15px;
                cursor: pointer;
                &.actived {
                    color: #63656e;
                }
                &:hover {
                    color: #63656e;
                }
            }
            .back-button {
                background: #ffffff;
                border: 1px solid #c4c6cc;
            }
        }
    }
}
</style>
