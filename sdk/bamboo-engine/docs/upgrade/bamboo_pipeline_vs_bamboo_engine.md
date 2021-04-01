<!-- TOC -->

- [bamboo-pipeline 与 bamboo-engine 性能对比](#bamboo-pipeline-与-bamboo-engine-性能对比)
  - [单个大流程执行](#单个大流程执行)
  - [多流程并行执行](#多流程并行执行)

<!-- /TOC -->

## bamboo-pipeline 与 bamboo-engine 性能对比

测试环境：

- MacBook Pro（16 英寸，2019）
- 处理器：2.6 GHz 六核Intel Core i7
- 内存：32 GB 2667 MHz DDR4
- OS：macOS Big Sur 11.2.1
- Broker：RabbitMQ 3.8.2
- MySQL：5.7.22

### 单个大流程执行

|引擎|节点数|执行耗时|
|-|-|-|
|bamboo-engine|100|1.33|
|bamboo-engine|500|9.66|
|bamboo-engine|1000|19.33|
|bamboo-engine|5000|154.33|
|bamboo-engine|10000|347.5|
|pipeline|100|6|
|pipeline|500|91|
|pipeline|1000|545|
|pipeline|5000|-|
|pipeline|10000|-|

![](../../benchmark/EXECUTION%20单流程多节点/Line-20210309.png)

### 多流程并行执行

|引擎|流程数|单个流程执行耗时|
|-|-|-|
|bamboo-engine|100|25.98|
|bamboo-engine|500|138|
|bamboo-engine|1000|272|
|bamboo-engine|5000|2442|
|pipeline|100|48.77|
|pipeline|500|311|
|pipeline|1000|748|
|pipeline|5000|-|

![](../../benchmark/EXECUTION%20多流程/Line-20210309.png)
