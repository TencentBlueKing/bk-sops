import * as G2Plot from '@antv/g2plot'
const container = document.getElementById('app');
const data = [
  {
    "series": "单流程多节点",
    "x": "100",
    "y": 0.05
  },
  {
    "series": "单流程多节点",
    "x": "500",
    "y": 0.05
  },
  {
    "series": "单流程多节点",
    "x": "1000",
    "y": 0.09
  },
  {
    "series": "单流程多节点",
    "x": "5000",
    "y": 0.45
  },
  {
    "x": "10000",
    "y": 0.91,
    "series": "单流程多节点"
  },
  {
    "x": "100000",
    "y": 9.32,
    "series": "单流程多节点"
  }
];
const config = {
  "title": {
    "text": "任务创建耗时"
  },
  "description": {
    "visible": true,
    "text": "并行网关后多个节点"
  },
  "legend": {
    "flipPage": false
  },
  "xAxis": {
    "title": {
      "visible": true,
      "text": "耗时(s)"
    }
  },
  "yAxis": {
    "title": {
      "visible": true,
      "text": "节点数"
    }
  },
  "label": {
    "visible": true
  },
  "smooth": true,
  "point": {
    "size": 0
  },
  "forceFit": false,
  "width": 1097,
  "height": 532,
  "xField": "x",
  "yField": "y",
  "seriesField": "series",
  "color": [
    "#5B8FF9"
  ]
}
const plot = new G2Plot.Line(container, {
  data,
  ...config,
});
plot.render();
