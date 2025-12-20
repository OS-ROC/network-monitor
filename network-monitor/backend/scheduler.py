from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from collector import collect_job
from config import INTERVAL_MINUTES
from datetime import datetime
from db import engine
from models import Base
from sqlalchemy import text
import time

# 1️⃣ 确保表存在
Base.metadata.create_all(bind=engine)
print("[{}] 数据库表已确认存在".format(datetime.now()))

# 2️⃣ 等待数据库真正可用
for i in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[{}] 数据库连接成功".format(datetime.now()))
        break
    except Exception:
        print("等待数据库...")
        time.sleep(2)
else:
    raise RuntimeError("数据库不可用")

# 3️⃣ 使用 BlockingScheduler（关键）
if __name__ == "__main__":
    executors = {"default": ThreadPoolExecutor(5)}
    scheduler = BlockingScheduler(executors=executors)

    # 每 INTERVAL_MINUTES 分钟执行一次，容忍 misfire 10 秒
    scheduler.add_job(
        collect_job,
        trigger="interval",
        minutes=INTERVAL_MINUTES,
        next_run_time=datetime.now(),
        misfire_grace_time=10,
        coalesce=True  # 错过多次执行，只执行一次
    )

    print("[{}] 🚀 Scheduler 已启动".format(datetime.now()))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[{}] Scheduler 停止".format(datetime.now()))
