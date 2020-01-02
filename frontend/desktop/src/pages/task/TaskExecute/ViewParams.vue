/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="view-params-container clearfix">
        <div class="select-node">
            <NodeTree
                :data="nodeData"
                :selected-flow-path="selectedFlowPath"
                @onSelectNode="onSelectNode">
            </NodeTree>
        </div>
        <div class="view-params" v-bkloading="{ isLoading: loading, opacity: 1 }">
            <div class="params-panel" v-if="!isEmptyParams">
                <h4 class="panel-title">{{ i18n.atom_params }}</h4>
                <div class="params-content">
                    <RenderForm
                        v-if="!loading"
                        :key="currentNode"
                        :scheme="renderConfig"
                        :form-option="renderOption"
                        v-model="renderData">
                    </RenderForm>
                </div>
            </div>
            <NoData v-else>{{noDataMessage}}</NoData>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import NodeTree from './NodeTree.vue'
    export default {
        name: 'ViewParams',
        components: {
            NodeTree,
            RenderForm,
            NoData
        },
        props: [
            'nodeData',
            'selectedFlowPath',
            'treeNodeConfig'
        ],
        data () {
            return {
                i18n: {
                    atom_params: gettext('查看标准插件参数')
                },
                loading: true,
                bkMessageInstance: null,
                renderOption: {
                    showGroup: false,
                    showLabel: true,
                    showHook: false,
                    formEdit: false,
                    formMode: false
                },
                renderConfig: [],
                renderData: {}
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config
            }),
            isEmptyParams () {
                return !this.renderConfig || this.renderConfig.length === 0
            },
            isSubflowNode () {
                return !this.treeNodeConfig.component_code
            },
            noDataMessage () {
                return this.isSubflowNode ? gettext('请点击标准插件节点查看参数') : gettext('无数据')
            },
            currentNode () {
                return this.selectedFlowPath.slice(-1)[0].id
            }
        },
        watch: {
            treeNodeConfig (val) {
                this.upDataParamsData(val)
            }
        },
        mounted () {
            this.upDataParamsData(this.treeNodeConfig)
        },
        methods: {
            ...mapActions('task/', [
                'getNodeActInfo',
                'instanceRetry'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig'
            ]),
            ...mapMutations('atomForm/', [
                'setAtomConfig'
            ]),
            async loadNodeInfo () {
                this.loading = true
                try {
                    this.nodeInfo = await this.getNodeActInfo(this.treeNodeConfig)
                    this.renderConfig = await this.getNodeConfig(this.treeNodeConfig.component_code)
                    if (this.nodeInfo.result) {
                        for (const key in this.nodeInfo.data.inputs) {
                            this.$set(this.renderData, key, this.nodeInfo.data.inputs[key])
                        }
                    } else {
                        errorHandler(this.nodeInfo, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            async getNodeConfig (type) {
                if (this.atomFormConfig[type]) {
                    return this.atomFormConfig[type]
                } else {
                    try {
                        await this.loadAtomConfig({ atomType: type })
                        this.setAtomConfig({ atomType: type, configData: $.atoms[type] })
                        return this.atomFormConfig[type]
                    } catch (e) {
                        errorHandler(e, this)
                    }
                }
            },
            upDataParamsData (config) {
                if (config.component_code) {
                    this.loadNodeInfo()
                } else {
                    this.$nextTick(() => {
                        this.loading = false
                        this.renderConfig = []
                        this.renderData = {}
                    })
                }
            },
            onSelectNode (nodeHeirarchy, isClick, nodeType) {
                this.$emit('onClickTreeNode', nodeHeirarchy, isClick, nodeType)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.view-params-container {
    height: 100%;
    overflow: hidden;
    .panel-title {
        margin: 0;
        font-size: 22px;
        font-weight: normal;
    }
    .select-node {
        float: left;
        padding: 10px 0;
        width: 220px;
        height: 100%;
        border-right: 1px solid $commonBorderColor;
        overflow: auto;
        @include scrollbar;
    }
    .view-params {
        float: left;
        width: 529px;
        height: 100%;
        overflow-y: auto;
        @include scrollbar;
    }
    .params-panel {
        padding: 20px;
        height: 100%;
        overflow-y: auto;
        @include scrollbar;
    }
    .params-content {
        padding-top: 20px;
    }
}
</style>
