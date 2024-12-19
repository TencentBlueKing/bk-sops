<template>
    <nodePreview
        :preview-data-loading="templateLoading"
        :canvas-data="templateData"
        :preview-bread="[]">
    </nodePreview>
</template>
<script>
    import { mapActions } from 'vuex'
    import nodePreview from '../../task/NodePreview.vue'
    import { formatCanvasData } from '@/utils/checkDataType'
    export default {
        components: {
            nodePreview
        },
        props: {
            project_id: [Number, String],
            template_id: [Number, String]
        },
        data () {
            return {
                templateLoading: true,
                templateData: {
                    location: [],
                    line: [],
                    gateways: {},
                    constants: []
                }
            }
        },
        created () {
            this.getTemplateData()
        },
        methods: {
            ...mapActions('templateMarket/', [
                'loadTemplatePreviewData'
            ]),
            async getTemplateData () {
                try {
                    this.templateLoading = true
                    const resp = await this.loadTemplatePreviewData({
                        template_id: this.template_id,
                        project_id: this.project_id
                    })
                    const pipelineTree = JSON.parse(resp.data.pipeline_tree)
                    this.templateData = formatCanvasData('perview', pipelineTree)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateLoading = false
                }
            }
        }
    }
</script>
