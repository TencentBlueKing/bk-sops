<template>
    <div
        v-if="node.type === 'startpoint'"
        :class="['node-circle', node['status'] ? node['status'].toLowerCase() : '']">
        <div class="node-type-status">{{ i18n.start }}</div>
    </div>
    <div
        v-else-if="node.type === 'endpoint'"
        :class="['node-circle', node['status'] ? node['status'].toLowerCase() : '']">
        <div class="node-type-status">{{ i18n.end }}</div>
    </div>
    <div
        v-else-if="node.type === 'tasknode'"
        ref="nodeLocation"
        :class="['bk-flow-location', node['status'] ? node['status'].toLowerCase() : '']"
        @click="onNodeClick(node, $event)">
        <div class="node-name">
            <p class="name">{{ node.name }}</p>
        </div>
        <div class="task-name">{{ node.stage_name }}</div>
    </div>
    <div
        v-else-if="node.type === 'subflow'"
        ref="nodeLocation"
        class="bk-flow-location node-subflow"
        @click="onNodeClick(node, $event)">
        <div class="node-name">
            <div class="subflow-node-icon">
                <van-icon name="plus" />
            </div>
            <p class="name">{{ node.name }}</p>
        </div>
        <div class="task-name">{{ node.stage_name }}</div>
    </div>
    <div
        v-else
        ref="nodeLocation"
        class="node-circle">
        <van-icon slot="icon" class-prefix="icon" :name="`node-${node.type}`" />
    </div>
</template>
<script>
    export default {
        name: 'MobileNodeTemplate',
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
                i18n: {
                    start: window.gettext('开始'),
                    end: window.gettext('结束')
                }
            }
        },
        mounted () {
            this.showNodePosition()
        },
        methods: {
            onNodeClick (node, event) {
                console.log(node)
                if (this.node.type !== 'subflow' && !this.node.status) {
                    return false
                }
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
                const nodeTop = document.getElementById(node.id).offsetTop
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
                if (this.$refs.nodeLocation && this.$refs.nodeLocation.offsetHeight) {
                    const $tool = document.getElementById('tool' + this.node.id)
                    const toolTop = nodeTop + this.$refs.nodeLocation.offsetHeight
                    $tool.style.top = toolTop + 'px'
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
        position: relative;
        .node-name {
            width: 100%;
            font-size: $fs-12;
            height: 60px;
            line-height: 60px;
            background: #fafafa;
            border: 1px solid #a9adb5;
            border-bottom: none;
            overflow: hidden;
            .name {
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                padding: 0 10px;
                height: 100%;
            }
        }
        .task-name {
            height: 30px;
            line-height: 30px;
            font-size: $fs-14;
            color: $white;
            background: #53699d;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    }

    .node-subflow {
        border-top: 5px solid #53699d;
        .node-name {
            height: 55px;
        }
        .subflow-node-icon {
            position: absolute;
            top: -2px;
            left: 0;
            width: 24px;
            height: 19px;
            line-height: 19px;
            color: $white;
            background: #53699d;
            > i {
                vertical-align: middle;
            }
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
        &.finished{
            border-color: #2fca55;
            color: #2fca55;
            .node-type-status{
                background: #2fca55;
            }
        }
        &.failed{
            border-color: #ea3636;
            color: #ea3636;
            .node-type-status{
                background: #ea3636;
            }
        }
        &.suspended{
            border-color: #ff9c01;
            color: #ff9c01;
            .node-type-status{
                background: #ff9c01;
            }
        }
    }
</style>
