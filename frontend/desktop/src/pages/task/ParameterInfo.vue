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
    <div v-bkloading="{ isLoading: ParameterInfoLoading, opacity: 1 }">
        <TaskParamEdit
            v-if="isReferencedVariables"
            class="task-param-wrapper"
            ref="TaskParamEdit"
            :constants="referencedVariable"
            @onChangeConfigLoading="onReferencedConfigLoading">
        </TaskParamEdit>
        <div
            class="variable-wrap"
            v-if="isUnreferencedVariableBar">
            <div class="title-background" @click="onToggleUnReferenceShow">
                <div class="UnreferencedVariable"
                    :class=" { UnReferenceShow: isUnreferencedVariables } ">
                </div>
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
                v-show="isUnreferencedVariables"
                ref="TaskParamEdit"
                :constants="noReferencedVariable"
                :editable="false"
                @onChangeConfigLoading="onUnreferencedConfigLoading">
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
        name: 'taskParamVariate',
        components: {
            TaskParamEdit,
            NoData
        },
        props: ['referencedVariable', 'noReferencedVariable'],
        data () {
            return {
                i18n: {
                    title: gettext('查看未引用变量'),
                    executorTips: gettext('在创建流程时可选择“变量”是否被引用，未被引用的“变量”则在创建任务时（当前步骤）不可编辑。')
                },
                ParameterInfoLoading: true,
                isReferencedVariables: false,
                isUnreferencedVariables: false,
                isUnreferencedVariableBar: false,
                isNoData: false,
                ReferencedVariablesLoading: false,
                UnreferencedVariablesLoading: false
            }
        },
        watch: {
            referencedVariable () {
                if (Object.keys(this.referencedVariable).length === 0) {
                    this.isReferencedVariables = false
                    if (this.isUnreferencedVariableBar === false) {
                        this.ParameterInfoLoading = false
                        this.isNoData = true
                    }
                } else {
                    this.isReferencedVariables = true
                    this.isNoData = false
                }
            },
            noReferencedVariable () {
                if (Object.keys(this.noReferencedVariable).length === 0) {
                    this.isUnreferencedVariableBar = false
                    if (this.isReferencedVariables === false) {
                        this.ParameterInfoLoading = false
                        this.isNoData = true
                    }
                } else {
                    this.isUnreferencedVariableBar = true
                    this.isNoData = false
                }
            },
            ParameterInfoLoading () {
                this.$nextTick(() => {
                    this.$emit('onParameterInfoLoading', this.ParameterInfoLoading)
                })
            }
        },
        methods: {
            onReferencedConfigLoading () {
                this.ReferencedVariablesLoading = true
                if (this.isUnreferencedVariableBar === false) {
                    this.ParameterInfoLoading = false
                } else if (this.UnreferencedVariablesLoading === true) {
                    this.ParameterInfoLoading = false
                }
            },
            onUnreferencedConfigLoading () {
                this.UnreferencedVariablesLoading = true
                if (this.isReferencedVariables === false) {
                    this.ParameterInfoLoading = false
                } else if (this.ReferencedVariablesLoading === true) {
                    this.ParameterInfoLoading = false
                }
            },
            onToggleUnReferenceShow () {
                this.isUnreferencedVariables = !this.isUnreferencedVariables
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.task-param-wrapper {
    margin: 0 20px 20px 20px;
}
.variable-wrap {
    background: #f0f1f5;
    .unreferenced {
       padding-bottom: 20px;
    }
    .title {
        font-weight: 600;
    }
    .title-background {
        padding-left: 20px;
        &:hover {
            background: #e4e6ed;
        }
        cursor: pointer;
        .common-icon-tooltips:hover {
            .tooltips-direction-icon, .unreferenced-tooltips {
                display: block;
            }
        }
        .UnreferencedVariable {
            display: inline-block;
            position: relative;
            width: 0;
            height: 0;
            border-left: 5px solid gray;
            border-top: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 5px solid transparent;
        }
        .desc-tooltip {
            float: right;
            margin: 20px;
        }
        .icon-info-circle {
            position: relative;
            right: 12px;
        }
        .tooltips-direction-icon {
                display: none;
                white: 0px;
                height: 0px;
                border-left: 8px solid transparent;
                border-top: 8px solid transparent;
                border-right: 8px solid transparent;
                border-bottom: 8px solid black;
        }
        .UnReferenceShow {
            top: 2px;
            transform: rotate(90deg);
        }
        .unreferenced-tooltips {
            display :none;
            position: absolute;
            top: 50px;
            width: 265px;
            height: 55px;
            right: 5px;
            font-size: 12px;
            line-height: 15px;
            color: white;
            background: black;
            padding: 4px 5px 0px 5px;
            border-radius: 4px;
        }
        .title {
            line-height: 60px;
            font-size: 14px
        }
    }
}
</style>
