/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <MobileCanvas v-if="!loading" :editable="false" :canvas-data="canvasData"></MobileCanvas>
    </div>
</template>

<script>
    import { errorHandler } from '@/utils/errorHandler.js'
    import MobileCanvas from '@/components/MobileCanvas/index.vue'
    import { mapState, mapActions } from 'vuex'

    export default {
        name: 'template_preview',
        components: {
            MobileCanvas
        },
        data () {
            return {
                pipelineTree: {},
                loading: true,
                i18n: {
                    loading: window.gettext('加载中...')
                }
            }
        },
        computed: {
            ...mapState({
                templateId: state => state.templateId,
                excludeTaskNodes: state => state.excludeTaskNodes
            }),
            canvasData () {
                const { line = [], location = [], gateways = {} } = this.pipelineTree
                return { lines: line, nodes: location, gateways: gateways }
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('template', [
                'getPreviewTaskTree'
            ]),

            async loadData () {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const params = {
                    template_id: this.$route.query.templateId || this.template_id,
                    exclude_task_nodes_id: JSON.stringify(this.excludeTaskNodes),
                    template_source: 'business'
                }
                try {
                    this.pipelineTree = await this.getPreviewTaskTree(params)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                    this.$toast.clear()
                }
            }
        }
    }
</script>
