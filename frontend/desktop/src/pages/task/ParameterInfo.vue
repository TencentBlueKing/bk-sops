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
    <div class="parameter-info-wrap" v-bkloading="{ isLoading: isParameterInfoLoading, opacity: 1 }">
        <TaskParamEdit
            v-if="isReferencedShow"
            class="task-param-wrapper"
            ref="TaskParamEdit"
            :constants="referencedVariable"
            @onChangeConfigLoading="onRefVarLoadingChange">
        </TaskParamEdit>
        <div
            class="variable-wrap"
            v-if="isUnreferencedShow">
            <div class="title-background" @click="onToggleUnreferenceShow">
                <div :class="['unreferenced-variable', { 'unreference-show': isUnrefVarShow }]"></div>
                <span class="title">{{i18n.title}}</span>
                <bk-tooltip placement="bottom-end" width="400" class="desc-tooltip">
                    <i class="bk-icon icon-info-circle"></i>
                    <div slot="content" style="white-space: normal;">
                        <div>{{i18n.executorTips}}</div>
                    </div>
                </bk-tooltip>
            </div>
            <TaskParamEdit
                class="unreferenced"
                v-show="isUnrefVarShow"
                ref="TaskParamEdit"
                :constants="unReferencedVariable"
                :editable="false"
                @onChangeConfigLoading="onUnrefVarLoadingChange">
            </TaskParamEdit>
        </div>
        <NoData v-if="isNoData"></NoData>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import TaskParamEdit from './TaskParamEdit.vue'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'ParameterInfo',
        components: {
            TaskParamEdit,
            NoData
        },
        props: ['referencedVariable', 'unReferencedVariable', 'taskMessageLoading'],
        data () {
            return {
                i18n: {
                    title: gettext('查看未引用变量'),
                    executorTips: gettext('在创建流程时可选择“变量”是否被引用，未被引用的“变量”则在创建任务时（当前步骤）不可编辑。')
                },
                isUnrefVarShow: false,
                isRefVarLoading: true,
                isUnrefVarLoading: true

            }
        },
        computed: {
            isReferencedShow () {
                return this.taskMessageLoading ? false : (Object.keys(this.referencedVariable).length > 0)
            },
            isUnreferencedShow () {
                return this.taskMessageLoading ? false : (Object.keys(this.unReferencedVariable).length > 0)
            },
            isParameterInfoLoading () {
                return this.isRefVarLoading || this.isUnrefVarLoading
            },
            isNoData () {
                return !this.taskMessageLoading && !this.isReferencedShow && !this.isUnreferencedShow
            }
        },
        watch: {
            isParameterInfoLoading (Val) {
                this.$emit('onParameterInfoLoading', Val)
            },
            taskMessageLoading (val) {
                if (!val) {
                    if (!this.isReferencedShow) {
                        this.isRefVarLoading = false
                    }
                    if (!this.isUnreferencedShow) {
                        this.isUnrefVarLoading = false
                    }
                }
            }
        },
        methods: {
            onToggleUnreferenceShow () {
                this.isUnrefVarShow = !this.isUnrefVarShow
            },
            onRefVarLoadingChange () {
                this.isRefVarLoading = false
            },
            onUnrefVarLoadingChange () {
                this.isUnrefVarLoading = false
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.task-param-wrapper {
    margin: 0 20px 20px 20px;
}
.parameter-info-wrap {
    min-height: 180px;
}
.variable-wrap {
    background: #f0f1f5;
    .unreferenced {
       padding-bottom: 20px;
    }
    .title-background {
        padding-left: 20px;
        cursor: pointer;
        &:hover {
            background: #e4e6ed;
        }
        .unreferenced-variable {
            display: inline-block;
            position: relative;
            width: 0;
            height: 0;
            border-left: 5px solid gray;
            border-top: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 5px solid transparent;
        }
        .unreference-show {
            top: 2px;
            transform: rotate(90deg);
        }
        .desc-tooltip {
            float: right;
            margin: 20px;
        }
        .icon-info-circle {
            position: relative;
            right: 12px;
        }
        .title {
            font-weight: 600;
            line-height: 60px;
            font-size: 14px
        }
    }
}
</style>
