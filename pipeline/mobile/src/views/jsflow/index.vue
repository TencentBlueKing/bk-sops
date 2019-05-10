<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
    <MobileNodeCanvas ref="mobileNodeCanvas" selector="entry-item" v-model="canvasData" :is-="isPreview"
        @toolPanelClick="toolPanelClick">
        <template v-slot:nodeTemplate="{ node }">
            <node-template v-if="node.type !== 'startpoint' && node.type !== 'endpoint'" :node="node" :is-preview="isPreview"></node-template>
            <div v-if="node.type === 'startpoint'" :class="['node-circle', node['status'] ? node['status'].toLowerCase() : '']">
                <div class="node-type-status">{{ i18n.start }}</div>
            </div>
            <div v-if="node.type === 'endpoint'" :class="['node-circle', node['status'] ? node['status'].toLowerCase() : '']">
                <div class="node-type-status">{{ i18n.end }}</div>
            </div>
        </template>
    </MobileNodeCanvas>

</template>
<script>
    import MobileNodeCanvas from './MobileNodeCanvas.vue'
    import NodeTemplate from './NodeTemplate.vue'

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
                i18n: {
                    start: window.gettext('开始'),
                    end: window.gettext('结束')
                }
            }
        },
        methods: {
            toolPanelClick (type) {
                console.log(1)
            }
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
