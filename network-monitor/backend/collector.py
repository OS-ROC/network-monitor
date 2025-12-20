import subprocess
import time
from datetime import datetime
import requests
import re
from db import SessionLocal
from models import NetworkMetric
from config import TEST_URL, MONITOR_HOSTS
from concurrent.futures import ThreadPoolExecutor, as_completed

def ping_host(host):
    try:
        # Linux: ping -c 4; Windows: ping -n 4
        import platform
        count_flag = "-n" if platform.system().lower() == "windows" else "-c"
        cmd = ["ping", count_flag, "4", host]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        latency, loss = None, None
        for line in result.stdout.splitlines():
            if "packet loss" in line or "丢失" in line:
                match = re.search(r"(\d+)%", line)
                if match:
                    loss = int(match.group(1))
            if "rtt min/avg/max" in line or "平均 = " in line:
                match = re.search(r"= [\d\.]+/([\d\.]+)/" , line) or re.search(r"平均 = (\d+)ms", line)
                if match:
                    latency = float(match.group(1))
        return {"host": host, "latency_ms": latency, "packet_loss_percent": loss}
    except subprocess.TimeoutExpired:
        return {"host": host, "latency_ms": None, "packet_loss_percent": 100}
    except Exception as e:
        print("[ERROR] ping {} failed: {}".format(host, e))
        return {"host": host, "latency_ms": None, "packet_loss_percent": 100}

def http_response_time(url=TEST_URL):
    start = time.time()
    try:
        requests.get(url, timeout=5)
        return round((time.time() - start) * 1000, 2)
    except requests.RequestException:
        return None

def save_metric(host, latency, loss, http_ms):
    db = SessionLocal()
    try:
        metric = NetworkMetric(
            host=host,
            latency_ms=latency,
            packet_loss_percent=loss,
            http_response_ms=http_ms,
            created_at=datetime.utcnow()
        )
        db.add(metric)
        db.commit()
    finally:
        db.close()

def collect_single_host(host):
    ping_result = ping_host(host)
    http_ms = http_response_time(TEST_URL)
    print("[DEBUG] host={}, ping_result={}, http_ms={}".format(host, ping_result, http_ms), flush=True)
    save_metric(
        host=ping_result["host"],
        latency=ping_result["latency_ms"],
        loss=ping_result["packet_loss_percent"],
        http_ms=http_ms
    )

def collect_job():
    print("[{}] 开始采集任务".format(datetime.now()), flush=True)
    with ThreadPoolExecutor(max_workers=len(MONITOR_HOSTS)) as executor:
        futures = [executor.submit(collect_single_host, host) for host in MONITOR_HOSTS]
        for _ in as_completed(futures):
            pass
    print("[{}] ✅ 数据已写入数据库".format(datetime.now()), flush=True)
