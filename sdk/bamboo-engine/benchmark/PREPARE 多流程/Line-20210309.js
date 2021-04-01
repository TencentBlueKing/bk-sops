import * as G2Plot from '@antv/g2plot'
const container = document.getElementById('app');
const data = [
  {
    "series": "normal(20 nodes 14 vars) 100 并发",
    "x": "100",
    "y": 0.76
  },
  {
    "series": "normal(20 nodes 14 vars) 100 并发",
    "x": "500",
    "y": 1.68
  },
  {
    "series": "normal(20 nodes 14 vars) 100 并发",
    "x": "1000",
    "y": 3.19
  },
  {
    "series": "normal(20 nodes 14 vars) 100 并发",
    "x": "5000",
    "y": 13
  },
  {
    "x": "10000",
    "y": 30,
    "series": "normal(20 nodes 14 vars) 100 并发"
  }
];
const config = {
  "title": {
    "visible": true,
    "text": "任务创建耗时"
  },
  "description": {
    "visible": true
  },
  "legend": {
    "flipPage": false
  },
  "xAxis": {
    "title": {
      "visible": true,
      "text": "流程数"
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
    "#5B8FF9"
  ]
}
const plot = new G2Plot.Line(container, {
  data,
  ...config,
});
plot.render();
