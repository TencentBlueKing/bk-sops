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
    <!--
      画布节点模板，包括起止节点、控制节点（并行、分支、汇聚）、任务节点（标准插件、子流程）
      @params id {String} 节点唯一id
      @params type {String} 节点类型
      @params status {String} 节点状态
      @params name {String} 任务节点名称
      @params stage_name {String} 任务节点任务步骤名称
      @params optional {Boolean} 任务节点是否为可选节点
      @params mode {String} 任务节点展示模式：select(checkbox可选)、selectDisabled(checkbox禁用)、
                            edit（模板编辑状态，只有标识icon）、execute（任务执行状态）
      @params error_ignorable {Boolean} 任务节点是否可跳过
      @params isSkipped {Boolean} 任务节点错误是否被跳过
      @params isShowClockIcon {Boolean} 任务节点是否为定时节点
      @params hasUpdated {Boolean} 子流程节点是否有更新
      @params isActived {Boolean} 节点选择状态
    -->
    <div id='node-template'>
        <!-- 开始节点模板 -->
        <script type='text/x-art-template' id='startpoint-template'>
            <div class="startpoint-node node-circle <%= status || ''%>">
                <div class="node-type-status <%= status || ''%>">
                     <span class="startpoint-span"> {{i18n.startPoint}}</span>
                </div>
                <div class="common-icon-dark-circle-close" data-id=<%= id %> data-type=<%= type %>></div>
            </div>
        </script>
        <!-- 终止节点模板 -->
        <script type='text/x-art-template' id='endpoint-template'>
            <div class="endpoint-node node-circle <%= status || ''%>">
                <div class="node-type-status <%= status || ''%>">
                     <span class="endpoint-span"> {{ i18n.endPoint}}</span>
                </div>
               
                <div class="common-icon-dark-circle-close" data-id=<%= id %> data-type=<%= type %>></div>
            </div>
        </script>
        <!-- 并行网关节点模板 -->
        <script type='text/x-art-template' id='parallelgateway-template'>
            <div class='parallelgateway-node node-circle <%= status || ''%>'>
                <div class="common-icon-node-parallelgateway node-type-icon"></div>
                <div class="common-icon-dark-circle-close" data-id=<%= id %> data-type=<%= type %>></div>
            </div>
        </script>
        <!-- 汇聚网关节点模板 -->
        <script type='text/x-art-template' id='convergegateway-template'>
            <div class='convergegateway-node node-circle <%= status || ''%>'>
                <div class="common-icon-node-convergegateway node-type-icon"></div>
                <div class="common-icon-dark-circle-close" data-id=<%= id %> data-type=<%= type %>></div>
            </div>
        </script>
        <!-- 分支网关节点模板 -->
        <script type='text/x-art-template' id='branchgateway-template'>
            <div class='branchgateway-node node-circle <%= status || ''%>'>
                <div class="common-icon-node-branchgateway node-type-icon"></div>
                <div class="common-icon-dark-circle-close" data-id=<%= id %> data-type=<%= type %>></div>
            </div>
        </script>
        <!-- 标准插件节点模板 -->
        <script type='text/x-art-template' id='tasknode-template'>
            <div
                class='node-tasknode node-with-text <%= status || ''%> <%= isActived ? 'isActived' : ''%>'
                data-status=<%= status || ''%>
            >
                <div class='node-name'>
                    <p class="name" title="<%= name %>"><%= name %></p>
                </div>
                <div class="task-name" title="<%= stage_name %>">
                    <% if (stage_name) { %>
                        <%= stage_name %>
                    <% } %>
                </div>
                <div class="common-icon-dark-circle-close" data-id=<%= id %> data-type=<%= type %>></div>
                <!-- 节点右侧区域 -->
                <% if (status === 'SUSPENDED' || status === 'RUNNING') { %>
                    <div class="running-state">
                        <% if (isShowClockIcon) { %>
                            <i class="common-icon-clock"></i>
                        <% } else { %>
                        <% if (status === 'SUSPENDED') { %>
                            <i class="common-icon-double-vertical-line"></i>
                        <% } else if (status === 'RUNNING') { %>
                            <i class="common-icon-loading"></i>
                        <% }} %>
                    </div>
                <% } %>
                <!-- 节点左侧区域 -->
                <div class="task-operation">
                    <% if (optional && mode !== 'execute') { %>
                        <% if (mode === 'edit') { %>
                            <div class="task-optional">
                            </div>
                        <% } else if (mode === 'select') { %>
                            <div class="node-checkbox">
                                <input
                                    type="checkbox"
                                    <%= checked ? "checked" : ""%>
                                    id=<%= 'checkbox-' + id %>
                                    data-id=<%= id %> />
                                <label for=<%= 'checkbox-' + id %>></label>
                            </div>
                        <% } else if (mode === 'selectDisabled') { %>
                            <div class="node-checkbox">
                                <input
                                    type="checkbox"
                                    disabled
                                    <%= checked ? "checked" : ""%>
                                    id=<%= 'checkbox-' + id %>
                                    data-id=<%= id %> />
                                <label class="label-disabled" for=<%= 'checkbox-' + id %>></label>
                            </div>
                        <% } %>
                    <% } %>
                    <% if (error_ignorable && mode === 'edit') { %>
                        <div class="dark-circle common-icon-dark-circle-i">
                        </div>
                    <% } %>
                    <% if (isSkipped) { %>
                        <div class="dark-circle common-icon-dark-circle-s">
                        </div>
                    <% } %>
                    <% if (can_retry) { %>
                        <div class="dark-circle common-icon-dark-circle-r">
                        </div>
                    <% } %>
                </div>
            </div>
        </script>
        <!-- 子流程节点模板 -->
        <script type='text/x-art-template' id='subflow-template'>
            <div
                class='node-subflow node-with-text <%= status || ''%> <%= isActived ? 'isActived' : ''%>'
                data-status=<%= status || ''%>
            >
                <div class='node-name'>
                    <div class="subflow-node-icon">
                        <div class="common-icon-add"></div>
                    </div>
                    <p class="name" title="<%= name %>"><%= name %></p>
                </div>
                <div class="task-name" title="<%= stage_name %>">
                    <% if (stage_name) { %>
                        <%= stage_name %>
                    <% } %>
                </div>
                <div class="common-icon-dark-circle-close" data-id=<%= id %> data-type=<%= type %>></div>
                <!-- 子流程节点有更新标识小红点 -->
                <% if (hasUpdated) { %>
                    <span class="updated-dot"></span>
                <% } %>
                <!-- 节点右侧区域 -->
                <% if (status === 'SUSPENDED' || status === 'RUNNING') { %>
                    <div class="running-state">
                        <% if (status === 'SUSPENDED') { %>
                            <i class="common-icon-double-vertical-line"></i>
                        <% } else if (status === 'RUNNING') { %>
                            <i class="common-icon-loading"></i>
                        <% } %>
                    </div>
                <% } %>
                <!-- 节点左侧区域 -->
                <div class="task-operation">
                    <% if (optional && mode !== 'execute') { %>
                        <% if (mode === 'edit') { %>
                        <div class="task-optional">
                        </div>
                        <% } else if (mode === 'select') { %>
                            <div class="node-checkbox">
                                <input
                                    type="checkbox"
                                    <%= checked ? "checked" : ""%>
                                    id=<%= 'checkbox-' + id %>
                                    data-id=<%= id %> />
                                <label for=<%= 'checkbox-' + id %>></label>
                            </div>
                        <% } else if (mode === 'selectDisabled') { %>
                            <div class="node-checkbox">
                                <input
                                    type="checkbox"
                                    disabled
                                    <%= checked ? "checked" : ""%>
                                    id=<%= 'checkbox-' + id %>
                                    data-id=<%= id %> />
                                <label class="label-disabled" for=<%= 'checkbox-' + id %>></label>
                            </div>
                        <% } %>
                    <% } %>
                </div>
            </div>
        </script>
    </div>
</template>
<script>
import '@/utils/i18n.js'
export default {
    name: 'NodeTemplate',
    data () {
        return {
            i18n: {
                startPoint: gettext('开始'),
                endPoint: gettext('结束')
            }
        }
    }
}
</script>


