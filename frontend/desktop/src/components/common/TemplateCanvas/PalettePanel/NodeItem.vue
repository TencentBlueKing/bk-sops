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
        :data-type="type">
        <div class="name-wrapper">{{node.name}}</div>
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
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';

    .node-item {
        margin-bottom: 8px;
        background: #e1ecff;
        border: 1px solid #cbddf9;
        border-radius: 2px;
        overflow: hidden;
        cursor: move;
        user-select: none;
        &:hover {
            background: $blueDashBg;
            border-color: $blueDefault;
            .name-wrapper p{
                &:after {
                    background: $blueDashBg;
                }
            }
        }
        &:first-child {
            margin-top: 16px;
        }
        &:last-child {
            margin-bottom: 16px;
        }
        .name-wrapper {
            padding: 0 10px;
            height: 32px;
            line-height: 32px;
            color: #313238;
            font-size: 12px;
            text-align: center;
        }
    }
</style>
