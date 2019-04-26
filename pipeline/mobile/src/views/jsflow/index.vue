<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
    <js-flow
        ref="jsFlow"
        selector="entry-item"
        v-model="canvasData">
        <template v-slot:nodeTemplate="{ node }">
            <node-template :node="node"></node-template>
            <div class="node-circle finished" v-if="node.type === 'start'"><van-icon name="play-circle-o"></van-icon></div>
            <div class="node-circle finished" v-if="node.type === 'end'"><van-icon name="stop-circle-o"></van-icon></div>
        </template>
    </js-flow>

</template>
<script>
    import JsFlow from './JsFlow.vue'
    import { uuid } from '../../../static/jsflow/uuid.js'
    import NodeTemplate from './NodeTemplate.vue'

    const lines = [
        {
            id: uuid('line'),
            source: {
                arrow: 'Right',
                id: 'nodeb662bc1afb5e60daa67e69f48de1'
            },
            target: {
                arrow: 'Left',
                id: 'node74b1ec6275b60d5c22c9848466f1'
            }
        },
        {
            id: uuid('line'),
            source: {
                arrow: 'Right',
                id: 'node74b1ec6275b60d5c22c9848466f1'
            },
            target: {
                arrow: 'Left',
                id: 'noded782259a6895c557a452252ec65a'
            }
        },
        {
            id: uuid('line'),
            source: {
                arrow: 'Right',
                id: 'noded782259a6895c557a452252ec65a'
            },
            target: {
                arrow: 'Left',
                id: 'noded782259a6895c557a452252ec781'
            }
        },
        {
            id: uuid('line'),
            source: {
                arrow: 'Right',
                id: 'noded782259a6895c557a452252ec781'
            },
            target: {
                arrow: 'Left',
                id: 'node74b1ec6275b60d5c22c984525211'
            }
        }
    ]
    /* 第一个节点和第二个相差130，其它节点之间相差230*/
    const nodes = [
        {
            id: 'nodeb662bc1afb5e60daa67e69f48de1',
            x: 20,
            y: 0,
            type: 'start'
        },
        {
            id: 'node74b1ec6275b60d5c22c9848466f1',
            x: 150,
            y: 0,
            type: 'endpoint'
        },
        {
            id: 'noded782259a6895c557a452252ec65a',
            x: 380,
            y: 0,
            type: 'tasknode'
        },
        {
            id: 'noded782259a6895c557a452252ec781',
            x: 610,
            y: 0,
            type: 'startpoint'
        },
        {
            id: 'node74b1ec6275b60d5c22c984525211',
            x: 840,
            y: 0,
            type: 'end'
        }
    ]

    export default {
        name: 'JsFlowIndex',
        components: {
            JsFlow,
            NodeTemplate
        },
        data () {
            return {
                nodes: nodes,
                canvasData: {
                    nodes,
                    lines
                }
            }
        },
        mounted () {
            // this.$refs.jsFlow.addLineOverlay(lines[1], {type: 'Label', name: 'test', location: -100})
            // this.$refs.jsFlow.setCanvasPosition(100, 100)

        },
        methods: {

        }
    }
</script>
<style lang="scss">
    @import '../../../static/style/app.scss';
    .node-circle{
        width: 60px;
        height: 60px;
        line-height: 60px;
        font-size: 32px;
        color: #53699d;
        text-align: center;
        background: #fafafa;
        border-radius: 50%;
        border: 1px dashed #b1b5bc;
        .van-icon{
            margin-top: 14px;
        }
    }
    .finished{
        border-color: #30d878;
        color: #30d878;
    }
</style>
