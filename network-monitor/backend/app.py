from flask import Flask, render_template, jsonify, request, send_file
from db import SessionLocal
from models import NetworkMetric
from config import MONITOR_HOSTS
import psutil
from datetime import datetime, timedelta
import json
from io import BytesIO
import os
import platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../frontend/templates")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

IS_WINDOWS = platform.system() == "Windows"
HOST_METRICS_FILE = os.getenv("HOST_METRICS_FILE", "/app/host_metrics.json")  # Windows JSON 文件路径

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/network/<metric>")
def network_page(metric):
    if metric not in ["latency", "packetloss", "http"]:
        metric = "latency"
    return render_template("network.html", metric=metric, hosts=MONITOR_HOSTS)


@app.route("/logs")
def system_logs():
    db = SessionLocal()
    range_type = request.args.get("range", "30d")
    page = int(request.args.get("page", 1))
    per_page = 15
    filter_alert = request.args.get("alert", "all")  # all / warning / critical

    now = datetime.utcnow()
    if range_type == "1h":
        start_time = now - timedelta(hours=1)
    elif range_type == "24h":
        start_time = now - timedelta(days=1)
    elif range_type == "7d":
        start_time = now - timedelta(days=7)
    else:
        start_time = now - timedelta(days=30)

    # 先按 id 降序查询指定时间内所有日志
    logs_query = db.query(NetworkMetric).filter(NetworkMetric.created_at >= start_time)\
                                        .order_by(NetworkMetric.id.desc())
    all_logs = logs_query.all()

    # 告警判定函数
    def get_alert(log):
        if (log.latency_ms and log.latency_ms > 600) or (log.packet_loss_percent and log.packet_loss_percent > 20):
            return "critical"
        elif (log.latency_ms and log.latency_ms > 300) or (log.packet_loss_percent and log.packet_loss_percent > 5):
            return "warning"
        else:
            return "normal"

    # 先标记告警，不改变顺序
    for log in all_logs:
        log.alert_info = get_alert(log)

    # 根据告警类型过滤，同时保持顺序不乱
    if filter_alert != "all":
        all_logs = [log for log in all_logs if log.alert_info == filter_alert]

    # 分页
    total_logs = len(all_logs)
    total_pages = (total_logs + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    logs_page = all_logs[start_idx:start_idx + per_page]

    # 转换为本地时间
    LOCAL_OFFSET = timedelta(hours=8)
    for log in logs_page:
        log.created_at = log.created_at + LOCAL_OFFSET

    db.close()

    return render_template(
        "logs.html",
        logs=logs_page,
        current_range=range_type,
        current_page=page,
        total_pages=total_pages,
        filter_alert=filter_alert
    )



@app.route("/logs/download")
def download_logs():
    db = SessionLocal()
    range_type = request.args.get("range", "30d")
    filter_alert = request.args.get("alert", "all")

    now = datetime.utcnow()
    if range_type == "1h":
        start_time = now - timedelta(hours=1)
    elif range_type == "24h":
        start_time = now - timedelta(days=1)
    elif range_type == "7d":
        start_time = now - timedelta(days=7)
    else:
        start_time = now - timedelta(days=30)

    # 先按 id 降序查询
    logs_query = db.query(NetworkMetric).filter(NetworkMetric.created_at >= start_time)\
                                        .order_by(NetworkMetric.id.desc())
    all_logs = logs_query.all()

    # 告警判定函数
    def get_alert(log):
        if (log.latency_ms and log.latency_ms > 600) or (log.packet_loss_percent and log.packet_loss_percent > 20):
            return "critical"
        elif (log.latency_ms and log.latency_ms > 300) or (log.packet_loss_percent and log.packet_loss_percent > 5):
            return "warning"
        else:
            return "normal"

    # 标记告警
    for log in all_logs:
        log.alert_info = get_alert(log)

    # 根据告警类型过滤，同时保持顺序
    if filter_alert != "all":
        all_logs = [log for log in all_logs if log.alert_info == filter_alert]

    # 转换为本地时间
    LOCAL_OFFSET = timedelta(hours=8)
    logs_data = []
    for log in all_logs:
        logs_data.append({
            "id": log.id,
            "host": log.host,
            "latency_ms": log.latency_ms,
            "packet_loss_percent": log.packet_loss_percent,
            "http_response_ms": log.http_response_ms,
            "alert_info": log.alert_info,
            "created_at": (log.created_at + LOCAL_OFFSET).strftime("%Y-%m-%d %H:%M:%S")
        })

    db.close()

    json_bytes = BytesIO()
    json_bytes.write(json.dumps(logs_data, ensure_ascii=False, indent=2).encode("utf-8"))
    json_bytes.seek(0)

    return send_file(
        json_bytes,
        mimetype="application/json",
        as_attachment=True,
        download_name=f"system_logs_{range_type}.json"
    )



@app.route("/api/network_metrics")
def api_network_metrics():
    db = SessionLocal()
    metrics = db.query(NetworkMetric)\
        .filter(NetworkMetric.host.in_(MONITOR_HOSTS))\
        .order_by(NetworkMetric.created_at.desc())\
        .limit(200)\
        .all()
    db.close()

    metrics.reverse()
    data_by_host = {}

    for m in metrics:
        h = m.host
        if h not in data_by_host:
            data_by_host[h] = {"latency_ms": [], "packet_loss_percent": [], "http": [], "created_at": [], "alert_level": []}

        alert = "normal"
        if (m.latency_ms and m.latency_ms > 600) or (m.packet_loss_percent and m.packet_loss_percent > 20):
            alert = "critical"
        elif (m.latency_ms and m.latency_ms > 300) or (m.packet_loss_percent and m.packet_loss_percent > 5):
            alert = "warning"

        data_by_host[h]["latency_ms"].append(m.latency_ms or 0)
        data_by_host[h]["packet_loss_percent"].append(m.packet_loss_percent or 0)
        data_by_host[h]["http"].append(m.http_response_ms or 0)
        data_by_host[h]["created_at"].append(m.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        data_by_host[h]["alert_level"].append(alert)

    for h in MONITOR_HOSTS:
        if h not in data_by_host:
            data_by_host[h] = {"latency_ms": [], "packet_loss_percent": [], "http": [], "created_at": [], "alert_level": []}

    return jsonify(data_by_host)


@app.route("/api/home_metrics")
def api_home_metrics():
    try:
        if IS_WINDOWS:
            # Windows 读取挂载的 JSON 文件
            if os.path.exists(HOST_METRICS_FILE):
                with open(HOST_METRICS_FILE, "r") as f:
                    data = json.load(f)
                return jsonify(data)
            else:
                return jsonify({"error": "宿主机 metrics 文件不存在"}), 404
        else:
            # Linux 宿主机
            memory = psutil.virtual_memory()
            disk_path = os.getenv("DISK_PATH", "/host_root")
            disk = psutil.disk_usage(disk_path)
            net_io = psutil.net_io_counters()
            total_traffic_mb = round((net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024, 2)
            return jsonify({
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "total_traffic_mb": total_traffic_mb,
                "memory_used": round(memory.used / 1024 / 1024, 2),
                "memory_total": round(memory.total / 1024 / 1024, 2),
                "disk_used": round(disk.used / 1024 / 1024 / 1024, 2),
                "disk_total": round(disk.total / 1024 / 1024 / 1024, 2),
                "net_sent_mb": round(net_io.bytes_sent / 1024 / 1024, 2),
                "net_recv_mb": round(net_io.bytes_recv / 1024 / 1024, 2)
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/home_detail/<metric>")
def home_detail(metric):
    if metric not in ["memory", "disk", "traffic"]:
        metric = "memory"
    return render_template("home_detail.html", metric=metric)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
