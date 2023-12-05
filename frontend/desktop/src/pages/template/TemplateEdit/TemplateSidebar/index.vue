<template>
    <div class="template-side" :class="{ 'side-edit-active': isNodeConfigPanelShow || varPanelActivated }">
        <div class="side-content" v-bk-clickoutside="handleClickOutside">
            <NodeConfig
                v-if="isNodeConfigPanelShow"
                ref="nodeConfig"
                :is-not-exist-atom-or-version="isNotExistAtomOrVersion"
                :node-id="nodeId"
                :is-view-mode="isViewMode"
                :project_id="project_id"
                :atom-list="atomList"
                :atom-type-list="atomTypeList"
                :third-party-list="thirdPartyList"
                :common="common"
                :isolation-atom-config="isolationAtomConfig"
                :width="nodeConfigPanelWidth"
                @close="$emit('close')"
                @onViewCited="onViewCited"
                @selectorPanelToggle="selectPanelShow = $event"
                @updateNodeInfo="updateNodeInfo">
            </NodeConfig>
            <VariablePanel
                ref="variablePanel"
                :is-view-mode="isViewMode"
                :common="common"
                :width="variablePanelWidth"
                :is-node-config-panel-show="isNodeConfigPanelShow"
                @onCitedNodeClick="$emit('onCitedNodeClick', $event)"
                @handleMousedown="handleMousedown"
                @updateWidth="updateVariablePanelWidth">
            </VariablePanel>
            <!--可拖拽样式-->
            <template>
                <div
                    v-if="isNodeConfigPanelShow"
                    class="resize-trigger"
                    @mousedown.left="handleMousedown('tplSide')">
                </div>
                <i :class="['resize-proxy', 'left']" ref="resizeProxy"></i>
                <div class="resize-mask" ref="resizeMask"></div>
            </template>
        </div>
        <!--遮罩-->
        <div v-if="isNodeConfigPanelShow || varPanelActivated" class="side-mask"></div>
    </div>
</template>

<script>
    import VariablePanel from './VariablePanel/index.vue'
    import NodeConfig from './NodeConfigPanel//index.vue'
    import dom from '@/utils/dom.js'
    import { mapState } from 'vuex'

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
        data () {
            return {
                resizePanel: '', // 正在拖拽的面板
                nodeConfigPanelWidth: 600, // 默认600 最小480
                variablePanelWidth: 180, // 默认180
                selectPanelShow: false // 插件选择面板是否打开
            }
        },
        computed: {
            ...mapState({
                'infoBasicConfig': state => state.infoBasicConfig,
                'varPanelActivated': state => state.template.varPanelActivated
            })
        },
        watch: {
            selectPanelShow (val) {
                if (val) {
                    const maxWith = window.innerWidth - 880
                    const { width } = document.querySelector('.template-side').getBoundingClientRect()
                    if (width > maxWith) {
                        this.variablePanelWidth = 0
                        if (this.nodeConfigPanelWidth > maxWith) {
                            this.nodeConfigPanelWidth = maxWith
                        }
                    }
                }
            }
        },
        mounted () {
            window.addEventListener('resize', this.handlerWindowResize, false)
        },
        beforeDestroy () {
            window.removeEventListener('resize', this.handlerWindowResize, false)
        },
        methods: {
            onViewCited (data) {
                const variablePanel = this.$refs.variablePanel
                variablePanel.openVarCitedInfo(data.id)
            },
            updateNodeInfo (id, data) {
                this.$emit('updateNodeInfo', id, data)
            },
            handleMousedown (type) {
                this.resizePanel = type
                this.updateResizeMaskStyle()
                this.updateResizeProxyStyle()
                document.addEventListener('mousemove', this.handleMouseMove)
                document.addEventListener('mouseup', this.handleMouseUp)
            },
            handleMouseMove (event) {
                let maxWith = window.innerWidth - (this.selectPanelShow ? 880 : 560) // 最大宽度（节点配置面板+变量面板）
                let minWidth = 0
                if (this.resizePanel === 'tplSide') {
                    const varPanelDom = document.querySelector('.variable-panel')
                    const { width: varPanelWidth } = varPanelDom.getBoundingClientRect()
                    minWidth = varPanelWidth + 480 // 最小宽度（节点配置面板最小宽 + 变量面板）
                } else {
                    maxWith = this.isNodeConfigPanelShow ? maxWith - 480 : maxWith // 变量面板的最大宽度
                }
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
                const panelDom = this.resizePanel === 'tplSide'
                    ? document.querySelector('.template-side')
                    : document.querySelector('.variable-panel')
                const { width } = panelDom.getBoundingClientRect()
                resizeProxy.style.right = `${width}px`
            },
            handleMouseUp () {
                const resizeMask = this.$refs.resizeMask
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'hidden'
                resizeMask.style.display = 'none'
                let right = resizeProxy.style.right.slice(0, -2)
                right = Number(right)

                const panelDom = this.resizePanel === 'tplSide'
                    ? document.querySelector('.variable-panel')
                    : document.querySelector('.template-side')
                const { width } = panelDom.getBoundingClientRect()

                if (this.isNodeConfigPanelShow) {
                    if (this.resizePanel === 'tplSide') {
                        this.nodeConfigPanelWidth = right - width
                        this.variablePanelWidth = width
                    } else {
                        right = right > 180 ? right : 0
                        this.nodeConfigPanelWidth = width - right > 480 ? width - right : 480
                        this.variablePanelWidth = right
                    }
                } else {
                    this.nodeConfigPanelWidth = 0
                    this.variablePanelWidth = right > 180 ? right : 0
                }
                this.resizePanel = ''
                document.removeEventListener('mousemove', this.handleMouseMove)
                document.removeEventListener('mouseup', this.handleMouseUp)
            },
            updateVariablePanelWidth (width) {
                this.variablePanelWidth = width
                const { width: sideWidth } = document.querySelector('.template-side').getBoundingClientRect()
                this.nodeConfigPanelWidth = sideWidth - width
            },
            handlerWindowResize () {
                if (this.selectPanelShow) {
                    const maxWith = window.innerWidth - 880
                    const { width } = document.querySelector('.template-side').getBoundingClientRect()
                    if (width > maxWith) {
                        this.variablePanelWidth = 0
                        if (this.nodeConfigPanelWidth > maxWith) {
                            this.nodeConfigPanelWidth = maxWith
                        }
                    }
                }
            },
            handleClickOutside (e) {
                if (!this.varPanelActivated && !this.isNodeConfigPanelShow) return

                // 如果插件选择面板打开时，不进行后续操作
                const selectPanelDom = document.querySelector('.select-panel')
                if (selectPanelDom) return

                if (dom.parentClsContains('side-mask', e.target)
                    || dom.parentClsContains('template-header-wrapper', e.target)
                ) {
                    // 先校验变量面板再校验节点配置面板
                    const variablePanel = this.$refs.variablePanel
                    let isChange = variablePanel.close()
                    if (isChange || !this.isNodeConfigPanelShow) return
                    const nodeConfig = this.$refs.nodeConfig
                    isChange = nodeConfig.close()
                    if (isChange) {
                        this.$bkInfo({
                            ...this.infoBasicConfig,
                            confirmFn: () => {
                                this.$emit('close', false)
                                this.updateNodeInfo(this.nodeId, { isActived: false })
                            }
                        })
                    } else {
                        this.$emit('close', false)
                        this.updateNodeInfo(this.nodeId, { isActived: false })
                    }
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
.template-side {
    position: absolute;
    right: 0;
    top: 48px;
    height: calc(100% - 48px);
    z-index: 10;
    .side-content {
        display: flex;
        height: 100%;
    }
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
    &.side-edit-active {
        z-index: 112;
        .side-content {
            position: relative;
            z-index: 113;
        }
        .side-mask {
            position: fixed;
            height: 100vh;
            width: 100vw;
            top: 60px;
            left: 0;
            z-index: 112;
        }
    }
}
</style>
