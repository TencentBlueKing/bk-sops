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
    <div class="node-preview-wrapper">
        <div class="operation-header clearfix">
            <div class="bread-crumbs-wrapper">
                <div
                    :class="['path-item', { 'name-ellipsis': previewBread.length > 1 }]"
                    v-for="(path, index) in previewBread"
                    :key="index"
                    :title="showBreakList.includes(index) ? path.name : ''">
                    <span
                        v-if="!!index && showBreakList.includes(index) || index === 1">
                        &gt;
                    </span>
                    <span
                        v-if="showBreakList.includes(index)"
                        class="node-name"
                        :title="path.name"
                        @click="onSelectSubflow(path.data, index)">
                        {{path.name}}
                    </span>
                    <span class="node-ellipsis" v-else-if="index === 1">
                        {{ellipsis}}
                    </span>
                </div>
            </div>
        </div>
        <div class="canvas-wrapper" v-bkloading="{ isLoading: previewDataLoading, opacity: 1 }">
            <PipelineCanvas
                v-if="!previewDataLoading"
                ref="pipelineCanvas"
                :is-menu-bar-show="false"
                :is-config-bar-show="false"
                :is-edit="false"
                :is-select-node="isSelectNode"
                :is-select-all-node="isSelectAllNode"
                :is-preview-mode="isPreviewMode"
                :canvas-data="canvasData"
                @onNodeClick="onNodeClick">
            </PipelineCanvas>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import PipelineCanvas from '@/components/common/PipelineCanvas/index.vue'
    export default {
        name: 'NodePreview',
        components: {
            PipelineCanvas
        },
        props: ['canvasData', 'previewBread', 'previewDataLoading', 'isSelectNode', 'isPreviewMode', 'isSelectAllNode'],
        data () {
            return {
                ellipsis: '...',
                showBreakList: [0, 1, 2],
                isOmit: true
            }
        },
        watch: {
            previewBread (val) {
                if (val.length > 3) {
                    this.showBreakList = [0, val.length - 1, val.length - 2]
                } else {
                    this.showBreakList = [0, 1, 2]
                }
            }
        },
        methods: {
            onNodeClick (id) {
                if (this.previewDataLoading) {
                    return
                }
                this.$emit('onNodeClick', id)
            },
            onSelectSubflow (data, index) {
                if (this.previewDataLoading) {
                    return
                }
                if (this.previewBread.length - 1 === index) {
                    return
                }
                this.$emit('onSelectSubflow', data, index)
            },
            onUpdateNodeInfo (id, item) {
                this.$refs.pipelineCanvas.onUpdateNodeInfo(item.id, item)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.node-preview-wrapper {
    height: 100%;
}
.canvas-wrapper {
    height: calc(100% - 50px);
    overflow: hidden;
    z-index: 1;
    /deep/ .node-canvas {
        width: 100%;
        height: 100%;
        background: #e1e4e8;
    }
}
.operation-header {
    padding: 0 0 0 10px;
    height: 50px;
    line-height: 50px;
    background: #f4f7fa;
    border-bottom: 1px solid $commonBorderColor;
    .bread-crumbs-wrapper {
        display: inline-block;
        font-size: 14px;
        .path-item {
            display: inline-block;
            overflow: hidden;
            .node-name {
                margin: 0 4px;
                color: $blueDefault;
                cursor: pointer;
            }
            &:first-child {
                padding-left: 8px;
            }
            .node-ellipsis {
                margin-right: 4px;
            }
            &.name-ellipsis {
                max-width: 180px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
            &:last-child {
                .node-name {
                    cursor: pointer;
                    &:last-child {
                        color: #313238;
                        cursor: text;
                    }
                }
            }
        }
    }
    .operation-container {
        float: right;
        .operation-btn {
            float: left;
            width: 60px;
            height: 49px;
            line-height: 49px;
            font-size: 22px;
            text-align: center;
            color: $greyDisable;
            &.clickable {
                color: $greyDefault;
                cursor: pointer;
                &:hover {
                    color: $greenDefault;
                }
                &.actived {
                    color: $greenDefault;
                    background: $whiteDefault;
                }
            }
            &.common-icon-dark-paper {
                border-left: 1px solid $commonBorderColor;
            }
        }
    }
}
</style>
