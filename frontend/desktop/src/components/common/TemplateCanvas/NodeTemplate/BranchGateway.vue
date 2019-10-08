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
    <el-tooltip placement="bottom" popper-class="task-node-tooltip" :disabled="!isOpenTooltip">
        <div
            :class="[
                'gateway-node',
                'branch-gateway',
                node.status ? node.status.toLowerCase() : ''
            ]">
            <div class="node-type-icon common-icon-node-branchgateway"></div>
        </div>
        <div id="node-tooltip-content" slot="content">
            <bk-button @click.stop="onGatewaySelectionClick">{{ i18n.skip }}</bk-button>
        </div>
    </el-tooltip>
</template>
<script>
    export default {
        name: 'BranchGateway',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                i18n: {
                    skip: gettext('跳过')
                }
            }
        },
        computed: {
            isOpenTooltip () {
                return this.node.status === 'FAILED'
            }
        },
        methods: {
            onGatewaySelectionClick () {
                this.$emit('onGatewaySelectionClick', this.node.id)
            }
        }
    }
</script>
