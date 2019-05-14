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
                        lines: []
                    }
                }
            },
            editable: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                endpointOptions: endpointOptions,
                connectorOptions: connectorOptions
            }
        },
        created () {
            console.log(this.canvasData)
            console.log(this.editable)
        },
        mounted () {
            // this.$refs.jsFlow.setCanvasPosition(100, 200)
        },
        methods: {
            onNodeClick () {
                console.log(1)
            }
        }
    }

</script>
