
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
                this.pipelineTree = await this.getPreviewTaskTree(params)
                this.loading = false
                this.$toast.clear()
            }
        }
    }
</script>
