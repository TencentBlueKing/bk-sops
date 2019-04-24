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
    <div>
        <TaskParamEdit
            class="task-param-wrapper"
            v-if="pipelinedata"
            ref="TaskParamEdit"
            :constants="pipelinedata"
            @onChangeConfigLoading="onChangeConfigLoading">
        </TaskParamEdit>
        <div
            class="variable-wrap"
            v-if="true">
            <div class="title-background" @click="onUnreferenced">
                <div :class="[isunreferenced ? 'triangle-show' : 'triangle-hide']"></div>
                <span class="title">{{i18n.title}}</span>
                <a class="bk-text-main bk-icon icon-info-circle template-tooltip mr15"
                    v-bktooltips.bottom="{ content: longConfig.content, placements: ['bottom'] }">
                </a>
            </div>
            <TaskParamEdit
                class="unreferenced"
                v-show="isunreferenced"
                ref="TaskParamEdit"
                :constants="unreferenced"
                :editable="false"
                @onChangeConfigLoading="onChangeConfigLoading">
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
        props: ['pipelinedata', 'unreferenced'],
        data () {
            return {
                i18n: {
                    title: gettext('查看未引用变量')
                },
                longConfig: {
                    content: '在创建流程时可选择“变量”是否被引用，未被引用的“变量”则在创建任务时（当前步骤）不可编辑。',
                    width: 500
                },
                loading: false,
                isNoData: false,
                isunreferenced: false,
                configLoading: true,
                taskParamEditLoading: true,
                noneData: false,
                referencedShow: false
            }
        },
        watch: {
            configLoading (loading) {
                if (!loading) {
                    this.templateLoading = false
                }
                this.$emit('send', this.templateLoading)
            }
        },
        created () {
            const parent = this.$parent
            this.$on('send', parent.getData)
        },
        methods: {
            onChangeConfigLoading (loading) {
                this.configLoading = loading
                console.log(this.pipelinedata)
                console.log(this.unreferenced)
            },
            onUnreferenced () {
                this.isunreferenced = !this.isunreferenced
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.task-param-wrapper{
    margin-left: 20px;
    padding-bottom: 20px;
}
.unreferenced{
            background: #f0f1f5;
        }
.variable-wrap{
    .title-background{
        background: #f0f1f5;
        padding-left: 20px;
        background: #f0f1f5;
            &:hover{
                background: #e4e6ed;
            }
        cursor: pointer;
        .triangle-hide{
            display: inline-block;
            width: 0;
            height: 0;
            border-left: 5px solid gray;
            border-top: 5px solid transparent;;
            border-right: 5px solid transparent;
            border-bottom: 5px solid transparent;
        }
        .template-tooltip{
            float: right;
            margin: 20px;
        }
        .triangle-show{
            display: inline-block;
            width: 0;
            height: 0;
            position: relative;
            top: 2px;
            margin-top: 5px;
            border-left: 5px solid transparent;;
            border-top: 5px solid  gray;
            border-right: 5px solid transparent;
            border-bottom: 5px solid transparent;
        }
        .title{
            line-height: 60px;
            font-size: 14px
        }
    }
}
</style>
