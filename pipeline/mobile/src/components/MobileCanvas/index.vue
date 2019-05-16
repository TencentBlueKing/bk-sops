<template>
    <div class="page-home">
        <js-flow
            ref="jsFlow"
            selector="entry-item"
            :show-palette="false"
            :show-tool="false"
            v-model="canvasData"
            :editable="editable"
            :endpoint-options="endpointOptions"
            :connector-options="connectorOptions"
            @onNodeClick="onNodeClick">
            <template v-slot:nodeTemplate="{ node }">
                <mobile-node-template :node="node"></mobile-node-template>
            </template>
        </js-flow>
    </div>
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
        mounted () {
            const lineMap = this.getLineMap(this.canvasData)
            const overlayConfig = {
                type: 'label',
                name: '',
                cls: 'branch-conditions',
                editable: false,
                location: '-60'
            }
            const gateways = this.canvasData.gateways
            if (Object.keys(gateways).length) {
                this.canvasData.nodes.forEach(node => {
                    if (node.type === 'branchgateway') {
                        const { conditions } = gateways[node.id]
                        for (const c of Object.keys(conditions)) {
                            const line = lineMap.get(c)
                            const overlay = Object.assign({}, overlayConfig, { name: conditions[c].evaluate })
                            console.log('before draw branch gateway')
                            console.log(line)
                            console.log(overlay)
                            this.$refs.jsFlow.setCanvasPosition(-300)
                            this.$refs.jsFlow.addLineOverlay(line, overlay)
                        }
                    }
                })
            }
        },
        methods: {
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
            }

        }

    }
</script>
