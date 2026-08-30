"""
production_rag.core.log_generator - Realtime Production Log Stream Simulator
"""

import os
import time
import random
import threading
from datetime import datetime
from production_rag.config.settings import settings

LOG_TEMPLATES = [
    {
        "subfolder": "auth_service",
        "file": "auth_errors.log",
        "templates": [
            "{timestamp} ERROR [AuthThread-{thread}] auth_service.jwt.verifier - JWT Signature verification failed: Token expired at {timestamp}.\n"
            "  Payload: {{\"user_id\": \"usr_{rand_id}\", \"ip\": \"192.168.1.{ip_suffix}\", \"user_agent\": \"Mozilla/5.0 (X11; Linux x86_64)\"}}\n"
            "  Stack trace:\n"
            "    at com.auth.jwt.JWTVerifier.verifyToken(JWTVerifier.java:142)\n"
            "    at com.auth.service.AuthHandler.handleRequest(AuthHandler.java:88)\n",
            
            "{timestamp} WARNING [AuthThread-{thread}] auth_service.security - Rate limit window 95% full for IP 10.0.4.{ip_suffix}.\n"
        ]
    },
    {
        "subfolder": "payment_gateway",
        "file": "payment_failures.log",
        "templates": [
            "{timestamp} CRITICAL [PaymentWorker-{thread}] payment_gateway.processor - Payment transaction tx_{rand_id} failed with HTTP 502 Bad Gateway.\n"
            "  Request Context: {{\"amount\": {rand_amount}, \"currency\": \"USD\", \"gateway\": \"Stripe-v2\", \"attempt\": 3}}\n"
            "  Exception: org.apache.http.conn.HttpHostConnectException: Connect to 10.244.2.45:8080 failed: Connection refused\n"
            "    at org.apache.http.impl.conn.DefaultHttpClientConnectionOperator.connect(DefaultHttpClientConnectionOperator.java:159)\n"
            "    at org.apache.http.impl.conn.PoolingHttpClientConnectionManager.connect(PoolingHttpClientConnectionManager.java:376)\n",
            
            "{timestamp} ERROR [KafkaConsumer-{thread}] payment_gateway.kafka - Kafka Consumer Lag Critical: Topic 'payment-events' partition {partition} lag is {lag_count}.\n"
        ]
    },
    {
        "subfolder": "database",
        "file": "postgres_and_redis.log",
        "templates": [
            "{timestamp} WARNING [QueryMonitor-{thread}] postgres.slow_query - Long running transaction detected: PID {pid} running for {duration}s.\n"
            "  Query: SELECT * FROM orders WHERE status = 'PENDING' AND created_at < NOW() - INTERVAL '1 day' ORDER BY created_at DESC;\n"
            "  Execution State: active | Wait Event: IO:DataFileRead | Locks Held: ExclusiveLock on relation 'orders'\n"
            "  Context: Unindexed sequential scan (seq_scan) on table 'orders' (12,450,000 rows scanned).\n",
            
            "{timestamp} ERROR [DBPool-{thread}] postgres.connection.pool - Connection acquire timeout after 5000ms. Active: 100/100, Idle: 0, Waiting: 42.\n"
            "  SQL State: 53300 (too_many_connections) - User 'app_user' has reached maximum allowed connections.\n",
            
            "{timestamp} CRITICAL [RedisEvent-{thread}] redis.cluster.memory - Redis OOM threshold reached. Used: 2048MB / Max: 2048MB.\n"
            "  Command 'SET' rejected for key 'cache:session:{rand_id}'. Policy 'noeviction' prevented key removal.\n"
        ]
    }
]

class RealtimeLogGenerator:
    """Generates continuous production log streams in the background."""
    
    def __init__(self, log_dir: str = settings.LOG_DIR):
        self.log_dir = log_dir
        self.running = False
        self._thread = None
        
    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            print("[LogGenerator] Realtime production log generator started in background.")
            
    def stop(self):
        self.running = False
        
    def _run(self):
        while self.running:
            try:
                item = random.choice(LOG_TEMPLATES)
                subfolder = os.path.join(self.log_dir, item["subfolder"])
                os.makedirs(subfolder, exist_ok=True)
                file_path = os.path.join(subfolder, item["file"])
                
                template = random.choice(item["templates"])
                now_str = datetime.utcnow().isoformat() + "Z"
                
                log_entry = template.format(
                    timestamp=now_str,
                    thread=random.randint(10, 99),
                    pid=random.randint(18000, 99000),
                    duration=random.randint(320, 850),
                    rand_id=random.randint(10000, 99999),
                    ip_suffix=random.randint(1, 254),
                    rand_amount=random.randint(10, 500),
                    partition=random.randint(0, 3),
                    lag_count=random.randint(40000, 80000)
                )
                
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(log_entry + "\n")
                    
            except Exception as e:
                print(f"[LogGenerator Error] {e}")
                
            time.sleep(3)  # Append a new multi-line log entry every 3 seconds

log_generator = RealtimeLogGenerator()
