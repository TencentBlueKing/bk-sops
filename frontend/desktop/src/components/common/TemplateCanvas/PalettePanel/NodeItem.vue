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
    <div
        class="node-item entry-item"
        :data-config-atom-id="type === 'tasknode' ? node.code : node.template_id"
        :data-config-version="type === 'tasknode' ? '' : node.version"
        :data-config-name="node.name.replace(/\s/g, '')"
        :data-config-group="node.group_name"
        :data-config-icon="node.group_icon"
        :data-type="type">
        <div class="name-wrapper">{{node.name}}</div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'

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
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';

    .node-item {
        background: #f0f1f5;
        border-top: 1px solid #e2e4ed;
        border-radius: 2px;
        overflow: hidden;
        cursor: move;
        user-select: none;
        &:first-child {
            border-top: none;
        }
        &:hover {
            background: #fafbfd;
        }
        .name-wrapper {
            padding: 0 14px;
            height: 40px;
            line-height: 40px;
            color: #63656e;
            font-size: 12px;
        }
    }
</style>
