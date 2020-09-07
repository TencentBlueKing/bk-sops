<template>
  <div
    class="bk-flow-location"
    @mousedown="onMouseDown"
    @mouseup="onMouseUp">
    <div v-if="node.type === 'startpoint'" class="node startpoint">start</div>
    <div v-if="node.type === 'endpoint'" class="node endpoint">end</div>
    <div v-if="node.type === 'tasknode'" class="node common-node">taskNode</div>
    <div v-if="node.type === 'subflow'" class="node common-node">subFlow</div>
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
      if (
        Math.abs(x - this.moveFlag.x) > 20
        || Math.abs(y - this.moveFlag.y) > 20
      ) {
        this.moveFlag.moved = true
      }
    }
  }
}
</script>
<style lang="scss" scoped>
.common-node {
  width: 120px;
  height: 60px;
  line-height: 60px;
  border: 1px solid #cccccc;
  text-align: center;
  background: #ffffff;
  cursor: pointer;
  &:hover {
    border-color: #348aff;
  }
}
.startpoint,
.endpoint {
  width: 60px;
  height: 60px;
  line-height: 60px;
  border-radius: 50%;
  border: 1px solid #cccccc;
  text-align: center;
  background: #ffffff;
}
.canvas-node.selected .node{
  border-color: #348aff;
}
</style>

