<template>
    <div class="page-view">
        <MobileCanvas :is-preview="false" :canvas-data="canvasData"></MobileCanvas>
    </div>
</template>

<script>
    import MobileCanvas from '../jsflow/index.vue'
    import { mapState, mapActions } from 'vuex'

    export default {
        name: 'template_preview',
        components: {
            MobileCanvas
        },
        data () {
            return {
                pipelineTree: {}
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
                const params = {
                    template_id: this.templateId,
                    exclude_task_nodes_id: JSON.stringify(this.excludeTaskNodes),
                    template_source: 'business'
                }
                this.pipelineTree = await this.getPreviewTaskTree(params)
            }
        }
    }
</script>
