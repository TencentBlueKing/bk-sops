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
    <js-flow
        selector="palette-item"
        :canvas-data="{}"
        :show-palette="showPalette"
        :show-tool="showTool"
        :editable="editable"
        @onToolClick="onToolClick">
        <template
            v-slot:palettePanel>
            <palettePanel
                :atom-type-list="atomTypeList">
            </palettePanel>
        </template>
        <template v-slot:toolPanel>
            <toolPanel></toolPanel>
        </template>
        <template v-slot:nodeTemplate="{ node }">
            <node-template :node="node"></node-template>
        </template>
    </js-flow>
</template>
<script>
    import JsFlow from '@/assets/js/jsflow.esm.js'
    import NodeTemplate from './NodeTemplate'
    import PalettePanel from './PalettePanel'
    import ToolPanel from './ToolPanel'

    export default {
        name: 'TemplateCanvas',
        components: {
            JsFlow,
            NodeTemplate,
            PalettePanel,
            ToolPanel
        },
        props: {
            data: {
                type: Object,
                default () {
                    return {
                        lines: [],
                        locations: []
                    }
                }
            },
            showPalette: {
                type: Boolean,
                default: true
            },
            showTool: {
                type: Boolean,
                default: true
            },
            editable: {
                type: Boolean,
                default: true
            },
            atomTypeList: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        methods: {
            onToolClick () {}
        }
    }
</script>
<style lang="scss" scoped>
    .jsflow {
        border: none;
        /deep/ .adding-node {
            z-index: 4;
        }
    }
</style>
