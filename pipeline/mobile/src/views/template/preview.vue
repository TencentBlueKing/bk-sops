<template>
    <div class="page-view">
        <MobileCanvas :is-preview="true" :canvas-data="canvasData"></MobileCanvas>
    </div>
</template>

<script>
    import MobileCanvas from '../jsflow/index.vue'
    import { mapState } from 'vuex'

    export default {
        name: 'template_preview',
        components: {
            MobileCanvas
        },
        data () {
            return {
                canvasData: {
                    lines: [],
                    nodes: []
                }
            }
        },
        computed: {
            ...mapState({
                template: state => state.template
            })
        },
        created () {
            const pipelineTree = JSON.parse(this.template.pipeline_tree);
            ({ line: this.canvasData.lines, location: this.canvasData.nodes } = pipelineTree)
            console.log(this.canvasData)
        }
    }
</script>
