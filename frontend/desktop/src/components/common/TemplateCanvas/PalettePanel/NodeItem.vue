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
        <div class="name-wrapper">
            <p>{{node.name}}</p>
        </div>
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
    @import '@/scss/mixins/multiLineEllipsis.scss';

    .node-item {
        float: left;
        margin-right: 8px;
        margin-bottom: 10px;
        background: $whiteNodeBg;
        border: 1px solid $commonBorderColor;
        overflow: hidden;
        cursor: move;
        user-select: none;
        &:nth-child(2n) {
            margin-right: 0;
        }
        &:hover {
            background: $blueDashBg;
            border-color: $blueDefault;
            .name-wrapper p{
                &:after {
                    background: $blueDashBg;
                }
            }
        }
        .name-wrapper {
            display: table-cell;
            padding: 0 10px;
            width: 130px;
            height: 58px;
            vertical-align: middle;
            p {
                @include multiLineEllipsis($lineHeight: 1.2em, $lineCount: 2, $bgColor: #fafafa);
                font-size: 12px;
                color: $greyDefault;
                text-align: center;
                word-break: break-all;
                &:before {
                    right: 3px;
                }
            }
        }
    }
</style>
