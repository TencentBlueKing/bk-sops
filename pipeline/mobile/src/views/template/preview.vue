
<template>
    <div class="page-view">
        <MobileCanvas v-if="!loading" :editable="false" :canvas-data="canvasData"></MobileCanvas>
    </div>
</template>

<script>
    import MobileCanvas from '@/components/MobileCanvas/index.vue'
    import { mapState, mapActions } from 'vuex'

    export default {
        name: 'template_preview',
        components: {
            MobileCanvas
            // JsFlow
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
                const { line = [], location = [] } = this.pipelineTree
                return { lines: line, nodes: location }
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
                this.$toast.loading({ mask: true, message: '加载中...' })
                const params = {
                    template_id: this.$route.query.templateId || this.template_id,
                    exclude_task_nodes_id: JSON.stringify(this.excludeTaskNodes),
                    template_source: 'business'
                }
                console.log('---')
                console.log(this.loading)
                this.pipelineTree = await this.getPreviewTaskTree(params)
                this.loading = false
                this.$toast.clear()
            }
        }
    }
</script>
