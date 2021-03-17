/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <js-flow
        ref="jsFlow"
        selector="entry-item"
        :show-palette="false"
        :show-tool="false"
        v-model="canvasData"
        :editable="editable"
        :endpoint-options="endpointOptions"
        :connector-options="connectorOptions">
        <template v-slot:nodeTemplate="{ node }">
            <mobile-node-template :node="node" @nodeClick="onNodeClick"></mobile-node-template>
        </template>
    </js-flow>
</template>

<script>

    import JsFlow from './jsflow.esm.js'
    import MobileNodeTemplate from './MobileNodeTemplate.vue'
    import { endpointOptions, connectorOptions } from './options.js'

    export default {
        name: 'MobileCanvas',
        components: {
            MobileNodeTemplate,
            JsFlow
        },
        props: {
            canvasData: {
                type: Object,
                default () {
                    return {
                        nodes: [],
                        lines: [],
                        gateways: {}
                    }
                }
            },
            editable: {
                type: Boolean,
                default: false // 移动端默认false
            }
        },
        data () {
            return {
                endpointOptions: endpointOptions,
                connectorOptions: connectorOptions
            }
        },
        watch: {
            canvasData (val) {
                this.$refs.jsFlow.resetPosition()
                this.$store.commit('setTitle', '子流程')
                this.init()
            }
        },
        mounted () {
            this.init()
        },
        methods: {
            init () {
                const lineMap = this.getLineMap(this.canvasData)
                const overlayConfig = {
                    type: 'Label',
                    name: '',
                    cls: 'branch-condition',
                    editable: false,
                    location: '-60'
                }
                const gateways = this.canvasData.gateways
                this.canvasData.nodes.forEach(node => {
                    if (node.type === 'branchgateway') {
                        const { conditions } = gateways[node.id]
                        for (const c of Object.keys(conditions)) {
                            const line = lineMap.get(c)
                            const overlay = Object.assign({}, overlayConfig, { name: conditions[c].evaluate })
                            this.$refs.jsFlow.addLineOverlay(line, overlay)
                        }
                    } else if (node.type === 'tasknode') {
                        if (node.status === 'RUNNING' || node.status === 'FAILED') {
                            this.setCanvasPosition(node)
                        }
                    }
                })
            },
            setCanvasPosition (node) {
                // 屏幕宽度
                const screenWidth = window.innerWidth
                const x = this.calcNodePosition({ x: node.x, screenWidth: screenWidth })
                this.$refs.jsFlow.setCanvasPosition(x)
            },

            calcNodePosition ({ x = 0, screenWidth = 375, nodeWidth = 152 } = {}) {
                return x * -1 + screenWidth / 2 - nodeWidth / 2
            },

            getLineMap ({ lines = [] }) {
                const map = new Map()
                lines.forEach((line) => map.set(line.id, line))
                return map
            },
            onNodeClick (node) {
                this.$emit('nodeClick', node)
            }
        }

    }
</script>

<style lang="scss">
    .branch-condition {
        padding: 3px 8px;
        min-width: 60px;
        max-width: 120px;
        font-size: 12px;
        text-align: center;
        background: #e1f3ff;
        border: 1px solid #c3cdd7;
        border-radius: 2px;
        z-index: 1;
    }

    .page-view {
        .task-status{
            +.jsflow{
                top: 41px;
                position: absolute;
                width: 100%;
                height: auto;
                bottom: 0;
            }
        }
        .jsflow{
            border: none;
        }
    }
</style>
