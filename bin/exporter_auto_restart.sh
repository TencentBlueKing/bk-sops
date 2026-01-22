#!/bin/bash
set -e

# 从环境变量读取重启间隔（秒），默认 7 天
RESTART_INTERVAL=${EXPORTER_RESTART_INTERVAL:-604800}

# 随机偏移百分比，默认 10%（表示 ±10% 的随机偏移）
RESTART_RANDOM_PERCENT=${EXPORTER_RESTART_RANDOM_PERCENT:-10}

# 获取 exporter 命令参数
EXPORTER_ARGS="$@"

echo "[$(date)] Celery Prometheus Exporter auto-restart wrapper started"
echo "[$(date)] Base restart interval: ${RESTART_INTERVAL} seconds"
echo "[$(date)] Random offset: ±${RESTART_RANDOM_PERCENT}%"
echo "[$(date)] Exporter args: ${EXPORTER_ARGS}"
echo "[$(date)] First startup: immediate (no initial delay)"

while true; do
    # 计算本次重启的随机间隔
    # 随机偏移范围：-RESTART_RANDOM_PERCENT% 到 +RESTART_RANDOM_PERCENT%
    RANDOM_OFFSET_RANGE=$((RESTART_INTERVAL * RESTART_RANDOM_PERCENT / 100))
    # 生成 -RANDOM_OFFSET_RANGE 到 +RANDOM_OFFSET_RANGE 的随机数
    RANDOM_OFFSET=$((RANDOM % (2 * RANDOM_OFFSET_RANGE + 1) - RANDOM_OFFSET_RANGE))
    ACTUAL_INTERVAL=$((RESTART_INTERVAL + RANDOM_OFFSET))

    # 确保间隔不小于 1 小时
    if [ $ACTUAL_INTERVAL -lt 3600 ]; then
        ACTUAL_INTERVAL=3600
    fi

    echo "[$(date)] Starting celery-prometheus-exporter..."
    echo "[$(date)] This cycle restart interval: ${ACTUAL_INTERVAL} seconds (base: ${RESTART_INTERVAL}, offset: ${RANDOM_OFFSET})"

    # 使用 timeout 命令限制运行时间
    # --foreground: 前台运行，确保信号传递
    # --kill-after=600: 如果 TERM 信号无效，600秒后强制 KILL
    # 临时禁用 set -e，以便捕获真实的退出码
    set +e
    timeout --foreground --kill-after=600 ${ACTUAL_INTERVAL}s \
        celery-prometheus-exporter ${EXPORTER_ARGS}
    EXIT_CODE=$?
    set -e

    if [ $EXIT_CODE -eq 124 ]; then
        # 124 是 timeout 的正常退出码
        echo "[$(date)] Exporter reached restart interval, restarting..."
    elif [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Exporter exited normally, restarting..."
    else
        echo "[$(date)] Exporter exited with error code $EXIT_CODE, waiting 10s before restart..."
        sleep 10
    fi

    # 短暂延迟，避免频繁重启
    sleep 2
done

