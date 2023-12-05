<template>
    <div class="node-config-panel" :style="{ width: `${width}px`, background: varPanelActivated ? '#fafbfd' : '#fff' }">
        <h4 class="panel-title">{{$t('节点配置')}}</h4>
        <i class="bk-icon icon-angle-right-line close-panel-icon" @click="$emit('close')"></i>
        <bk-tab :active.sync="activeTab" type="unborder-card" :label-height="42">
            <bk-tab-panel name="pluginConfig" :label="isSubFlow ? $t('子流程配置') : $t('插件配置')">
            </bk-tab-panel>
            <bk-tab-panel name="controlOption" :label="$t('流程控制选项')">
            </bk-tab-panel>
        </bk-tab>
        <PluginConfig
            ref="pluginConfig"
            :active-tab="activeTab"
            :is-not-exist="isNotExist"
            :node-id="nodeId"
            :is-view-mode="isViewMode || varPanelActivated"
            :project_id="project_id"
            :atom-list="atomList"
            :atom-type-list="atomTypeList"
            :common="common"
            :isolation-atom-config="isolationAtomConfig"
            @onViewCited="$emit('onViewCited', $event)"
            @selectorPanelToggle="$emit('selectorPanelToggle', $event)"
            @updateNodeInfo="updateNodeInfo"
            @close="$emit('close')">
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
    import { mapMutations, mapState, mapActions } from 'vuex'
    import PluginConfig from './PluginConfig.vue'
    export default {
        name: 'NodeConfigPanel',
        components: {
            PluginConfig
        },
        props: {
            project_id: [String, Number],
            nodeId: String,
            atomList: Array,
            atomTypeList: Object,
            common: [String, Number],
            isViewMode: Boolean,
            width: Number
        },
        data () {
            return {
                activeTab: 'pluginConfig',
                isSelectorPanelShow: false,
                varPanelWidth: 0,
                isolationAtomConfig: {},
                isNotExist: false
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'locations': state => state.template.location,
                'thirdPartyList': state => state.template.thirdPartyList,
                'varPanelActivated': state => state.template.varPanelActivated
            }),
            isSubFlow () {
                const nodeConfig = this.activities[this.nodeId]
                return nodeConfig.type !== 'ServiceActivity'
            }
        },
        created () {
            this.initLoad()
        },
        beforeDestroy () {
            this.setVarPanelActivated(false)
        },
        methods: {
            ...mapMutations('template', [
                'setVarPanelActivated',
                'setThirdPartyList'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceMeta'
            ]),
            async initLoad (id = this.nodeId) {
                this.isolationAtomConfig = { list: [] }
                // 判断节点配置的插件是否存在
                const nodeConfig = this.activities[id]
                if (nodeConfig && nodeConfig.type === 'ServiceActivity' && nodeConfig.name && nodeConfig.component.code !== 'remote_plugin') {
                    let atom = null
                    atom = this.atomList.find(item => item.code === nodeConfig.component.code)
                    // 插件列表中未匹配到，1.该插件被移除 2.该插件被隔离
                    if (!atom) {
                        const resp = await this.loadAtomConfig({
                            atom: nodeConfig.component.code,
                            version: nodeConfig.component.version,
                            project_id: this.common ? undefined : this.project_id,
                            scope: 'flow'
                        }).catch(() => {
                            this.isNotExist = true
                        })
                        // 隔离插件允许拉取详情数据
                        if (resp) {
                            this.isNotExist = false
                            // 被隔离插件的基础配置
                            this.isolationAtomConfig = {
                                ...resp.data,
                                list: [resp.data]
                            }
                        }
                    } else {
                        const matchResult = atom.list.find(item => item.version === nodeConfig.component.version)
                        this.isNotExist = !matchResult
                    }
                }
                const location = this.locations.find(item => item.id === id)
                if (['tasknode', 'subflow'].includes(location.type)) {
                    // 设置第三发插件缓存
                    const nodeConfig = this.activities[id]
                    if (nodeConfig.component
                        && nodeConfig.component.code === 'remote_plugin'
                        && !this.thirdPartyList[id]) {
                        const resp = await this.loadPluginServiceMeta({ plugin_code: nodeConfig.component.data.plugin_code.value })
                        // 第三方插件是否存在
                        if (!resp.result && resp.message.indexOf('404') > -1) {
                            this.isNotExist = true
                            return
                        }
                        const { code, versions, description } = resp.data
                        const versionList = versions.map(version => {
                            return { version }
                        })
                        const { data } = nodeConfig.component
                        let version = data && data.plugin_version
                        version = version && version.value
                        const group = {
                            code,
                            list: versionList,
                            version,
                            desc: description
                        }
                        // 第三方插件版本是否存在
                        if (versions.includes(version)) {
                            this.setThirdPartyList({ id, value: group })
                        } else {
                            this.isNotExist = true
                        }
                    }
                }
            },
            updateNodeInfo (id, data) {
                this.$emit('updateNodeInfo', id, data)
            },
            close () {
                const { isDataChange } = this.$refs.pluginConfig || {}
                return isDataChange
            }
        }
    }
</script>

<style lang="scss" scoped>
    .node-config-panel {
        display: flex;
        flex-direction: column;
        min-width: 480px;
        background: #fff;
        box-shadow: -1px 0 0 0 #dcdee5;
        .panel-title {
            padding-left: 40px;
            margin: 14px 0 2px;
            color: #313238;
            line-height: 24px;
        }
        .close-panel-icon {
            position: absolute;
            top: 14px;
            left: -12px;
            z-index: 5;
            display: inline-block;
            height: 24px;
            width: 24px;
            font-size: 12px;
            text-align: center;
            line-height: 24px;
            color: #979ba5;
            background: #fff;
            box-shadow: 0 0 4px 0 #00000026;
            border-radius: 50%;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
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
