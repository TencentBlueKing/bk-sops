/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div
        class="entry-item"
        :data-config-atom-id="type === 'tasknode' ? node.code : node.template_id"
        :data-config-name="node.name.replace(/\s/g, '')"
        :data-config-group="node.group_name"
        :data-config-icon="node.group_icon"
        :data-type="type">
        <div v-if="node.plugin_type" class="plugin-item">
            <img class="plugin-logo" :src="node.logo_url" alt="">
            <div>
                <p class="plugin-title" v-bk-overflow-tips>{{ node.nodeName }}</p>
                <p class="plugin-code">{{ node.name }}</p>
            </div>
        </div>
        <div v-else class="name-wrapper">{{node.name}}</div>
    </div>
</template>
<script>

    export default {
        name: 'NodeItem',
        props: {
            type: {
                type: String,
                default: ''
            },
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .plugin-item {
        min-height: 70px;
        display: flex;
        align-items: center;
        cursor: move;
        padding: 0 7px 0 13px;
        background: #fff;
        border-bottom: 1px solid #e2e4ed;
        color: #63656e;
        .plugin-logo {
            flex-shrink: 0;
            width: 32px;
            height: 32px;
            margin-right: 12px;
        }
        .plugin-title {
            font-size: 14px;
            font-weight: 700;
            line-height: 19px;
            margin-bottom: 4px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        .plugin-code {
            font-size: 12px;
        }
        &:hover {
            background: hsl(218, 100%, 94%);
        }
    }
</style>
