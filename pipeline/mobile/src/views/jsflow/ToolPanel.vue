<template>
    <div class="tool-panel">
        <div
            v-for="(tool, index) in tools"
            :key="index"
            :class="['tool-item', tool.cls,{ 'actived': tool.type === 'frameSelect' && isFrameSelecting }]"
            @click="onToolClick(tool)">
            {{tool.type}}
        </div>
    </div>
</template>
<script>
    export default {
        name: 'ToolPanel',
        // eslint-disable-next-line vue/require-prop-types
        props: ['tools', 'isFrameSelecting'],
        data () {
            return {}
        },
        methods: {
            onToolClick (tool) {
                typeof this[tool.type] === 'function' && this[tool.type]()
                this.$emit('onToolClick', tool)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .tool-item {
        display: inline-block;
        margin-right: 10px;
        cursor: pointer;
        user-select: none;

        &:last-child {
            margin-right: 0;
        }

        &.actived {
            color: #3a84ff;
        }
    }
</style>
