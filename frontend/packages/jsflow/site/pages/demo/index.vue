<template>
  <div class="page-home">
    <div class="main-content-area">
      <div class="canvas-container">
        <js-flow
          ref="jsFlow"
          selector="entry-item"
          :data="canvasData"
          :editable="editable"
          :endpointOptions="endpointOptions"
          :connectorOptions="connectorOptions"
          @onNodeMoving="onNodeMoving"
          @onNodeMoveStop="onNodeMoveStop"
          @onToolClick="onToolClick"
          @onCreateNodeBefore="onCreateNodeBefore"
          @onConnectionDragStop="onConnectionDragStop">
          <template v-slot:palettePanel>
            <Palette></Palette>
          </template>
          <template v-slot:nodeTemplate="{ node }">
            <node-template :node="node"></node-template>
          </template>
        </js-flow>
      </div>
    </div>
  </div>
</template>
<script>
import JsFlow from '../../../src/'
import NodeTemplate from './NodeTemplate.vue'
import Palette from './Palette.vue'
const lines = [
  {
    id: 'line123feod03j26895c557a452252f0',
    source: {
      arrow: 'Right',
      id: 'nodeb662bc1afb5e60daa67e69f48de1'
    },
    target: {
      arrow: 'Left',
      id: 'node74b1ec6275b60d5c22c9848466f1'
    }
  },
  {
    id: 'line332309df3j26895c557a4522fd0d',
    source: {
      arrow: 'Right',
      id: 'node74b1ec6275b60d5c22c9848466f1'
    },
    target: {
      arrow: 'Left',
      id: 'noded782259a6895c557a452252ec65a'
    }
  }
]

const nodes = [
  {
    id: 'nodeb662bc1afb5e60daa67e69f48de1',
    x: 20,
    y: 80,
    type: 'startpoint',
    anchor: ['Left', 'Right']
  },
  {
    id: 'node74b1ec6275b60d5c22c9848466f1',
    x: 220,
    y: 80,
    type: 'tasknode',
    anchor: ['Top', 'Left', 'Bottom', 'Right']
  },
  {
    id: 'noded782259a6895c557a452252ec65a',
    x: 380,
    y: 80,
    type: 'endpoint',
    anchor: ['Left', 'Bottom']
  }
]

// 端点配置项
const endpointOptions = {
  endpoint: 'Dot',
  connectorOverlays: [
      ['PlainArrow', { width: 8, length: 6, location: 1, id: 'arrow' }]
  ],
  paintStyle: { stroke: 'rgba(52, 138, 243, 0.15)', strokeWidth: 1, radius: 7 },
  hoverPaintStyle: { fill: '#348af3', stroke: '#348af3' },
  cssClass: 'template-canvas-endpoint',
  hoverClass: 'template-canvas-endpoint-hover',
  isSource: true, // 端点是否可以作为拖动源
  isTarget: true, // 端点是否可以作为拖动目标
  maxConnections: -1 // 不设置最大连接数
}

// 连接线配置项
export const connectorOptions = {
    connector: ['Bezier', { curviness: 30 }],
    paintStyle: {
        strokeWidth: 2,
        stroke: '#9f9f9f',
        outlineStroke: 'tranparent',
        outlineWidth: 4
    },
    hoverPaintStyle: { stroke: '#3a84ff' }
}

export default {
  name: 'Demo',
  components: {
    JsFlow,
    NodeTemplate,
    Palette
  },
  data () {
    return {
      editable: true,
      endpointOptions,
      connectorOptions,
      canvasData: {
        nodes,
        lines
      }
    }
  },
  mounted () {
    this.addLineOverlay()
  },
  methods: {
    onToolClick (tool) {
      console.log(tool)
    },
    addLineOverlay () {
      this.$refs.jsFlow.addLineOverlay(lines[0], {
        type: 'Label',
        name: 'some condition',
        location: 0.5,
        id: 'test'
      })
    },
    onCreateNodeBefore (node) {
      return true
    },
    onNodeMoving (node, event) {
      console.log('moving')
    },
    onNodeMoveStop (node, event) {
      console.log('moveStop')
    },
    onConnectionDragStop (source, targetId, event) {
      let arrow
      const line = {
        source,
        target: {
          id: targetId
        }
      }
      const nodeEl = document.getElementById(targetId)
      const nodeRects = nodeEl.getBoundingClientRect()
      const offsetX = event.clientX - nodeRects.left
      const offsetY = event.clientY - nodeRects.top
      if (offsetX < nodeRects.width / 2) {
          if (offsetY < nodeRects.height / 2) {
              arrow = offsetX > offsetY ? 'Top' : 'Left'
          } else {
              arrow = offsetX > (nodeRects.height - offsetY) ? 'Bottom' : 'Left'
          }
      } else {
          if (offsetY < nodeRects.height / 2) {
              arrow = (nodeRects.width - offsetX) > offsetY ? 'Top' : 'Right'
          } else {
              arrow = (nodeRects.width - offsetX) > (nodeRects.height - offsetY) ? 'Bottom' : 'Right'
          }
      }

      line.target.arrow = arrow
      this.$refs.jsFlow.createConnector(line)
    }
  }
}
</script>
<style lang="scss">
.page-home {
  height: calc(100% - 60px);
}
.main-content-area {
  height: 100%;
}
.canvas-container {
  height: 600px;
}
.jtk-overlay {
  height: 30px;
  line-height: 30px;
  background: #d9e9fa;
  white-space: nowrap;
}
</style>