# 网络性能监控系统

一个基于 Flask 和 Docker 的网络性能监控系统，用于实时监控多个主机的网络延迟、丢包率、HTTP 响应时间以及系统资源使用情况。

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [API 文档](#api-文档)
- [告警规则](#告警规则)
- [常见问题](#常见问题)

## ✨ 功能特性

### 网络监控
- **延迟监控**：实时监控多个主机的网络延迟（ping 延迟）
- **丢包率监控**：检测网络丢包情况
- **HTTP 响应时间**：监控指定 URL 的 HTTP 响应时间
- **多主机支持**：同时监控多个目标主机（默认：8.8.8.8、1.1.1.1、baidu.com、chat.deepseek.com）

### 系统监控
- **内存使用率**：实时显示系统内存占用情况
- **磁盘使用率**：监控磁盘空间使用情况
- **网络流量**：统计网络发送和接收流量

### 数据可视化
- **实时图表**：使用 Chart.js 展示历史趋势
- **告警状态**：根据阈值自动标记告警级别（正常/警告/严重）
- **日志查看**：支持按时间范围和告警级别筛选日志
- **数据导出**：支持导出 JSON 格式的监控日志

### 定时采集
- **自动采集**：使用 APScheduler 定时采集网络指标（默认每分钟一次）
- **并发采集**：使用线程池并发采集多个主机的数据
- **数据持久化**：所有监控数据存储在 MySQL 数据库中

## 🛠 技术栈

### 后端
- **Flask 3.0.0**：Web 框架
- **SQLAlchemy 2.0.25**：ORM 数据库操作
- **APScheduler 3.11.0**：定时任务调度
- **psutil**：系统资源监控
- **requests 2.31.0**：HTTP 请求
- **pymysql**：MySQL 数据库驱动

### 数据库
- **MySQL 8.0**：数据存储

### 前端
- **Bootstrap**：UI 框架
- **Chart.js**：图表可视化
- **jQuery**：DOM 操作和 AJAX

### 部署
- **Docker**：容器化部署
- **Docker Compose**：多容器编排

## 📁 项目结构

```
network-monitor/
├── backend/                 # 后端代码
│   ├── app.py              # Flask 主应用（Web 服务和 API）
│   ├── collector.py        # 数据采集模块（ping、HTTP 测试）
│   ├── scheduler.py        # 定时任务调度器
│   ├── models.py           # 数据库模型定义
│   ├── db.py               # 数据库连接配置
│   ├── config.py           # 配置文件（监控主机、采集间隔等）
│   ├── system_metrics.py   # 系统指标获取
│   └── init_db.py          # 数据库初始化（如需要）
├── frontend/               # 前端模板
│   └── templates/
│       ├── base.html       # 基础模板
│       ├── index.html      # 首页（系统资源监控）
│       ├── network.html    # 网络监控页面
│       ├── logs.html       # 日志查看页面
│       └── home_detail.html # 系统资源详情页
├── database/               # 数据库文件目录（SQLite 备用）
│   └── netmon.db
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile.web          # Web 服务镜像构建文件
├── Dockerfile.scheduler    # 调度器镜像构建文件
├── wait-for-mysql.sh       # MySQL 等待脚本
├── requirements.txt        # Python 依赖包
└── README.md              # 项目说明文档
```

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- 或 Python 3.10+（本地开发）

### 使用 Docker Compose 部署（推荐）

1. **克隆或下载项目**

```bash
cd network-monitor
```

2. **启动服务**

```bash
docker-compose up -d
```
或者
```bash
docker compose up -d
```
这将启动以下服务：
- `mysql`：MySQL 8.0 数据库
- `scheduler`：定时采集服务
- `web`：Web 服务和 API

3. **访问 Web 界面**

打开浏览器访问：`http://localhost:5000`

4. **查看日志**

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f scheduler
docker-compose logs -f web
```

5. **停止服务**

```bash
docker-compose down
```

### 本地开发部署

1. **安装依赖**

```bash
pip install -r requirements.txt
```

2. **配置 MySQL 数据库**

确保 MySQL 服务运行，并创建数据库：

```sql
CREATE DATABASE netmon;
CREATE USER 'netmon_user'@'localhost' IDENTIFIED BY 'netmon_pass';
GRANT ALL PRIVILEGES ON netmon.* TO 'netmon_user'@'localhost';
FLUSH PRIVILEGES;
```

3. **配置环境变量**

在 `backend/config.py` 中修改数据库连接信息，或设置环境变量：

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=netmon_user
export DB_PASSWORD=netmon_pass
export DB_NAME=netmon
```

4. **启动调度器**

```bash
python backend/scheduler.py
```

5. **启动 Web 服务**

```bash
python backend/app.py
```

6. **访问应用**

打开浏览器访问：`http://localhost:5000`

## ⚙️ 配置说明

### 监控主机配置

编辑 `backend/config.py` 文件，修改 `MONITOR_HOSTS` 列表：

```python
MONITOR_HOSTS = [
    "8.8.8.8",           # Google DNS
    "1.1.1.1",           # Cloudflare DNS
    "baidu.com",         # 百度
    "chat.deepseek.com", # DeepSeek
    # 添加更多主机...
]
```

### 采集间隔配置

在 `backend/config.py` 中修改 `INTERVAL_MINUTES`：

```python
INTERVAL_MINUTES = 1  # 每 1 分钟采集一次
```

### HTTP 测试 URL

修改 `TEST_URL` 以测试不同的 HTTP 服务：

```python
TEST_URL = "https://www.baidu.com"
```

### 数据库配置

通过环境变量配置数据库连接（Docker 部署）：

```yaml
environment:
  DB_HOST: mysql
  DB_PORT: 3306
  DB_NAME: netmon
  DB_USER: netmon_user
  DB_PASSWORD: netmon_pass
```

### 系统资源监控配置

对于 Linux 系统，Web 服务需要挂载宿主机目录以获取系统信息：

```yaml
volumes:
  - /:/host_root:ro       # 挂载宿主机根目录，用于磁盘信息
  - /proc:/host_proc:ro   # 挂载宿主机 /proc，用于网络流量
```

对于 Windows 系统，可以通过环境变量指定 JSON 文件路径：

```bash
HOST_METRICS_FILE=/app/host_metrics.json
```

## 📖 使用指南

### Web 界面功能

#### 1. 首页（系统资源监控）

- **内存使用率**：显示当前内存占用百分比和详细信息
- **磁盘使用率**：显示磁盘空间使用情况
- **网络流量**：显示总流量、发送流量、接收流量

点击各个卡片可查看详细的历史趋势图。

#### 2. 网络监控页面

访问 `/network/<metric>` 查看网络指标：
- `/network/latency`：延迟监控
- `/network/packetloss`：丢包率监控
- `/network/http`：HTTP 响应时间监控

每个页面显示所有监控主机的实时图表和历史趋势。

#### 3. 日志查看页面

访问 `/logs` 查看监控日志：

- **时间范围筛选**：1小时、24小时、7天、30天
- **告警级别筛选**：全部、警告、严重
- **分页浏览**：每页 15 条记录
- **数据导出**：点击"导出日志"按钮下载 JSON 文件

### 告警级别说明

系统根据以下规则自动标记告警级别：

- **正常（normal）**：
  - 延迟 ≤ 300ms 且丢包率 ≤ 5%

- **警告（warning）**：
  - 延迟 > 300ms 且 ≤ 600ms
  - 或丢包率 > 5% 且 ≤ 20%

- **严重（critical）**：
  - 延迟 > 600ms
  - 或丢包率 > 20%

## 🔌 API 文档

### 获取网络指标数据

**GET** `/api/network_metrics`

返回所有监控主机的最近 200 条记录。

**响应示例：**

```json
{
  "8.8.8.8": {
    "latency_ms": [10.5, 11.2, 10.8, ...],
    "packet_loss_percent": [0, 0, 0, ...],
    "http": [150.2, 148.5, 152.1, ...],
    "created_at": ["2024-01-01 12:00:00", ...],
    "alert_level": ["normal", "normal", ...]
  },
  "baidu.com": { ... }
}
```

### 获取系统资源指标

**GET** `/api/home_metrics`

返回当前系统的资源使用情况。

**响应示例：**

```json
{
  "memory_percent": 45.2,
  "disk_percent": 62.5,
  "total_traffic_mb": 1024.5,
  "memory_used": 8192.0,
  "memory_total": 16384.0,
  "disk_used": 500.0,
  "disk_total": 800.0,
  "net_sent_mb": 512.3,
  "net_recv_mb": 512.2
}
```

### 下载日志

**GET** `/logs/download?range=30d&alert=all`

下载指定时间范围和告警级别的日志 JSON 文件。

**查询参数：**
- `range`：时间范围（1h / 24h / 7d / 30d）
- `alert`：告警级别（all / warning / critical）

## 🚨 告警规则

系统在以下情况会触发告警：

| 指标 | 正常 | 警告 | 严重 |
|------|------|------|------|
| 延迟 | ≤ 300ms | 300ms - 600ms | > 600ms |
| 丢包率 | ≤ 5% | 5% - 20% | > 20% |

告警信息会在日志页面中显示，并可通过筛选功能查看。

## ❓ 常见问题

### 1. Docker 容器无法连接到 MySQL

**问题**：scheduler 或 web 服务启动失败，提示数据库连接错误。

**解决方案**：
- 确保 MySQL 容器已启动并健康：`docker-compose ps`
- 检查环境变量配置是否正确
- 查看 MySQL 日志：`docker-compose logs mysql`

### 2. ping 命令在容器中无法使用

**问题**：scheduler 容器中 ping 命令失败。

**解决方案**：
- 确保 Dockerfile.scheduler 中已安装 `iputils-ping`
- 重新构建镜像：`docker-compose build scheduler`

### 3. 系统资源监控显示错误

**问题**：首页显示的系统资源数据不正确。

**解决方案**：
- Linux：确保已正确挂载 `/` 和 `/proc` 目录
- Windows：确保 `HOST_METRICS_FILE` 环境变量指向正确的 JSON 文件

### 4. 数据采集不工作

**问题**：日志页面没有新数据。

**解决方案**：
- 检查 scheduler 容器是否运行：`docker-compose ps`
- 查看 scheduler 日志：`docker-compose logs scheduler`
- 确认数据库连接正常
- 检查 `MONITOR_HOSTS` 配置是否正确

### 5. 端口被占用

**问题**：无法启动 Web 服务，提示端口 5000 被占用。

**解决方案**：
- 修改 `docker-compose.yml` 中的端口映射：`"8080:5000"`
- 或停止占用端口的其他服务

### 6. 时区问题

**问题**：日志时间显示不正确。

**解决方案**：
- 系统默认使用 UTC 时间，显示时会转换为 UTC+8（北京时间）
- 如需修改，可在代码中调整 `LOCAL_OFFSET`

## 📝 开发说明

### 添加新的监控指标

1. 在 `models.py` 中添加新的字段
2. 在 `collector.py` 中实现采集逻辑
3. 在 `app.py` 中添加 API 端点
4. 在前端模板中添加可视化

### 修改告警阈值

编辑 `app.py` 中的告警判定函数：

```python
def get_alert(log):
    if (log.latency_ms and log.latency_ms > 600) or ...
        return "critical"
    elif (log.latency_ms and log.latency_ms > 300) or ...
        return "warning"
    else:
        return "normal"
```

### 数据库迁移

如果需要修改数据库结构：

1. 修改 `models.py` 中的模型定义
2. 删除旧数据库或使用迁移工具
3. 重新启动服务，表结构会自动创建

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**：本系统仅用于监控和测试目的，请勿用于生产环境的敏感数据监控。


