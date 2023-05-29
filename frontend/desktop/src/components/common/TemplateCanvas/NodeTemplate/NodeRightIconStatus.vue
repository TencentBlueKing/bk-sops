<template>
    <div class="node-execute-icon">
        <!-- 节点执行顶部右侧 icon， 执行中、重试次数、是否为跳过-->
        <div v-if="node.status === 'RUNNING'" class="task-status-icon">
            <i class="common-icon-loading"></i>
        </div>
        <div v-else-if="node.status === 'FINISHED' && !(node.retry > 0 || node.skip)" class="task-status-icon">
            <!-- 后续用icon替换 -->
            <i v-if="!node.skip" style="position: absolute; top: -3px; left: -1px; transform: scale(0.6);">M</i>
            <i v-if="!node.skip" style="position: absolute;top: 6px; left: 5px;" class="bk-icon icon-arrows-right-shape"></i>
            <span v-else-if="node.retry > 0" class="retry-times">{{ node.retry > 99 ? '100+' : node.retry }}</span>
        </div>
        <!-- 节点失败后自动忽略icon -->
        <div v-else-if="node.status === 'FINISHED' && node.error_ignored" class="task-status-icon node-subscript">
            <i style="position: absolute; top: -3px; left: 1px; transform: scale(0.6);">A</i>
            <i style="position: absolute;top: 6px; left: 5px;" class="bk-icon icon-arrows-right-shape"></i>
        </div>
        <!-- 节点循环次数 -->
        <div v-if="node.loop > 1" :class="['task-status-icon task-node-loop', { 'loop-plural': node.loop > 9 }]">
            <i :class="`common-icon-loading-${ node.loop > 9 ? 'oval' : 'round' }`"></i>
            <span>{{ node.loop > 99 ? '99+' : node.loop }}</span>
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
        }
    }
</script>

<style lang="scss" scoped>

</style>
