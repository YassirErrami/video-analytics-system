import redis
import time

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Test connection
try:
    r.ping()
    print("✅ Connected to Redis successfully!")

    # Test basic operations
    r.set('test_key', 'Hello from PyCharm!')
    value = r.get('test_key')
    print(f"✅ Stored and retrieved: {value}")

    # Test list operations (we'll use this for queues)
    r.lpush('test_queue', 'item1', 'item2', 'item3')
    item = r.rpop('test_queue')
    print(f"✅ Queue operations work: {item}")

    # Cleanup
    r.delete('test_key', 'test_queue')
    print("✅ Redis is ready for Phase 2!")

except redis.ConnectionError:
    print("❌ Could not connect to Redis. Make sure Docker is running!")
except Exception as e:
    print(f"❌ Error: {e}")