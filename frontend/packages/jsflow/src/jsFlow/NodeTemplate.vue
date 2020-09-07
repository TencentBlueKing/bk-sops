<template>
    <div
        class="bk-flow-location"
        @mousedown="onMouseDown"
        @mouseup="onMouseUp">
        <div v-if="node.type === 'startpoint'" class="circle-node startpoint"></div>
        <div v-else-if="node.type === 'endpoint'" class="circle-node endpoint"></div>
        <div v-else-if="node.type === 'tasknode'" class="tasknode"></div>
        <div v-else-if="node.type === 'gateway'" class="gateway"></div>
        <div v-else class="node-default"></div>
      </div>
</template>
<script>
export default {
    name: 'NodeTemplate',
    props: {
        node: {
            type: Object,
            default () {
                return {}
            }
        }
    },
    data () {
        return {
            moveFlag: {
                x: 0,
                y: 0,
                moved: false
            }
        }
    },
    methods: {
        onMouseDown (event) {
            this.moveFlag = {
                x: event.pageX,
                y: event.pageY,
                moved: false
            }
            this.$el.addEventListener('mousemove', this.mouseMoveHandler)
        },
        onMouseUp (event) {
            const { pageX: x, pageY: y } = event
            this.moveFlag.x = x
            this.moveFlag.y = y

            if (this.moveFlag.moved) {
                console.log('drag event')
                this.moveFlag.moved = false
            } else {
                console.log('click event')
            }
            this.$el.removeEventListener('mousemove', this.mouseMoveHandler)
        },
        mouseMoveHandler (event) {
            const { pageX: x, pageY: y } = event
            // 鼠标点击事件偏移阈值
            if (
                Math.abs(x - this.moveFlag.x) > 2
                || Math.abs(y - this.moveFlag.y) > 2
            ) {
                this.moveFlag.moved = true
            }
        }
    }
}
</script>
<style lang="scss">
.bk-flow-location {
    .circle-node {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        text-align: center;
    }
    .startpoint {
        border: 4px solid #6a6c8a;
    }
    .endpoint {
        background: #6a6c8a;
    }
    .tasknode {
        width: 80px;
        height: 50px;
        border: 2px solid #33d0c6;
    }
    .gateway {
        width: 30px;
        height: 30px;
        background: #7c68fc;
        transform: rotate(-45deg);
    }
    .node-default {
        width: 120px;
        height: 80px;
        line-height: 80px;
        border: 1px solid #cccccc;
        border-radius: 2px;
        text-align: center;
        &.selected {
            border: 1px solid #3a84ff;
        }
    }
}
</style>

