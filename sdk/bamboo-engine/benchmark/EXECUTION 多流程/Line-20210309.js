import * as G2Plot from '@antv/g2plot'
const container = document.getElementById('app');
const data = [
  {
    "series": "bamboo-engine",
    "x": "100",
    "y": 25.98
  },
  {
    "series": "bamboo-engine",
    "x": "500",
    "y": 138
  },
  {
    "series": "bamboo-engine",
    "x": "1000",
    "y": 272
  },
  {
    "series": "bamboo-engine",
    "x": "5000",
    "y": 2442
  },
  {
    "series": "pipeline",
    "y": 48.77,
    "x": "100"
  },
  {
    "series": "pipeline",
    "y": 311,
    "x": "500"
  },
  {
    "series": "pipeline",
    "y": 748,
    "x": "1000"
  },
  {
    "series": "pipeline",
    "y": null,
    "x": "5000"
  }
];
const config = {
  "title": {
    "visible": true,
    "text": "多流程并发执行"
  },
  "description": {
    "visible": true,
    "text": "17个节点，子流程，并行、分支网关(100 gevent)"
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
      "text": "公平调度平均耗时(s)"
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
