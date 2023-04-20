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
    <div :class="['gateway-node', 'parallel-gateway', node.status ? node.status.toLowerCase() : '', { 'ready': node.ready }]">
        <!-- 网关节点全选/全不选 -->
        <bk-popover placement="top" theme="light" ext-cls="gateway-select-pop" :disabled="!node.optional || node.mode !== 'select'">
            <div class="node-type-icon common-icon-node-parallelgateway"></div>
            <template slot="content">
                <span class="select-all" @click="onNodeCheckClick(true)">{{ $t('全选') }}</span>
                <span class="unselect-all" @click="onNodeCheckClick(false)">{{ $t('全不选') }}</span>
            </template>
        </bk-popover>
    </div>
</template>
<script>

    export default {
        name: 'ParallelGateway',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        methods: {
            onNodeCheckClick (value) {
                this.$emit('onNodeCheckClick', this.node.id, value)
            }
        }
    }
</script>
