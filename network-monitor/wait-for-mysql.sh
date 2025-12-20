#!/bin/sh
set -e

host="$1"
shift
cmd="$@"

echo "[wait-for-mysql] host=$host"
echo "[wait-for-mysql] command=$cmd"
echo "[wait-for-mysql] 等待 MySQL 3306 端口开放..."

# 等端口，而不是 mysql 命令（避免 SSL 坑）
until nc -z "$host" 3306; do
  echo "[wait-for-mysql] MySQL 端口未就绪，2 秒后重试..."
  sleep 2
done

echo "[wait-for-mysql] MySQL 端口已开放，启动 Python"
exec $cmd
