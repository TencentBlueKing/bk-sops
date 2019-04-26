<template>
    <div ref="nodeLocation" v-if="node.type !== 'start' && node.type !== 'end'" class="bk-flow-location" @click="onNodeClick(node, $event)">
        <div class="node-name" v-if="node.type === 'startpoint'"><p class="name">startPointstartPointstartPointstartPointstartPointstartPoint</p></div>
        <div class="node-name" v-if="node.type === 'endpoint'"><p class="name">endpoint</p></div>
        <div class="node-name" v-if="node.type === 'tasknode'"><p class="name">tasknode</p></div>
        <div class="task-name" title="步骤1" v-if="node.type !== 'start' && node.type !== 'end'">
            步骤1a步骤1步骤1步骤1步骤1步骤1步骤1步骤1步骤1步骤1
        </div>
    </div>
</template>
<script>
    export default {
        name: 'NodeTemplate',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {

            }
        },
        mounted () {
            this.showNodePosition()
        },
        methods: {
            onNodeClick (node, event) {
                console.log(node.x, node.y)
                const $tool = document.getElementById('tool' + this.node.id)
                if ($tool.style.display === 'none') {
                    $tool.style.display = ''
                } else {
                    $tool.style.display = 'none'
                }
                this.showToolPosition(node)
                event.stopPropagation()
            },
            showNodePosition () {
                const $node = document.getElementById(this.node.id)
                let left
                if (this.$refs.nodeLocation && this.$refs.nodeLocation.offsetWidth) {
                    left = $node.offsetLeft + this.$refs.nodeLocation.offsetWidth - 152
                } else {
                    left = $node.offsetLeft
                }
                $node.style.left = left + 'px'
                return left
            },
            showToolPosition (node) {
                const nodeLeft = document.getElementById(node.id).offsetLeft
                if (this.$refs.nodeLocation && this.$refs.nodeLocation.offsetWidth) {
                    const $tool = document.getElementById('tool' + this.node.id)
                    let toolLeft
                    if ($tool.offsetWidth >= this.$refs.nodeLocation.offsetWidth) {
                        toolLeft = nodeLeft - ($tool.offsetWidth - this.$refs.nodeLocation.offsetWidth) / 2
                    } else {
                        toolLeft = nodeLeft + (this.$refs.nodeLocation.offsetWidth - $tool.offsetWidth) / 2
                    }
                    $tool.style.left = toolLeft + 'px'
                }
            },
            nextNodePosition () {
                const node = this.node
                //  用于执行中的节点，状态结束后，定位到某个节点位置
                if (node.type === 'tasknode') {
                    const canvas = document.getElementById('canvas-flow')
                    const left = document.getElementById(node.id).offsetLeft
                    canvas.style.left = canvas.offsetLeft - left + 'px'
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    .bk-flow-location {
        width: 152px;
        height: 90px;
        text-align: center;
        background: $white;
        .node-name {
            width: 100%;
            font-size: $fs-12;
            height: 60px;
            line-height: 60px;
            background: #fafafa;
            border: 1px solid #a9adb5;
            overflow: hidden;
            .name{
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                padding: 0 10px;
            }
        }
        .task-name {
            height: 30px;
            line-height: 30px;
            font-size: $fs-12;
            color: $white;
            background: #53699d;
            border-top: none;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    }
    .bk-flow-location.failed {
        .node-name {
            border-color: #ff5757;
        }
        .task-name {
            background: #ff5757;
        }
    }
    .bk-flow-location.finished {
        .node-name {
            border-color: #30d878;
        }
        .task-name {
            background: #30d878;
        }
    }
    .bk-flow-location.suspended {
        .node-name {
            border-color: #f8b53f;
        }
        .task-name {
            background: #f8b53f;
        }
    }
</style>
