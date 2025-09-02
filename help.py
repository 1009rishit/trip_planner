import redis

r = redis.Redis(host="localhost", port=6379, db=0)

# delete all cache keys with prefix
for key in r.scan_iter("cache:*"):
    r.delete(key)

# OR flush entire DB
print("deleted")
r.flushdb()