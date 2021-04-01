import * as G2Plot from '@antv/g2plot'
const container = document.getElementById('app');
const data = [
  {
    "series": "100流程(17节点)并发执行",
    "x": "100",
    "y": 25.98
  },
  {
    "series": "100流程(17节点)并发执行",
    "x": "200",
    "y": 14.75
  },
  {
    "series": "100流程(17节点)并发执行",
    "x": "500",
    "y": 8.29
  },
  {
    "series": "100流程(17节点)并发执行",
    "x": "1000",
    "y": 6.78
  },
  {
    "series": "1000节点大流程",
    "y": 19.33,
    "x": "100"
  },
  {
    "series": "1000节点大流程",
    "y": 12.5,
    "x": "200"
  },
  {
    "series": "1000节点大流程",
    "y": 11,
    "x": "500"
  },
  {
    "series": "1000节点大流程",
    "y": 7.5,
    "x": "1000"
  }
];
const config = {
  "title": {
    "visible": true,
    "text": "水平扩展测试"
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
      "text": "gevent worker 数"
    }
  },
  "yAxis": {
    "title": {
      "visible": true,
      "text": "流程执行耗时"
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
