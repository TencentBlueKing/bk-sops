import * as G2Plot from '@antv/g2plot'
const container = document.getElementById('app');
const data = [
  {
    "series": "bamboo-engine",
    "x": "100",
    "y": 1.33
  },
  {
    "series": "bamboo-engine",
    "x": "500",
    "y": 9.66
  },
  {
    "series": "bamboo-engine",
    "x": "1000",
    "y": 19.33
  },
  {
    "series": "bamboo-engine",
    "x": "5000",
    "y": 154.33
  },
  {
    "series": "pipeline",
    "y": 6,
    "x": "100"
  },
  {
    "series": "pipeline",
    "y": 91,
    "x": "500"
  },
  {
    "series": "pipeline",
    "y": 545,
    "x": "1000"
  },
  {
    "series": "pipeline",
    "y": null,
    "x": "5000"
  },
  {
    "x": "10000",
    "y": 347.5,
    "series": "bamboo-engine"
  },
  {
    "x": "10000",
    "y": null,
    "series": "pipeline"
  }
];
const config = {
  "title": {
    "visible": true,
    "text": "大流程执行"
  },
  "description": {
    "visible": true,
    "text": "并行网关连接多个节点(100 gevent)"
  },
  "legend": {
    "flipPage": false
  },
  "xAxis": {
    "title": {
      "visible": true,
      "text": "并发数"
    }
  },
  "yAxis": {
    "title": {
      "visible": true,
      "text": "耗时(s)"
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
    "#5B8FF9",
    "#5AD8A6"
  ]
}
const plot = new G2Plot.Line(container, {
  data,
  ...config,
});
plot.render();
