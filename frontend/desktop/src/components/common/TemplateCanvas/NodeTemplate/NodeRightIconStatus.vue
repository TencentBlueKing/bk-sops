<template>
    <div class="node-execute-icon">
        <!-- 节点执行顶部右侧 icon， 执行中、重试次数、是否为跳过-->
        <div v-if="node.status === 'RUNNING'" class="task-status-icon">
            <i class="common-icon-loading"></i>
        </div>
        <!-- 节点等待任务继续 -->
        <div v-else-if="node.status === 'PENDING_TASK_CONTINUE'" class="node-pending task-status-icon">
            <i v-bk-tooltips="$t('等待任务继续')" class="common-icon-pause"></i>
        </div>
        <!--节点等待处理/等待审批/等待确认-->
        <div v-else-if="isPendingState" class="task-status-icon node-pending">
            <i v-if="node.status === 'PENDING_PROCESSING'" v-bk-tooltips="$t('等待处理')" class="bk-icon icon-time"></i>
            <i v-if="node.status === 'PENDING_APPROVAL'" v-bk-tooltips="$t('等待审批')" class="common-icon-pending-approval"></i>
            <i v-if="node.status === 'PENDING_CONFIRMATION'" v-bk-tooltips="$t('等待确认')" class="common-icon-pending-confirm"></i>
        </div>
        <!-- 节点失败后自动忽略icon -->
        <div v-else-if="node.status === 'FINISHED' && node.skip" class="node-manual-skip">
            <i class="common-icon-manual-skip"></i>
        </div>
        <!-- 节点失败后自动忽略icon -->
        <div v-else-if="node.status === 'FINISHED' && node.error_ignored" class="node-auto-skip">
            <i class="common-icon-auto-skip"></i>
        </div>
        <!-- 节点顶部右侧生命周期 icon -->
        <div class="node-phase-icon" v-if="[1, 2].includes(node.phase)">
            <i
                :class="['bk-icon', 'icon-exclamation-circle', {
                    'phase-warn': node.phase === 1,
                    'phase-error': node.phase === 2
                }]"
                v-bk-tooltips="{
                    content: phaseStr[node.phase],
                    width: 210
                }">
            </i>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'NodeRightIconStatus',
        props: {
            node: Object
        },
        computed: {
            isPendingState () {
                return ['PENDING_PROCESSING', 'PENDING_APPROVAL', 'PENDING_CONFIRMATION'].includes(this.node.status)
            }
        }
    }
</script>

<style lang="scss" scoped>

</style>
