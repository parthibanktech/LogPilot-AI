"""
generate_massive_logs.py - Populates log files with hundreds of realistic production entries.
"""

import os
import random
from datetime import datetime, timedelta

BASE_LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs"))

SERVICES = {
    "auth_service/auth_errors.log": [
        "2026-08-29T{time}Z INFO auth_service.jwt.verifier [Thread-{thread}]: JWT Token issued successfully for sub='user_{user_id}' scope='read:orders,write:orders'",
        "2026-08-29T{time}Z WARNING auth_service.ratelimit [Thread-{thread}]: Rate limit warning for client 192.168.1.{ip}: 85/100 requests per minute consumed",
        "2026-08-29T{time}Z ERROR auth_service.jwt.verifier [Thread-{thread}]: JWT Signature verification failed: Token expired at timestamp {timestamp}\n  Payload: {{\"user_id\": \"usr_{user_id}\", \"ip\": \"192.168.1.{ip}\", \"user_agent\": \"Mozilla/5.0 (X11; Linux x86_64)\"}}\n  Stack trace:\n    at com.auth.jwt.JWTVerifier.verifyToken(JWTVerifier.java:142)\n    at com.auth.service.AuthHandler.handleRequest(AuthHandler.java:88)",
        "2026-08-29T{time}Z ERROR gateway-proxy[450]: SSL handshake failed, certificate expired (CN=api.internal.net) for upstream 10.0.1.{ip}:443",
        "2026-08-29T{time}Z WARNING sshd[1050]: PAM 3 more authentication failures; logname= uid=0 euid=0 tty=ssh ruser= rhost=192.168.1.{ip} user=admin"
    ],
    "payment_gateway/payment_failures.log": [
        "2026-08-29T{time}Z INFO payment_gateway.processor [Worker-{thread}]: Payment intent created tx_{tx_id} amount=${amount}.00 currency=USD",
        "2026-08-29T{time}Z WARNING kafka-broker-1[912]: [ConsumerGroup order-processing-group]: Consumer lag threshold warning: partition {partition} lag is {lag} messages",
        "2026-08-29T{time}Z CRITICAL kafka-broker-1[912]: CommitFailedException: Offset commit failed with CommitFailedException due to rebalance in progress for topic 'payment-events'",
        "2026-08-29T{time}Z ERROR nginx-ingress[301]: 502 Bad Gateway: connect() failed (111: Connection refused) while connecting to upstream 'http://10.244.2.{ip}:8080/payment/charge'",
        "2026-08-29T{time}Z CRITICAL payment_gateway.processor [Worker-{thread}]: Payment processing failed for tx_{tx_id}.\n  Request Context: {{\"amount\": {amount}, \"currency\": \"USD\", \"gateway\": \"Stripe-v2\", \"attempt\": 3}}\n  Exception: org.apache.http.conn.HttpHostConnectException: Connect to 10.244.2.{ip}:8080 failed: Connection refused\n    at org.apache.http.impl.conn.DefaultHttpClientConnectionOperator.connect(DefaultHttpClientConnectionOperator.java:159)"
    ],
    "database/postgres_and_redis.log": [
        "2026-08-29T{time}Z INFO postgres-primary[1801]: execute <JDBC Query>: SELECT * FROM orders WHERE user_id = {user_id} AND status = 'active'",
        "2026-08-29T{time}Z WARNING db-pool[1801]: Active database connection count at {conn_pct}% of capacity ({conn_pct}/100)",
        "2026-08-29T{time}Z CRITICAL db-pool[1801]: connection limit exceeded (100/100) for user 'app_user'\n  SQL State: 53300 (too_many_connections) - User 'app_user' has reached maximum allowed connections",
        "2026-08-29T{time}Z ERROR postgres-primary[18402]: ERROR: deadlock detected. Process {thread} waits for ExclusiveLock on relation orders; blocked by process {other_thread}",
        "2026-08-29T{time}Z WARNING redis-cluster[6379]: Memory usage at 94% (1920MB/2048MB). Eviction policy: noeviction",
        "2026-08-29T{time}Z CRITICAL redis-cluster[6379]: RedisException: OOM command not allowed when used memory > 'maxmemory' (used memory: 2048MB)"
    ],
    "cloud_infra/aws_and_elasticsearch.log": [
        "2026-08-29T{time}Z INFO cloudwatch-agent[1102]: Metrics successfully flushed to AWS CloudWatch namespace 'Production/EC2'",
        "2026-08-29T{time}Z ERROR aws-s3-adapter[4012]: com.amazonaws.services.s3.model.AmazonS3Exception: Access Denied (Service: Amazon S3; Status Code: 403; Error Code: AccessDenied; Request ID: {req_id})",
        "2026-08-29T{time}Z WARNING aws-s3-adapter[4012]: Retrying S3 upload for bucket 'production-data-bucket' key 'logs/2026-08-29/export_{user_id}.json'",
        "2026-08-29T{time}Z ERROR aws-s3-adapter[4012]: 503 Slow Down: Please reduce your request rate to S3 bucket 'production-data-bucket' (prefix: logs/)",
        "2026-08-29T{time}Z CRITICAL elasticsearch[9200]: ClusterHealthException: Cluster status is RED. 4 primary shards unassigned due to node failure",
        "2026-08-29T{time}Z ERROR elasticsearch[9200]: ElasticsearchException: CircuitBreakingException [parent] Data too large, data for [<http_request>] would be [1048576000/1gb], which is larger than the limit of [1020054732/972.8mb]",
        "2026-08-29T{time}Z ERROR logrotate[2210]: IOError: [Errno 28] No space left on device: '/var/log/syslog.1'",
        "2026-08-29T{time}Z CRITICAL systemd[1]: File system root partition /dev/sda1 reached 100% disk usage capacity (0 bytes free)"
    ]
}

def generate_logs():
    base_time = datetime(2026, 8, 29, 10, 0, 0)
    for rel_path, templates in SERVICES.items():
        full_path = os.path.join(BASE_LOG_DIR, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        lines = []
        # Generate 150 log entries per log file
        for i in range(150):
            t = base_time + timedelta(seconds=i * 20 + random.randint(1, 10))
            time_str = t.strftime("%H:%M:%S.") + f"{random.randint(100, 999)}"
            template = random.choice(templates)
            
            entry = template.format(
                time=time_str,
                thread=random.randint(100, 999),
                other_thread=random.randint(100, 999),
                user_id=random.randint(1000, 9999),
                tx_id=random.randint(100000, 999999),
                ip=random.randint(2, 254),
                amount=random.randint(15, 800),
                partition=random.randint(0, 3),
                lag=random.randint(50000, 95000),
                conn_pct=random.randint(85, 100),
                timestamp=int(t.timestamp()),
                req_id=f"{random.randint(1000,9999):X}"
            )
            lines.append(entry)
            
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
            
        print(f"[Generated] {rel_path}: {len(lines)} log entries.")

if __name__ == "__main__":
    generate_logs()
