# 流程分析算法设计文档

## 一、概述

本文档详细设计了流程分析的各个算法，包括算法的输入数据、处理步骤、输出结果和依赖关系。算法分为基础算法和高级算法两类，基础算法可直接基于现成数据实施，高级算法需要知识库支持。

### 算法分类

```
流程分析算法
├── 基础算法（可直接实施）
│   ├── 流程结构分析算法
│   ├── 流程执行分析算法
│   ├── 节点使用分析算法
│   ├── 业务场景分析算法
│   └── 质量分析算法（基础部分）
└── 高级算法（需要知识库）
    ├── 流程模式识别算法
    ├── 节点组合模式识别算法
    └── 基于最佳实践的质量分析算法
```

---

## 二、流程结构分析算法

### 2.1 流程深度计算算法（基础）

#### 算法名称
`calculate_flow_depth`

#### 输入数据
- `pipeline_tree`：流程树字典
  - `start_event`：开始节点
  - `end_event`：结束节点
  - `flows`：顺序流字典
  - `activities`：任务节点字典
  - `gateways`：网关节点字典

#### 处理步骤

1. **构建有向图**
   ```python
   # 从flows构建有向图
   graph = {}
   for flow_id, flow in flows.items():
       source = flow['source']
       target = flow['target']
       if source not in graph:
           graph[source] = []
       graph[source].append(target)
   ```

2. **计算最长路径**
   ```python
   # 使用动态规划或DFS计算从start_event到end_event的最长路径
   def dfs(node, visited, path_length):
       if node == end_event_id:
           return path_length
       max_length = 0
       for next_node in graph.get(node, []):
           if next_node not in visited:
               visited.add(next_node)
               length = dfs(next_node, visited, path_length + 1)
               max_length = max(max_length, length)
               visited.remove(next_node)
       return max_length

   depth = dfs(start_event_id, set(), 0)
   ```

3. **返回结果**
   - 返回最长路径长度（节点数）

#### 输出结果
- `flow_depth`：整数，流程的最大深度

#### 依赖关系
- ✅ 基础算法，无需知识库
- 数据来源：`pipeline_tree`

#### 时间复杂度
- O(V + E)，其中V是节点数，E是边数

---

### 2.2 流程模式识别算法（基础）

#### 算法名称
`identify_basic_flow_pattern`

#### 输入数据
- `pipeline_tree`：流程树字典

#### 处理步骤

1. **识别串行模式**
   ```python
   # 统计只有一个incoming和一个outgoing的节点
   serial_nodes = []
   for node_id, node in activities.items():
       incoming = node.get('incoming', [])
       outgoing = node.get('outgoing', '')
       if isinstance(incoming, str):
           incoming = [incoming]
       if len(incoming) == 1 and outgoing:
           serial_nodes.append(node_id)
   serial_ratio = len(serial_nodes) / total_nodes
   ```

2. **识别并行模式**
   ```python
   # 统计并行网关的数量和分支数
   parallel_gateways = []
   for gateway_id, gateway in gateways.items():
       if gateway['type'] == 'ParallelGateway':
           branch_count = len(gateway.get('outgoing', []))
           parallel_gateways.append({
               'id': gateway_id,
               'branches': branch_count
           })
   ```

3. **识别混合模式**
   ```python
   # 如果既有串行节点又有并行网关，则为混合模式
   if serial_nodes and parallel_gateways:
       pattern = 'mixed'
   elif parallel_gateways:
       pattern = 'parallel'
   else:
       pattern = 'serial'
   ```

#### 输出结果
- `flow_pattern`：字符串（'serial', 'parallel', 'mixed'）
- `serial_ratio`：浮点数（串行节点比例）
- `parallel_branches`：整数列表（并行分支数）

#### 依赖关系
- ✅ 基础算法，无需知识库

---

### 2.3 流程模式匹配算法（高级）

#### 算法名称
`match_flow_pattern_with_knowledge_base`

#### 输入数据
- `pipeline_tree`：流程树字典
- `knowledge_base`：知识库接口（包含流程模式知识）

#### 处理步骤

1. **向量化流程结构**
   ```python
   # 将流程结构转换为向量表示
   flow_vector = vectorize_flow_structure(pipeline_tree)
   # 包括：节点类型序列、网关类型、连接关系等
   ```

2. **检索相似模式**
   ```python
   # 从知识库检索相似的流程模式
   similar_patterns = knowledge_base.query(
       vector=flow_vector,
       top_k=5,
       threshold=0.7
   )
   ```

3. **匹配最佳模式**
   ```python
   # 计算与每个模式的相似度
   best_match = None
   best_score = 0
   for pattern in similar_patterns:
       score = calculate_similarity(flow_vector, pattern.vector)
       if score > best_score:
           best_score = score
           best_match = pattern
   ```

4. **返回匹配结果**
   ```python
   return {
       'pattern_type': best_match.type,
       'match_score': best_score,
       'pattern_name': best_match.name
   }
   ```

#### 输出结果
- `pattern_type`：字符串（流程模式类型）
- `match_score`：浮点数（匹配度，0-1）
- `pattern_name`：字符串（模式名称）

#### 依赖关系
- ⚠️ 高级算法，需要知识库支持
- 需要知识库中的流程模式向量和模式知识

---

## 三、流程执行分析算法

### 3.1 执行频率统计算法（基础）

#### 算法名称
`calculate_execution_frequency`

#### 输入数据
- `template_id`：模板ID
- `start_date`：开始日期（可选）
- `end_date`：结束日期（可选）

#### 处理步骤

1. **查询执行记录**
   ```python
   # 从TaskflowStatistics查询执行记录
   query = TaskflowStatistics.objects.filter(
       template_id=template_id
   )
   if start_date:
       query = query.filter(create_time__gte=start_date)
   if end_date:
       query = query.filter(create_time__lte=end_date)

   executions = query.values('create_time')
   ```

2. **统计总执行次数**
   ```python
   total_executions = executions.count()
   ```

3. **计算日均/周均/月均**
   ```python
   if start_date and end_date:
       days = (end_date - start_date).days + 1
       daily_avg = total_executions / days
       weekly_avg = total_executions / (days / 7)
       monthly_avg = total_executions / (days / 30)
   ```

4. **按时间维度分组统计**
   ```python
   # 按日分组
   daily_stats = executions.annotate(
       date=TruncDate('create_time')
   ).values('date').annotate(
       count=Count('id')
   ).order_by('date')
   ```

#### 输出结果
- `total_executions`：整数（总执行次数）
- `daily_avg_executions`：浮点数（日均执行次数）
- `weekly_avg_executions`：浮点数（周均执行次数）
- `monthly_avg_executions`：浮点数（月均执行次数）
- `daily_trend`：字典（日期 -> 执行次数）

#### 依赖关系
- ✅ 基础算法，无需知识库
- 数据来源：`TaskflowStatistics`

---

### 3.2 成功率计算算法（基础）

#### 算法名称
`calculate_success_rate`

#### 输入数据
- `template_id`：模板ID
- `start_date`：开始日期（可选）
- `end_date`：结束日期（可选）

#### 处理步骤

1. **查询任务实例**
   ```python
   # 从TaskflowStatistics获取实例ID列表
   taskflow_stats = TaskflowStatistics.objects.filter(
       template_id=template_id
   )
   if start_date:
       taskflow_stats = taskflow_stats.filter(create_time__gte=start_date)
   if end_date:
       taskflow_stats = taskflow_stats.filter(create_time__lte=end_date)

   instance_ids = taskflow_stats.values_list('instance_id', flat=True)
   ```

2. **查询任务状态**
   ```python
   # 从TaskFlowInstance查询任务状态
   tasks = TaskFlowInstance.objects.filter(
       pipeline_instance__instance_id__in=instance_ids
   )

   total_count = tasks.count()
   successful_count = tasks.filter(status='FINISHED').count()
   failed_count = tasks.filter(status='FAILED').count()
   ```

3. **计算成功率**
   ```python
   success_rate = successful_count / total_count if total_count > 0 else 0
   failure_rate = failed_count / total_count if total_count > 0 else 0
   ```

4. **计算节点成功率**
   ```python
   # 从TaskflowExecutedNodeStatistics统计节点执行情况
   node_stats = TaskflowExecutedNodeStatistics.objects.filter(
       template_id=template_id
   )
   if start_date:
       node_stats = node_stats.filter(instance_create_time__gte=start_date)
   if end_date:
       node_stats = node_stats.filter(instance_create_time__lte=end_date)

   node_total = node_stats.count()
   node_successful = node_stats.filter(status=True).count()
   node_success_rate = node_successful / node_total if node_total > 0 else 0
   ```

#### 输出结果
- `success_rate`：浮点数（0-1，流程成功率）
- `failure_rate`：浮点数（0-1，流程失败率）
- `node_success_rate`：浮点数（0-1，节点成功率）

#### 依赖关系
- ✅ 基础算法，无需知识库
- 数据来源：`TaskflowStatistics`, `TaskFlowInstance`, `TaskflowExecutedNodeStatistics`

---

### 3.3 耗时统计算法（基础）

#### 算法名称
`calculate_elapsed_time_statistics`

#### 输入数据
- `template_id`：模板ID
- `start_date`：开始日期（可选）
- `end_date`：结束日期（可选）

#### 处理步骤

1. **查询执行耗时数据**
   ```python
   # 从TaskflowStatistics查询耗时数据
   taskflow_stats = TaskflowStatistics.objects.filter(
       template_id=template_id
   ).exclude(elapsed_time__isnull=True)

   if start_date:
       taskflow_stats = taskflow_stats.filter(create_time__gte=start_date)
   if end_date:
       taskflow_stats = taskflow_stats.filter(create_time__lte=end_date)

   elapsed_times = list(taskflow_stats.values_list('elapsed_time', flat=True))
   ```

2. **计算基础统计量**
   ```python
   import numpy as np

   if elapsed_times:
       avg_elapsed_time = np.mean(elapsed_times)
       median_elapsed_time = np.median(elapsed_times)
       max_elapsed_time = np.max(elapsed_times)
       min_elapsed_time = np.min(elapsed_times)
       std_elapsed_time = np.std(elapsed_times)
   ```

3. **计算百分位数**
   ```python
   p50_elapsed_time = np.percentile(elapsed_times, 50)
   p90_elapsed_time = np.percentile(elapsed_times, 90)
   p95_elapsed_time = np.percentile(elapsed_times, 95)
   p99_elapsed_time = np.percentile(elapsed_times, 99)
   ```

4. **按时间维度统计趋势**
   ```python
   # 按周分组统计平均耗时
   weekly_stats = taskflow_stats.annotate(
       week=TruncWeek('create_time')
   ).values('week').annotate(
       avg_elapsed_time=Avg('elapsed_time'),
       count=Count('id')
   ).order_by('week')
   ```

#### 输出结果
- `avg_elapsed_time`：浮点数（平均耗时，秒）
- `median_elapsed_time`：浮点数（中位数耗时，秒）
- `p90_elapsed_time`：浮点数（P90耗时，秒）
- `p95_elapsed_time`：浮点数（P95耗时，秒）
- `p99_elapsed_time`：浮点数（P99耗时，秒）
- `weekly_trend`：字典（周 -> 平均耗时）

#### 依赖关系
- ✅ 基础算法，无需知识库
- 数据来源：`TaskflowStatistics`

---

## 四、节点使用分析算法

### 4.1 节点使用频率统计算法（基础）

#### 算法名称
`calculate_node_usage_frequency`

#### 输入数据
- `component_code`：组件代码（可选，如果为空则统计所有节点）
- `start_date`：开始日期（可选）
- `end_date`：结束日期（可选）

#### 处理步骤

1. **查询节点引用统计**
   ```python
   # 从TemplateNodeStatistics查询节点引用情况
   query = TemplateNodeStatistics.objects.all()
   if component_code:
       query = query.filter(component_code=component_code)
   if start_date:
       query = query.filter(template_create_time__gte=start_date)
   if end_date:
       query = query.filter(template_create_time__lte=end_date)

   # 按component_code分组统计
   usage_stats = query.values('component_code').annotate(
       usage_count=Count('id'),
       template_count=Count('template_id', distinct=True)
   ).order_by('-usage_count')
   ```

2. **计算使用率**
   ```python
   # 获取总模板数
   total_templates = TaskTemplate.objects.filter(
       is_deleted=False
   ).count()

   # 计算每个节点的使用率
   for stat in usage_stats:
       stat['usage_ratio'] = stat['template_count'] / total_templates if total_templates > 0 else 0
   ```

3. **获取Top N节点**
   ```python
   top_n_nodes = usage_stats[:n]  # n为配置的Top N数量
   ```

#### 输出结果
- `node_usage_stats`：列表（每个节点包含：component_code, usage_count, template_count, usage_ratio）
- `top_n_nodes`：列表（使用频率最高的N个节点）

#### 依赖关系
- ✅ 基础算法，无需知识库
- 数据来源：`TemplateNodeStatistics`, `TaskTemplate`

---

### 4.2 节点组合分析算法（基础）

#### 算法名称
`analyze_node_combinations`

#### 输入数据
- `template_id`：模板ID（可选，如果为空则分析所有模板）

#### 处理步骤

1. **获取流程树**
   ```python
   if template_id:
       templates = [TaskTemplate.objects.get(id=template_id)]
   else:
       templates = TaskTemplate.objects.filter(is_deleted=False)

   all_combinations = []
   for template in templates:
       pipeline_tree = template.pipeline_tree
       flows = pipeline_tree.get('flows', {})
   ```

2. **提取节点序列**
   ```python
   # 从flows构建节点序列
   node_sequences = []
   for flow_id, flow in flows.items():
       source = flow['source']
       target = flow['target']
       # 获取source和target的component_code
       source_component = get_component_code(source, pipeline_tree)
       target_component = get_component_code(target, pipeline_tree)
       if source_component and target_component:
           node_sequences.append((source_component, target_component))
   ```

3. **统计常见组合**
   ```python
   from collections import Counter

   # 统计所有模板中的节点组合
   all_combinations.extend(node_sequences)
   combination_counter = Counter(all_combinations)

   # 获取最常见的组合
   common_combinations = combination_counter.most_common(n)
   ```

4. **分析节点前置/后置关系**
   ```python
   # 构建节点关系图
   node_predecessors = {}
   node_successors = {}

   for source, target in all_combinations:
       if target not in node_predecessors:
           node_predecessors[target] = []
       node_predecessors[target].append(source)

       if source not in node_successors:
           node_successors[source] = []
       node_successors[source].append(target)
   ```

#### 输出结果
- `common_combinations`：列表（(source_component, target_component) -> count）
- `node_predecessors`：字典（节点 -> 前置节点列表）
- `node_successors`：字典（节点 -> 后置节点列表）

#### 依赖关系
- ✅ 基础算法，无需知识库
- 数据来源：`pipeline_tree.flows`

---

### 4.3 节点组合模式识别算法（高级）

#### 算法名称
`identify_node_combination_patterns`

#### 输入数据
- `node_combinations`：节点组合列表（来自基础算法）
- `knowledge_base`：知识库接口

#### 处理步骤

1. **向量化节点组合**
   ```python
   # 将节点组合转换为向量表示
   combination_vectors = []
   for combination in node_combinations:
       vector = vectorize_combination(combination)
       combination_vectors.append({
           'combination': combination,
           'vector': vector
       })
   ```

2. **从知识库检索模式**
   ```python
   # 从知识库检索节点组合模式
   patterns = knowledge_base.query_node_combination_patterns(
       combinations=combination_vectors,
       top_k=10
   )
   ```

3. **匹配组合模式**
   ```python
   matched_patterns = []
   for pattern in patterns:
       for combo_vec in combination_vectors:
           similarity = calculate_similarity(
               combo_vec['vector'],
               pattern.vector
           )
           if similarity > threshold:
               matched_patterns.append({
                   'combination': combo_vec['combination'],
                   'pattern': pattern.name,
                   'similarity': similarity
               })
   ```

#### 输出结果
- `matched_patterns`：列表（匹配的组合模式及其相似度）

#### 依赖关系
- ⚠️ 高级算法，需要知识库支持
- 需要知识库中的节点组合模式知识

---

## 五、业务场景分析算法

### 5.1 场景分布统计算法（基础）

#### 算法名称
`calculate_category_distribution`

#### 输入数据
- `start_date`：开始日期（可选）
- `end_date`：结束日期（可选）

#### 处理步骤

1. **统计模板分布**
   ```python
   # 从TaskTemplate统计各分类的模板数量
   template_dist = TaskTemplate.objects.filter(
       is_deleted=False
   ).values('category').annotate(
       template_count=Count('id')
   ).order_by('-template_count')

   total_templates = TaskTemplate.objects.filter(is_deleted=False).count()

   # 计算占比
   for dist in template_dist:
       dist['template_ratio'] = dist['template_count'] / total_templates
   ```

2. **统计执行分布**
   ```python
   # 从TaskflowStatistics统计各分类的执行次数
   execution_dist = TaskflowStatistics.objects.all()
   if start_date:
       execution_dist = execution_dist.filter(create_time__gte=start_date)
   if end_date:
       execution_dist = execution_dist.filter(create_time__lte=end_date)

   execution_dist = execution_dist.values('category').annotate(
       execution_count=Count('id')
   ).order_by('-execution_count')

   total_executions = execution_dist.aggregate(Sum('execution_count'))['execution_count__sum']

   # 计算占比
   for dist in execution_dist:
       dist['execution_ratio'] = dist['execution_count'] / total_executions if total_executions > 0 else 0
   ```

#### 输出结果
- `template_distribution`：列表（category -> template_count, template_ratio）
- `execution_distribution`：列表（category -> execution_count, execution_ratio）

#### 依赖关系
- ✅ 基础算法，无需知识库
- 数据来源：`TaskTemplate.category`, `TaskflowStatistics.category`

---

### 5.2 场景成功率统计算法（基础）

#### 算法名称
`calculate_category_success_rate`

#### 输入数据
- `category`：分类（可选）
- `start_date`：开始日期（可选）
- `end_date`：结束日期（可选）

#### 处理步骤

1. **查询执行记录**
   ```python
   # 从TaskflowStatistics查询执行记录
   query = TaskflowStatistics.objects.all()
   if category:
       query = query.filter(category=category)
   if start_date:
       query = query.filter(create_time__gte=start_date)
   if end_date:
       query = query.filter(create_time__lte=end_date)

   instance_ids = query.values_list('instance_id', flat=True)
   ```

2. **查询任务状态**
   ```python
   # 从TaskFlowInstance查询任务状态
   tasks = TaskFlowInstance.objects.filter(
       pipeline_instance__instance_id__in=instance_ids
   )

   # 按分类分组统计
   if not category:
       # 需要关联TaskflowStatistics获取category
       tasks = tasks.annotate(
           category=Subquery(
               TaskflowStatistics.objects.filter(
                   instance_id=OuterRef('pipeline_instance__instance_id')
               ).values('category')[:1]
           )
       )

   category_stats = tasks.values('category').annotate(
       total_count=Count('id'),
       successful_count=Count('id', filter=Q(status='FINISHED')),
       failed_count=Count('id', filter=Q(status='FAILED'))
   )
   ```

3. **计算成功率**
   ```python
   for stat in category_stats:
       stat['success_rate'] = stat['successful_count'] / stat['total_count'] if stat['total_count'] > 0 else 0
       stat['failure_rate'] = stat['failed_count'] / stat['total_count'] if stat['total_count'] > 0 else 0
   ```

#### 输出结果
- `category_success_stats`：列表（category -> success_rate, failure_rate, total_count）

#### 依赖关系
- ✅ 基础算法，无需知识库
- 数据来源：`TaskflowStatistics`, `TaskFlowInstance`

---

## 六、质量分析算法

### 6.1 综合质量评分算法（基础）

#### 算法名称
`calculate_comprehensive_quality_score`

#### 输入数据
- `template_id`：模板ID
- `weights`：权重配置（可选）

#### 处理步骤

1. **获取各维度指标**
   ```python
   # 获取执行质量指标
   execution_quality = calculate_execution_quality_score(template_id)
   # 返回：success_rate, avg_elapsed_time

   # 获取结构质量指标
   structure_quality = calculate_structure_quality_score(template_id)
   # 返回：complexity_score, reusability_score

   # 获取使用质量指标
   usage_quality = calculate_usage_quality_score(template_id)
   # 返回：usage_frequency, stability_score
   ```

2. **归一化指标**
   ```python
   # 归一化耗时（越小越好，转换为0-1）
   normalized_elapsed_time = 1 - min(avg_elapsed_time / max_elapsed_time, 1)

   # 归一化复杂度（越小越好，转换为0-1）
   normalized_complexity = 1 - min(complexity_score / max_complexity, 1)
   ```

3. **计算综合评分**
   ```python
   # 默认权重
   weights = weights or {
       'success_rate': 0.5,
       'efficiency': 0.3,
       'complexity': 0.2
   }

   comprehensive_score = (
       weights['success_rate'] * execution_quality['success_rate'] +
       weights['efficiency'] * normalized_elapsed_time +
       weights['complexity'] * normalized_complexity
   )
   ```

#### 输出结果
- `comprehensive_quality_score`：浮点数（0-1，综合质量评分）
- `execution_quality_score`：浮点数（0-1，执行质量评分）
- `structure_quality_score`：浮点数（0-1，结构质量评分）
- `usage_quality_score`：浮点数（0-1，使用质量评分）

#### 依赖关系
- ✅ 基础算法，无需知识库
- 依赖其他分析算法的结果

---

### 6.2 基于最佳实践的优化建议算法（高级）

#### 算法名称
`generate_optimization_suggestions`

#### 输入数据
- `template_id`：模板ID
- `knowledge_base`：知识库接口

#### 处理步骤

1. **获取当前流程信息**
   ```python
   template = TaskTemplate.objects.get(id=template_id)
   pipeline_tree = template.pipeline_tree
   current_metrics = calculate_all_metrics(template_id)
   ```

2. **检索最佳实践**
   ```python
   # 从知识库检索最佳实践
   best_practices = knowledge_base.query_best_practices(
       category=template.category,
       pattern_type=current_metrics['pattern_type']
   )
   ```

3. **对比分析**
   ```python
   suggestions = []
   for practice in best_practices:
       # 对比当前流程与最佳实践
       differences = compare_with_best_practice(
           current_metrics,
           practice.metrics
       )

       # 生成优化建议
       for diff in differences:
           if diff['type'] == 'structure':
               suggestions.append({
                   'type': 'structure',
                   'suggestion': f"建议优化流程结构：{diff['description']}",
                   'priority': diff['priority']
               })
           elif diff['type'] == 'node_combination':
               suggestions.append({
                   'type': 'node_combination',
                   'suggestion': f"建议优化节点组合：{diff['description']}",
                   'priority': diff['priority']
               })
   ```

4. **排序建议**
   ```python
   # 按优先级排序
   suggestions.sort(key=lambda x: x['priority'], reverse=True)
   ```

#### 输出结果
- `optimization_suggestions`：列表（优化建议，包含类型、描述、优先级）

#### 依赖关系
- ⚠️ 高级算法，需要知识库支持
- 需要知识库中的最佳实践知识

---

## 七、算法实施优先级

### 7.1 基础算法实施顺序

| 优先级 | 算法 | 实施阶段 |
|-------|------|---------|
| P0 | 流程深度计算算法 | 阶段五基础部分 |
| P0 | 流程模式识别算法（基础） | 阶段五基础部分 |
| P0 | 执行频率统计算法 | 阶段五基础部分 |
| P0 | 成功率计算算法 | 阶段五基础部分 |
| P0 | 耗时统计算法 | 阶段五基础部分 |
| P0 | 节点使用频率统计算法 | 阶段五基础部分 |
| P0 | 节点组合分析算法 | 阶段五基础部分 |
| P0 | 场景分布统计算法 | 阶段五基础部分 |
| P0 | 场景成功率统计算法 | 阶段五基础部分 |
| P1 | 综合质量评分算法 | 阶段五基础部分 |

### 7.2 高级算法实施顺序

| 优先级 | 算法 | 实施阶段 |
|-------|------|---------|
| P2 | 流程模式匹配算法 | 阶段五高级部分 |
| P2 | 节点组合模式识别算法 | 阶段五高级部分 |
| P2 | 基于最佳实践的优化建议算法 | 阶段五高级部分 |

---

## 八、总结

本文档设计了13个分析算法，其中10个为基础算法（可直接实施），3个为高级算法（需要知识库支持）。所有算法都明确了输入、处理步骤和输出，为后续的实现提供了详细的指导。

**关键要点**：
1. 基础算法占77%，可以立即实施
2. 高级算法占23%，需要在知识库构建完成后实施
3. 算法设计考虑了性能、可扩展性和可维护性
4. 算法之间可以组合使用，形成完整的分析能力

---

**文档版本**：v1.0
**创建时间**：2024-01-XX
**最后更新**：2024-01-XX
**文档状态**：已完成
