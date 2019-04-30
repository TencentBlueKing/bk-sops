<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
    <MobileNodeCanvas ref="mobileNodeCanvas" selector="entry-item" v-model="canvasData" :is-preview="isPreview">
        <template v-slot:nodeTemplate="{ node }">
            <node-template :node="node" :is-preview="isPreview"></node-template>
            <div v-if="node.type === 'startpoint'" :class="['node-circle', isPreview ? '' : 'finished']">
                <div class="node-type-status">开始</div>
            </div>
            <div v-if="node.type === 'endpoint'" :class="['node-circle', isPreview ? '' : 'finished']">
                <van-icon slot="icon" class-prefix="icon" name="node-branchgateway" />
            </div>
        </template>
    </MobileNodeCanvas>

</template>
<script>
    import { mapState } from 'vuex'
    import MobileNodeCanvas from './MobileNodeCanvas.vue'
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
            type: 'startpoint'
        },
        {
            id: 'node74b1ec6275b60d5c22c9848466f1',
            x: 150,
            y: 0,
            type: 'tasknode'
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
            type: 'tasknode'
        },
        {
            id: 'node74b1ec6275b60d5c22c984525211',
            x: 840,
            y: 0,
            type: 'endpoint'
        }
    ]

    export default {
        name: 'MobileCanvas',
        components: {
            MobileNodeCanvas,
            NodeTemplate
        },
        props: {
            isPreview: Boolean,
            canvasData: Object
        },
        data () {
            return {

            }
        },
        computed: {
            ...mapState({
                currTask: state => state.task
            })
        },
        mounted () {
            console.log(nodes)
            console.log(lines)
            console.log(`isPreview=${this.isPreview}`)
            console.log(JSON.stringify(this.canvasData.lines))
            console.log(JSON.stringify(this.canvasData.nodes))
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
        font-size: 30px;
        color: #53699d;
        text-align: center;
        background: #fff;
        border-radius: 50%;
        border: 1px dashed #b1b5bc;
        .icon{
            display: block;
            margin-top: 14px;
        }
        .node-type-status{
            background: #53699d;
            border-radius: 25px;
            display: block;
            font-size: $fs-12;
            color: $white;
            width: 50px;
            height: 50px;
            line-height: 50px;
            vertical-align: middle;
            margin: 4px;
        }
    }
    .finished{
        border-color: #2fca55;
        color: #2fca55;
    }
    .failed{
        border-color: #ea3636;
        color: #ea3636;
    }
    .suspended{
        border-color: #ff9c01;
        color: #ff9c01;
    }
</style>
