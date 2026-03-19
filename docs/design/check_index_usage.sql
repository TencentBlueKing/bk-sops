-- ============================================================
-- SQL索引使用情况检查脚本
-- 用于快速检查查询是否命中索引
-- ============================================================

-- ============================================================
-- 方法1：使用 EXPLAIN 检查（推荐）
-- ============================================================

-- 检查当前查询的索引使用情况
EXPLAIN SELECT COUNT(*)
FROM `taskflow3_taskflowinstance` AS t
INNER JOIN `pipeline_pipelineinstance` AS p
    ON t.`pipeline_instance_id` = p.`id`
WHERE (
    t.`is_deleted` = 0
    AND p.`is_expired` = 0
    AND t.`pipeline_instance_id` IS NOT NULL
    AND t.`project_id` = 1
    AND t.`is_child_taskflow` = 0
    AND p.`create_time` >= '2025-07-09 11:30:51.881148'
);

-- ============================================================
-- 方法2：使用 EXPLAIN FORMAT=JSON（详细版）
-- ============================================================

EXPLAIN FORMAT=JSON SELECT COUNT(*)
FROM `taskflow3_taskflowinstance` AS t
INNER JOIN `pipeline_pipelineinstance` AS p
    ON t.`pipeline_instance_id` = p.`id`
WHERE (
    t.`is_deleted` = 0
    AND p.`is_expired` = 0
    AND t.`pipeline_instance_id` IS NOT NULL
    AND t.`project_id` = 1
    AND t.`is_child_taskflow` = 0
    AND p.`create_time` >= '2025-07-09 11:30:51.881148'
)\G

-- ============================================================
-- 方法3：使用 EXPLAIN ANALYZE（MySQL 8.0+）
-- ============================================================

EXPLAIN ANALYZE SELECT COUNT(*)
FROM `taskflow3_taskflowinstance` AS t
INNER JOIN `pipeline_pipelineinstance` AS p
    ON t.`pipeline_instance_id` = p.`id`
WHERE (
    t.`is_deleted` = 0
    AND p.`is_expired` = 0
    AND t.`pipeline_instance_id` IS NOT NULL
    AND t.`project_id` = 1
    AND t.`is_child_taskflow` = 0
    AND p.`create_time` >= '2025-07-09 11:30:51.881148'
);

-- ============================================================
-- 方法4：检查索引使用统计
-- ============================================================

-- 查看表的索引使用情况
SELECT
    TABLE_NAME,
    INDEX_NAME,
    SEQ_IN_INDEX,
    COLUMN_NAME,
    CARDINALITY,
    INDEX_TYPE
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN ('taskflow3_taskflowinstance', 'pipeline_pipelineinstance')
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- ============================================================
-- 方法5：使用性能分析
-- ============================================================

-- 开启性能分析
SET profiling = 1;

-- 执行查询
SELECT COUNT(*)
FROM `taskflow3_taskflowinstance` AS t
INNER JOIN `pipeline_pipelineinstance` AS p
    ON t.`pipeline_instance_id` = p.`id`
WHERE (
    t.`is_deleted` = 0
    AND p.`is_expired` = 0
    AND t.`pipeline_instance_id` IS NOT NULL
    AND t.`project_id` = 1
    AND t.`is_child_taskflow` = 0
    AND p.`create_time` >= '2025-07-09 11:30:51.881148'
);

-- 查看性能分析
SHOW PROFILES;

-- 查看详细的执行步骤（替换 QUERY_ID 为实际的查询ID）
-- SHOW PROFILE FOR QUERY 1;

-- 查看CPU和IO使用情况
-- SHOW PROFILE CPU, BLOCK IO FOR QUERY 1;

-- ============================================================
-- 方法6：检查表统计信息
-- ============================================================

-- 查看表的行数和索引信息
SELECT
    TABLE_NAME,
    TABLE_ROWS,
    DATA_LENGTH,
    INDEX_LENGTH,
    ROUND(INDEX_LENGTH / DATA_LENGTH * 100, 2) AS INDEX_RATIO
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN ('taskflow3_taskflowinstance', 'pipeline_pipelineinstance');

-- ============================================================
-- 方法7：检查索引选择性
-- ============================================================

-- 检查索引的选择性（选择性越高，索引效果越好）
SELECT
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    CARDINALITY,
    TABLE_ROWS,
    ROUND(CARDINALITY / TABLE_ROWS * 100, 2) AS SELECTIVITY_PERCENT
FROM INFORMATION_SCHEMA.STATISTICS s
JOIN INFORMATION_SCHEMA.TABLES t
    ON s.TABLE_SCHEMA = t.TABLE_SCHEMA
    AND s.TABLE_NAME = t.TABLE_NAME
WHERE s.TABLE_SCHEMA = DATABASE()
    AND s.TABLE_NAME IN ('taskflow3_taskflowinstance', 'pipeline_pipelineinstance')
    AND s.SEQ_IN_INDEX = 1  -- 只看索引的第一列
ORDER BY SELECTIVITY_PERCENT DESC;

-- ============================================================
-- 方法8：对比优化前后的执行计划
-- ============================================================

-- 原始查询（带 ORDER BY）
EXPLAIN SELECT COUNT('*')
FROM `taskflow3_taskflowinstance`
INNER JOIN `pipeline_pipelineinstance`
    ON (`taskflow3_taskflowinstance`.`pipeline_instance_id` = `pipeline_pipelineinstance`.`id`)
WHERE (
    `taskflow3_taskflowinstance`.`is_deleted` = 0
    AND NOT `pipeline_pipelineinstance`.`is_expired`
    AND `taskflow3_taskflowinstance`.`pipeline_instance_id` IS NOT NULL
    AND `taskflow3_taskflowinstance`.`project_id` = 1
    AND NOT `taskflow3_taskflowinstance`.`is_child_taskflow`
    AND `pipeline_pipelineinstance`.`create_time` >= '2025-07-09 11:30:51.881148'
)
ORDER BY `taskflow3_taskflowinstance`.`id` DESC;

-- 优化后的查询
EXPLAIN SELECT COUNT(*)
FROM `taskflow3_taskflowinstance` AS t
INNER JOIN `pipeline_pipelineinstance` AS p
    ON t.`pipeline_instance_id` = p.`id`
WHERE (
    t.`is_deleted` = 0
    AND p.`is_expired` = 0
    AND t.`pipeline_instance_id` IS NOT NULL
    AND t.`project_id` = 1
    AND t.`is_child_taskflow` = 0
    AND p.`create_time` >= '2025-07-09 11:30:51.881148'
);

-- ============================================================
-- 快速判断索引是否命中的查询
-- ============================================================

-- 检查 EXPLAIN 结果中是否有未使用索引的表
SELECT
    table_name,
    type,
    CASE
        WHEN type = 'ALL' THEN '❌ 全表扫描 - 未使用索引'
        WHEN type = 'index' THEN '⚠️ 全索引扫描 - 索引使用不充分'
        WHEN type IN ('ref', 'range', 'eq_ref', 'const') THEN '✅ 使用索引'
        ELSE '⚠️ 其他类型'
    END AS index_status,
    key_name,
    rows
FROM (
    SELECT
        'taskflow3_taskflowinstance' AS table_name,
        'ref' AS type,  -- 替换为实际 EXPLAIN 的 type
        'idx_taskflow_project_deleted_child' AS key_name,  -- 替换为实际 EXPLAIN 的 key
        1000 AS rows  -- 替换为实际 EXPLAIN 的 rows
    UNION ALL
    SELECT
        'pipeline_pipelineinstance' AS table_name,
        'ref' AS type,
        'idx_pipeline_create_time_expired' AS key_name,
        1 AS rows
) AS explain_result;

-- ============================================================
-- 检查未使用索引的查询（慢查询日志）
-- ============================================================

-- 查看最近未使用索引的查询
SELECT
    sql_text,
    exec_count,
    sum_timer_wait/1000000000000 AS total_time_sec,
    avg_timer_wait/1000000000000 AS avg_time_sec,
    sum_rows_examined,
    sum_rows_sent,
    no_index_used,
    no_good_index_used
FROM performance_schema.events_statements_summary_by_digest
WHERE sql_text LIKE '%taskflow3_taskflowinstance%'
    AND (no_index_used > 0 OR no_good_index_used > 0)
ORDER BY sum_timer_wait DESC
LIMIT 10;

-- ============================================================
-- 索引使用情况总结查询
-- ============================================================

-- 生成索引使用情况报告
SELECT
    CONCAT('表: ', TABLE_NAME) AS info,
    CONCAT('索引: ', INDEX_NAME) AS index_info,
    CONCAT('列: ', GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX)) AS columns,
    CONCAT('基数: ', CARDINALITY) AS cardinality
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN ('taskflow3_taskflowinstance', 'pipeline_pipelineinstance')
GROUP BY TABLE_NAME, INDEX_NAME, CARDINALITY
ORDER BY TABLE_NAME, INDEX_NAME;








