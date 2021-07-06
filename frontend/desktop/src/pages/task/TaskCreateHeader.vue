/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <page-header class="task-create-header">
        <div class="header-title">
            <i v-if="isShowBackBtn" class="bk-icon icon-arrows-left back-icon" @click="onBackClick"></i>
            <div class="title">{{ title }}</div>
            <div v-if="instanceName" class="instance-name">{{ instanceName }}</div>
        </div>
        <div class="step-area" slot="expand">
            <bk-steps :steps="steps" :cur-step="currentStep" size="small" line-type="solid"></bk-steps>
        </div>
    </page-header>
</template>
<script>
    import { mapState } from 'vuex'
    import PageHeader from '@/components/layout/PageHeader.vue'

    export default {
        name: 'TaskCreateHeader',
        components: {
            PageHeader
        },
        props: {
            steps: {
                type: Array,
                default: () => ([])
            },
            currentStep: {
                type: Number,
                default: 0
            },
            common: {
                type: [String, Number],
                default: ''
            },
            title: {
                type: String,
                default: ''
            },
            instanceName: {
                type: String,
                default: ''
            },
            isFunctional: {
                type: Boolean,
                default: false
            },
            project_id: [String, Number],
            template_id: [String, Number]
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode
            }),
            isShowBackBtn () {
                return !(this.view_mode === 'appmaker' && this.$route.path.indexOf('newtask') !== -1)
            }
        },
        methods: {
            /**
             * 返回任务列表
             * 目的：返回到【节点选择】上一个页面
             */
            onBackClick () {
                const backObj = {
                    'business': {
                        name: 'process',
                        params: { project_id: this.project_id }
                    },
                    'periodicTask': {
                        name: 'periodicTemplate',
                        params: { project_id: this.project_id }
                    },
                    'taskflow': {
                        name: 'taskList',
                        params: { project_id: this.project_id }
                    },
                    'common': { name: 'commonProcessList' },
                    'templateEdit': {
                        name: 'templatePanel',
                        params: { type: 'edit', project_id: this.project_id },
                        query: { template_id: this.template_id }
                    },
                    'commonTplEdit': {
                        name: 'commonTemplatePanel',
                        params: { type: 'edit' },
                        query: { template_id: this.template_id }
                    },
                    'function': { name: 'functionHome' },
                    'audit': { name: 'auditHome' },
                    'appmaker': {
                        name: 'appmakerTaskHome',
                        params: { type: 'edit', app_id: this.$route.params.app_id, project_id: this.project_id },
                        query: { template_id: this.$route.query.template_id }
                    }
                }
                const pathMap = ['function', 'audit']
                const type = this.$route.path.split('/')[1]
                const currentUser = this.view_mode === 'app' ? (pathMap.includes(type) ? type : 'maintainer') : 'appmaker'
                const entrance = this.$route.query.entrance || ''
                let url = '/'
                switch (currentUser) {
                    case 'maintainer':
                        // 任务创建(节点选择+参数填写)
                        if (this.currentStep) {
                            /**
                             * entrance
                             * 1、periodicTask - 周期任务新建
                             * 2、taskflow - 任务记录新建
                             * 3、templateEdit - 模版编辑
                             */
                            if (entrance === 'periodicTask' || entrance === 'taskflow' || entrance === 'templateEdit') {
                                url = (this.common && entrance === 'templateEdit') ? backObj['commonTplEdit'] : backObj[entrance]
                                break
                            }
                            if (this.common) {
                                url = backObj['common']
                                break
                            }
                            if (this.isFunctional) {
                                url = backObj['taskflow']
                                break
                            }
                            url = backObj['business']
                        } else {
                            // 任务执行页面
                            url = backObj['taskflow']
                        }
                        break
                    case 'function':
                    case 'audit':
                    case 'appmaker':
                        url = backObj[currentUser]
                        break
                    default:
                        url = { name: 'home' }
                }
                this.$router.push(url)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.task-create-header {
    display: flex;
    justify-content: space-between;
    padding: 0 20px 0 10px;
    .header-title {
        display: flex;
        align-items: center;
        .back-icon {
            font-size: 28px;
            color: #3a84ff;
            cursor: pointer;
        }
        .title {
            font-size: 14px;
            color: #313238;
        }
        .instance-name {
            margin-left: 10px;
            font-size: 14px;
            color: #313238;
        }
    }
    .step-area {
        display: flex;
        align-items: center;
        width: 600px;
        height: 100%;
    }
}
</style>
