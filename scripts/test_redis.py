import redis
import sys

try:
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    ping = r.ping()
    print(f"Redis Connection Success: {ping}")
except Exception as e:
    print(f"Redis Connection Failed: {e}")
    sys.exit(1)
