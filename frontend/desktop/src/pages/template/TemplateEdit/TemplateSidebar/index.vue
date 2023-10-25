<template>
    <div class="template-side">
        <NodeConfig
            v-if="isNodeConfigPanelShow"
            :is-not-exist-atom-or-version="isNotExistAtomOrVersion"
            :node-id="nodeId"
            :is-view-mode="isViewMode"
            :project_id="project_id"
            :atom-list="atomList"
            :atom-type-list="atomTypeList"
            :third-party-list="thirdPartyList"
            :common="common"
            :isolation-atom-config="isolationAtomConfig"
            @close="$emit('close')"
            @updateNodeInfo="updateNodeInfo">
        </NodeConfig>
        <VariablePanel
            :is-view-mode="isViewMode"
            :common="common">
        </VariablePanel>
    </div>
</template>

<script>
    import VariablePanel from './VariablePanel/index.vue'
    import NodeConfig from './NodeConfigPanel//index.vue'
    export default {
        name: 'TemplateSidebar',
        components: {
            VariablePanel,
            NodeConfig
        },
        props: {
            isNodeConfigPanelShow: Boolean,
            isNotExistAtomOrVersion: Boolean,
            nodeId: String,
            project_id: [String, Number],
            atomList: Array,
            atomTypeList: Object,
            thirdPartyList: Object,
            common: [String, Number],
            isViewMode: Boolean,
            isolationAtomConfig: Object
        },
        methods: {
            updateNodeInfo (id, data) {
                this.$emit('updateNodeInfo', id, data)
            }
        }
    }
</script>

<style lang="scss" scoped>
.template-side {
    position: absolute;
    right: 0;
    top: 48px;
    display: flex;
    height: calc(100% - 48px);
    z-index: 10;
    /deep/.resize-trigger {
        width: 5px;
        height: 100%;
        position: absolute;
        left: 0;
        top: 0;
        cursor: col-resize;
        z-index: 3;
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            width: 1px;
            background-color: transparent;
        }
        &::after {
            content: "";
            position: absolute;
            top: 50%;
            right: -1px;
            width: 2px;
            height: 2px;
            color: #979ba5;
            transform: translate3d(0,-50%,0);
            background: currentColor;
            box-shadow: 0 4px 0 0 currentColor,0 8px 0 0 currentColor,0 -4px 0 0 currentColor,0 -8px 0 0 currentColor;
        }
        &:hover::before {
            background-color: #3a84ff;
        }
    }
    /deep/.resize-proxy {
        visibility: hidden;
        position: absolute;
        pointer-events: none;
        z-index: 9999;
        &.left {
            top: 0;
            height: 100%;
            border-left: 1px dashed #3a84ff;
        }
    }
    /deep/.resize-mask {
        display: none;
        position: fixed;
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        z-index: 9999;
    }
}
</style>
