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
    <div class="template-info">
        <div class="panel-title">
            <h3>{{ i18n.title }}</h3>
        </div>
        <div class="content-wrapper">
            <div class="info-sections">
                <section>
                    <h4 class="common-section-title">{{ i18n.contextInfo }}</h4>
                    <div class="context-data"></div>
                </section>
                <section>
                    <h4 class="common-section-title">{{ i18n.modelInfo }}</h4>
                    <div class="context-data"></div>
                </section>
            </div>
            <no-data></no-data>
        </div>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TemplateInfo',
        components: {
            NoData
        },
        props: {
            taskId: {
                type: String,
                required: true
            }
        },
        data () {
            return {
                taskflowDetailLoading: true,
                i18n: {
                    title: gettext('流程信息'),
                    contextInfo: gettext('上下文数据'),
                    modelInfo: gettext('任务模型数据')
                }
            }
        },
        created () {
            this.getData()
        },
        methods: {
            ...mapActions('admin/', [
                'taskflowDetail'
            ]),
            async getData () {
                try {
                    this.taskflowDetailLoading = true
                    const resp = await this.taskflowDetail({ task_id: this.taskId })
                    if (resp.result) {
                        console.log(resp.result)
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error)
                } finally {
                    this.taskflowDetailLoading = false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .template-info {
        position: relative;
        height: 100%;
        overflow: hidden;
        .panel-title {
            margin: 20px;
            padding-bottom: 5px;
            border-bottom: 1px solid #cacedb;
            h3 {
                margin: 0;
                font-size: 14px;
                font-weight: bold;
            }
        }
        .content-wrapper {
            padding: 20px;
        }
        .common-section-title {
            color: #313238;
            font-size: 14px;
            margin-bottom: 20px;
        }
    }
</style>
