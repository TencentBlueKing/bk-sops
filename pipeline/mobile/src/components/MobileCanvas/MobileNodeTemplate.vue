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
    <div v-else-if="node.type === 'tasknode'">
        <div
            ref="nodeLocation"
            :name="'tip_' + node.id"
            :class="['bk-flow-location', node['status'] ? node['status'].toLowerCase() : '']">
            <div class="node-name">
                <p class="name">{{ node.name }}</p>
            </div>
            <div class="task-name">{{ node.stage_name }}</div>
        </div>
        <Tooltips :node="node" v-if="node.status && node.status !== 'CREATED'"></Tooltips>
    </div>
    <div
        v-else-if="node.type === 'subflow'"
        ref="nodeLocation"
        :class="['bk-flow-location', 'node-subflow', node['status'] ? node['status'].toLowerCase() : '']"
        @click="onNodeClick(node, $event)">
        <div class="node-name">
            <div :class="['subflow-node-icon', node['status'] ? node['status'].toLowerCase() : '']">
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

    import Tooltips from './Tooltips.vue'

    export default {
        name: 'MobileNodeTemplate',
        components: {
            Tooltips
        },
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
                    end: window.gettext('结束'),
                    detail: window.gettext('执行详情'),
                    retry: window.gettext('重试'),
                    skip: window.gettext('跳过'),
                    sub: window.gettext('查看子流程')
                }
            }
        },
        methods: {
            onNodeClick (node) {
                const pipelineTree = this.$store.state.pipelineTree
                if (this.node.type === 'subflow') {
                    const subTree = pipelineTree.activities[node.id].pipeline
                    if (subTree) {
                        // 当前树替换成子流程树
                        this.$store.commit('setPipelineTree', subTree)
                    }
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

    .node-subflow.failed {
        border-top-color: #ff5757;
    }

    .node-subflow.finished {
        border-top-color: #30d878;
    }

    .node-subflow.suspended {
        border-top-color: #f8b53f;
    }

    .node-subflow {
        border-top-style: solid;
        border-top-width: 5px;
        border-top-color: #53699d;
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

        .subflow-node-icon.failed {
            background: #ff5757;
        }
        .subflow-node-icon.finished {
            background: #30d878;
        }
        .bsubflow-node-icon.suspended {
            background: #f8b53f;
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
