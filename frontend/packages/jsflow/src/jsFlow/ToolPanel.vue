<template>
    <div class="tool-panel">
        <div
            v-for="(tool, index) in tools"
            :key="index"
            :class="['tool-item', tool.cls, { 'actived': tool.type === 'frameSelect' && isFrameSelecting }]"
            @click="onToolClick(tool)">
            {{tool.name}}
        </div>
    </div>
</template>
<script>
    export default {
        name: 'ToolPanel',
        props: ['tools', 'isFrameSelecting'],
        data () {
            return {}
        },
        methods: {
            onToolClick (tool) {
                this.$emit('onToolClick', tool)
            }
        }
    }
</script>
<style lang="scss">
    .tool-item {
        display: inline-block;
        margin-right: 10px;
        user-select: none;
        cursor: pointer;
        &:last-child {
            margin-right: 0;
        }
        &.actived {
            color: #3a84ff;
        }
    }
</style>
