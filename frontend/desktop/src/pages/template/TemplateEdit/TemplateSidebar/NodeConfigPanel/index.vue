<template>
    <div class="node-config-panel" :style="{ width: `${sideWidth}px` }">
        <h4 class="panel-title">{{$t('节点配置')}}</h4>
        <bk-tab :active.sync="activeTab" type="unborder-card" :label-height="42">
            <bk-tab-panel name="pluginConfig" :label="isSubFlow ? $t('子流程配置') : $t('插件配置')">
            </bk-tab-panel>
            <bk-tab-panel name="controlOption" :label="$t('流程控制选项')">
            </bk-tab-panel>
        </bk-tab>
        <PluginConfig
            :active-tab="activeTab"
            :is-not-exist-atom-or-version="isNotExistAtomOrVersion"
            :node-id="nodeId"
            :is-view-mode="isViewMode"
            :project_id="project_id"
            :atom-list="atomList"
            :atom-type-list="atomTypeList"
            :third-party-list="thirdPartyList"
            :common="common"
            :isolation-atom-config="isolationAtomConfig"
            @updateNodeInfo="updateNodeInfo"
            @close="$emit('close')"
            @onSelectorPanelShow="isSelectorPanelShow = $event">
        </PluginConfig>
        <!--可拖拽-->
        <template>
            <div class="resize-trigger" @mousedown.left="handleMousedown($event)"></div>
            <i :class="['resize-proxy', 'left']" ref="resizeProxy"></i>
            <div class="resize-mask" ref="resizeMask"></div>
        </template>
    </div>
</template>

<script>
    import { mapState } from 'vuex'
    import PluginConfig from './PluginConfig.vue'
    export default {
        name: 'NodeConfigPanel',
        components: {
            PluginConfig
        },
        props: {
            project_id: [String, Number],
            isNotExistAtomOrVersion: Boolean,
            nodeId: String,
            atomList: Array,
            atomTypeList: Object,
            thirdPartyList: Object,
            common: [String, Number],
            isViewMode: Boolean,
            isolationAtomConfig: Object
        },
        data () {
            return {
                activeTab: 'pluginConfig',
                isSelectorPanelShow: false,
                sideWidth: 560,
                varPanelWidth: 0
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities
            }),
            isSubFlow () {
                const nodeConfig = this.activities[this.nodeId]
                return nodeConfig.type !== 'ServiceActivity'
            }
        },
        methods: {
            updateNodeInfo (id, data) {
                this.$emit('updateNodeInfo', id, data)
            },
            handleMousedown (event) {
                this.updateResizeMaskStyle()
                this.updateResizeProxyStyle()
                document.addEventListener('mousemove', this.handleMouseMove)
                document.addEventListener('mouseup', this.handleMouseUp)
            },
            handleMouseMove (event) {
                const varPanelDom = document.querySelector('.variable-panel')
                const { width: varPanelWidth } = varPanelDom.getBoundingClientRect()
                const maxWith = window.innerWidth - 400
                const minWidth = varPanelWidth + 600
                let width = window.innerWidth - event.clientX
                width = width > maxWith ? maxWith : width
                width = width < minWidth ? minWidth : width
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.right = `${width}px`
            },
            updateResizeMaskStyle () {
                const resizeMask = this.$refs.resizeMask
                resizeMask.style.display = 'block'
                resizeMask.style.cursor = 'col-resize'
            },
            updateResizeProxyStyle () {
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'visible'
                const tplSideDom = document.querySelector('.template-side')
                const { width: tplSideWidth } = tplSideDom.getBoundingClientRect()
                resizeProxy.style.right = `${tplSideWidth}px`
            },
            handleMouseUp () {
                const resizeMask = this.$refs.resizeMask
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'hidden'
                resizeMask.style.display = 'none'
                const varPanelDom = document.querySelector('.variable-panel')
                const { width: varPanelWidth } = varPanelDom.getBoundingClientRect()
                const right = resizeProxy.style.right.slice(0, -2)
                this.sideWidth = Number(right) - varPanelWidth
                document.removeEventListener('mousemove', this.handleMouseMove)
                document.removeEventListener('mouseup', this.handleMouseUp)
            }
        }
    }
</script>

<style lang="scss" scoped>
    .node-config-panel {
        display: flex;
        flex-direction: column;
        min-width: 560px;
        background: #fff;
        box-shadow: -1px 0 0 0 #dcdee5;
        .panel-title {
            padding-left: 40px;
            margin: 14px 0 2px;
            color: #313238;
            line-height: 24px;
        }
        /deep/.bk-tab {
            .bk-tab-label-wrapper {
                margin-left: 19px;
            }
            .bk-tab-section {
                padding: 0;
            }
        }
        .resize-trigger {
            width: 5px;
            height: 100vh;
            position: absolute;
            left: 0;
            top: 60px;
            cursor: col-resize;
            z-index: 3;
            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                bottom: 0;
                width: 1px;
                background-color: #dcdee5;
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
        .resize-proxy {
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
        .resize-mask {
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
