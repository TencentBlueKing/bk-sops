/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="choose-plugin">
        <bk-sideslider
            :ext-cls="'common-template-setting-sideslider'"
            :width="711"
            :is-show="isShow"
            :before-close="onBeforeClose"
            :quick-close="true">
            <div slot="header">
                <span>{{ isSubflow ? i18n.chooseSubflow : i18n.choosePlugin }}</span>
            </div>
            <div v-if="isShow" class="condition-form" slot="content">
                <div class="plugin-search">
                    <bk-input
                        class="search-input"
                        v-model="searchStr"
                        right-icon="bk-icon icon-search"
                        :placeholder="i18n.placeholder"
                        @input="onSearchInput" />
                </div>
                <div class="plugin-list">
                    <template v-if="listInPanel.length > 0">
                        <!-- 全部插件类表 -->
                        <template v-if="searchStr === ''">
                            <bk-collapse ext-cls="plugin-collapse" v-for="group in listInPanel" :key="group.type">
                                <bk-collapse-item :name="group.group_name">
                                    <div class="group-header">
                                        <img v-if="group.group_icon" class="group-icon-img" :src="group.group_icon" />
                                        <i v-else :class="['group-icon-font', getIconCls(group.type)]"></i>
                                        <span class="header-title">{{group.group_name}}
                                            <span class="header-atom">
                                                ({{group.list.length}})
                                            </span>
                                        </span>
                                    </div>
                                    <ul slot="content" class="node-item-wrap">
                                        <li class="node-item"
                                            v-for="(node, index) in group.list"
                                            :key="index">
                                            <span class="node-name">{{ node.name }}</span>
                                            <span class="opt-btns">
                                                <span v-if="getSelectedStatus(node)" class="opt-item selected">{{ i18n.selected }}</span>
                                                <span v-else class="opt-item" @click.stop="onChoosePlugin(node)">{{ i18n.choose }}</span>
                                                <span v-if="isSubflow" class="opt-item" @click.stop="onViewSubflow(node)">{{ i18n.view }}</span>
                                            </span>
                                        </li>
                                        <div class="node-empty" v-if="group.list.length === 0">
                                            <no-data></no-data>
                                        </div>
                                    </ul>
                                </bk-collapse-item>
                            </bk-collapse>
                        </template>
                        <!-- 搜索结果插件列表 -->
                        <template v-else>
                            <ul slot="content" class="node-item-wrap">
                                <li class="node-item"
                                    v-for="(node, index) in searchResult"
                                    :key="index">
                                    <span class="node-name">{{ node.name }}</span>
                                    <span class="opt-btns">
                                        <span v-if="getSelectedStatus(node)" class="opt-item selected">{{ i18n.selected }}</span>
                                        <span v-else class="opt-item" @click.stop="onChoosePlugin(node)">{{ i18n.choose }}</span>
                                        <span v-if="isSubflow" class="opt-item" @click.stop="onViewSubflow(node)">{{ i18n.view }}</span>
                                    </span>
                                </li>
                                <div class="node-empty" v-if="searchResult.length === 0">
                                    <no-data></no-data>
                                </div>
                            </ul>
                        </template>
                    </template>
                    <no-data v-else></no-data>
                </div>
            </div>
        </bk-sideslider>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'
    import { mapState, mapMutations } from 'vuex'
    import { SYSTEM_GROUP_ICON } from '@/constants/index.js'
    export default {
        name: 'ChoosePlugin',
        components: {
            NoData
        },
        props: {
            isShow: {
                type: Boolean,
                default: false
            },
            nodeId: {
                type: String,
                default: ''
            },
            atomTypeList: {
                type: Object,
                default: []
            }
        },
        data () {
            return {
                i18n: {
                    choose: gettext('选择'),
                    selected: gettext('已选'),
                    view: gettext('查看'),
                    choosePlugin: gettext('请选择插件'),
                    chooseSubflow: gettext('请选择子流程'),
                    placeholder: gettext('请输入名称')
                },
                searchStr: '',
                searchResult: []
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'pluginConfigs': state => state.atomForm.config
            }),
            nodeConfg () {
                if (this.nodeId) {
                    return tools.deepClone(this.activities[this.nodeId])
                }
                return {}
            },
            isSubflow () {
                return this.nodeConfg.type === 'SubProcess'
            },
            nodes () {
                return this.isSubflow ? this.atomTypeList.subflow : this.atomTypeList.tasknode
            },
            listInPanel () {
                return this.searchStr === '' ? this.nodes : this.searchResult
            }
        },
        methods: {
            ...mapMutations('template/', [
                'setActivities'
            ]),
            /**
             * 搜索值改变
             */
            onSearchInput () {
                if (this.searchStr !== '') {
                    const result = []
                    this.nodes.forEach(group => {
                        if (group.list.length > 0) {
                            group.list.forEach(node => {
                                if (
                                    typeof node.name === 'string'
                                    && node.name.indexOf(this.searchStr) !== -1
                                ) {
                                    result.push(node)
                                }
                            })
                        }
                    })
                    this.searchResult = result
                }
            },
            getIconCls (type) {
                const systemType = SYSTEM_GROUP_ICON.find(item => new RegExp(item).test(type))
                if (this.activeNodeListType === 'subflow') {
                    return 'common-icon-subflow-mark'
                }
                if (systemType) {
                    return `common-icon-sys-${systemType.toLowerCase()}`
                }
                return 'common-icon-sys-default'
            },
            /**
             * 选择插件
             * @param {Object} node 插件/子流程
             */
            onChoosePlugin (node) {
                const nodeConfg = tools.deepClone(this.nodeConfg)
                if (this.isSubflow) {
                    nodeConfg.template_id = node.id
                    nodeConfg.version = node.version
                    nodeConfg.name = node.name.replace(/\s/g, '')
                    nodeConfg.optional = false
                    nodeConfg.constants = {}
                } else {
                    nodeConfg.component.code = node.code
                    nodeConfg.component.data = {}
                    // 默认取最后一个版本
                    nodeConfg.component.version = node.list[node.list.length - 1].version
                    nodeConfg.name = node.name.replace(/\s/g, '')
                    nodeConfg.optional = false
                    nodeConfg.skippable = true
                    nodeConfg.retryable = true
                    nodeConfg.error_ignorable = false
                }
                this.setActivities({ type: 'edit', location: nodeConfg })
                this.$emit('onPluginChange', nodeConfg)
                // 待开发，遍历全局变量，看是否有被该节点引用的，有就souce_info中去除，
                // souce_info 中只有一条则删除该变量
                // 子流程更新
            },
            /**
             * 插件选中状态
             * @param {Object} node 插件/子流程
             */
            getSelectedStatus (node) {
                if (this.isSubflow) {
                    return node.id === this.nodeConfg.template_id
                }
                return node.code === this.nodeConfg.component.code
            },
            // 查看子流程
            onViewSubflow (node) {
                const { href } = this.$router.resolve({
                    name: 'templatePanel',
                    params: {
                        type: 'edit',
                        project_id: node.project.id
                    },
                    query: {
                        template_id: node.id
                    }
                })
                window.open(href, '_blank')
            },
            // 关闭面板
            onBeforeClose () {
                this.$emit('hide')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.choose-plugin {
    /deep/ {
        .bk-sideslider-wrapper {
            right: 56px;
        }
    }
    .plugin-search {
        margin: 16px;
        float: right;
        width: 280px;
    }
    .plugin-list {
        clear: both;
        height: calc(100vh - 232px);
        overflow: scroll;
        @include scrollbar;
        .plugin-collapse {
            /deep/ {
                .bk-collapse-item-header {
                    width: 100%;
                    background: #fafbfd;
                    border-top: 1px solid #e2e4ed;
                }
                .bk-collapse-item-content {
                    padding: 0;
                }
            }
        }
    }
    .group-header {
        height: 42px;
        overflow: hidden;
        .group-icon-font {
            float: left;
            margin-top: 13px;
            font-size: 16px;
            color: #52699d;
            &.common-icon-subflow-mark {
                font-size: 18px;
            }
        }
        .group-icon-img {
            float: left;
            margin-top: 13px;
            width: 16px;
            height: 16px;
        }
        .header-title {
            display: inline-block;
            margin-left: 10px;
            width: 210px;
            font-size: 14px;
            overflow: hidden;
            .header-atom {
                color: #a9b2bd;
                font-size: 12px;
            }
        }
    }
    .node-item-wrap {
        .node-item {
            clear: both;
            height: 42px;
            line-height: 42px;
            border-top: 1px solid #e2e4ed;
        }
        .node-name {
            margin-left: 38px;
            color: #63656e;
            font-size: 12px;
        }
        .opt-btns {
            float: right;
            margin-right: 30px;
            .opt-item {
                margin-left: 10px;
                color: #3a84ff;
                font-size: 12px;
                cursor: pointer;
                &.selected {
                    color: #c4c6cc;
                }
            }
        }
    }
}
</style>
