import os

DB_HOST = os.environ.get("DB_HOST", "mysql")
DB_USER = os.environ.get("DB_USER", "netmon_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "netmon_pass")
DB_NAME = os.environ.get("DB_NAME", "netmon")

MONITOR_HOSTS = [
    "8.8.8.8",
    "1.1.1.1",
    "baidu.com",
    "chat.deepseek.com"
]

TEST_URL = "https://www.baidu.com"
INTERVAL_MINUTES = 1
