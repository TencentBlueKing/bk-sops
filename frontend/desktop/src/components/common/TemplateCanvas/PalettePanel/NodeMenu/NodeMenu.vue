/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="node-menu" v-bk-clickoutside="handleClickOutSide">
        <div class="title-wrap">
            <span>{{ menuTitle }}</span>
            <div :class="['panel-fixed-pin', { 'actived': isFixed }]" @click="isFixed = !isFixed">
                <i class="common-icon-pin"></i>
            </div>
        </div>
        <bk-tab :active.sync="crtTab" type="unborder-card">
            <bk-tab-panel
                v-for="panel in panels"
                :key="panel.id"
                :name="panel.id"
                :label="panel.name">
                <component
                    :is="panel.comp"
                    :is-show="crtTab === panel.id"
                    :common="panel.id === 'common'"
                    :built-in-plugins="builtInPlugins"
                    :template-labels="templateLabels">
                </component>
            </bk-tab-panel>
        </bk-tab>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import dom from '@/utils/dom.js'
    import BuiltInPluginList from './BuiltInPluginList.vue'
    import ThirdPartyPluginList from './ThirdPartyPluginList.vue'
    import SubflowList from './SubflowList.vue'

    const PANELS = {
        plugin: [
            { id: 'builtIn', name: i18n.t('内置插件'), comp: 'BuiltInPluginList' },
            { id: 'thirdParty', name: i18n.t('第三方插件'), comp: 'ThirdPartyPluginList' }
        ],
        subflow: [
            { id: 'project', name: i18n.t('项目流程'), comp: 'SubflowList' },
            { id: 'common', name: i18n.t('公共流程'), comp: 'SubflowList' }
        ]
    }

    export default {
        name: 'NodeMenu',
        components: {
            BuiltInPluginList,
            ThirdPartyPluginList,
            SubflowList
        },
        props: {
            common: [String, Number],
            menuType: {
                type: String,
                default: 'plugin'
            },
            templateLabels: {
                type: Array,
                default: () => ([])
            },
            builtInPlugins: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            const panels = this.getPanels(this.menuType)
            return {
                panels,
                crtTab: panels[0].id,
                isFixed: false
            }
        },
        computed: {
            menuTitle () {
                const panelName = this.panels.find(item => item.id === this.crtTab).name
                return `${panelName}${i18n.t('节点')}`
            }
        },
        watch: {
            menuType (val) {
                this.panels = this.getPanels(val)
                this.crtTab = this.panels[0].id
            }
        },
        methods: {
            getPanels (type) {
                if (type === 'subflow' && this.common) {
                    return PANELS.subflow.filter(item => item.id === 'common')
                }
                return PANELS[type]
            },
            handleClickOutSide (e) {
                // 固定模式或者点击面板里的select框选项
                if (this.isFixed || dom.parentClsContains('node-menu-panel-popover', e.target)) {
                    return
                }
                let nodeType = ''
                let target = e.target
                while (target) {
                    if (['tasknode', 'subflow'].includes(target.dataset.type)) {
                        nodeType = target.dataset.type
                        break
                    }
                    target = target.parentNode.tagName === 'BODY' ? null : target.parentNode
                }
                if (nodeType) {
                    this.$emit('change', nodeType)
                } else {
                    this.$emit('close')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .node-menu {
        position: absolute;
        top: 0;
        margin-left: 60px;
        width: 293px;
        height: 100%;
        background: #ffffff;
        border-right: 1px solid #dddddd;
        z-index: 2;
    }
    .title-wrap {
        height: 41px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 11px 0 14px;
        color: #303132;
        font-size: 14px;
        border-bottom: 1px solid #ccd0dd;
        .panel-fixed-pin {
            color: #999999;
            cursor: pointer;
            &:hover {
                color: #707379;
            }
            &.actived {
                color: #52699d;
            }
        }
    }
    .bk-tab {
        height: calc(100% - 41px);
        ::v-deep .bk-tab-section {
            padding: 0;
            height: 100%;
            .bk-tab-content {
                height: calc(100% - 50px); // 减掉header高度
            }
        }
    }
</style>
