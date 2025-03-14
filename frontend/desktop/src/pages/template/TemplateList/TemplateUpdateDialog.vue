<template>
    <bk-dialog
        class="batch-update-dialog"
        :value="isShow"
        :close-icon="false"
        :fullscreen="true"
        data-test-id="templateEdit_form_batchUpdateDialog"
        :show-footer="false">
        <BatchUpdateDialog
            v-if="isShow && !!subflowShouldUpdated.length"
            :project-id="projectId"
            :list="subflowShouldUpdated"
            source="list"
            :template-id="row.id"
            @confirm="handleConfirm"
            @close="$emit('close')">
        </BatchUpdateDialog>
    </bk-dialog>
</template>
<script>
    import { mapActions } from 'vuex'
    import BatchUpdateDialog from '../TemplateEdit/BatchUpdateDialog.vue'
    export default {
        components: {
            BatchUpdateDialog
        },
        props: {
            isShow: Boolean,
            projectId: [Number, String],
            row: {
                type: Object,
                default: () => ({})
            }
        },
        computed: {
            subflowShouldUpdated () {
                const { subprocess_info: subprocessInfo, pipeline_tree: pipelineTree } = this.row
                if (subprocessInfo?.details) {
                    const { activities } = JSON.parse(pipelineTree)
                    return subprocessInfo.details.reduce((acc, cur) => {
                        const nodeId = cur.subprocess_node_id
                        if (!activities[nodeId]) {
                            return acc
                        }
                        const { scheme_id_list = [] } = activities[nodeId]
                        acc.push({
                            ...cur,
                            scheme_id_list
                        })
                        return acc
                    }, [])
                }
                return []
            }
        },
        methods: {
            ...mapActions('template/', [
                'saveTemplateData'
            ]),
            async handleConfirm () {
                const resp = await this.saveTemplateData({
                    templateId: this.row.id,
                    projectId: this.projectId,
                    common: false
                })
                if (!resp.result) {
                    if ('errorId' in resp) {
                        this.$bkMessage({
                            message: resp.message,
                            theme: 'error',
                            delay: 10000
                        })
                    }
                    return
                }
                this.$emit('confirm')
            }
        }
    }
</script>
