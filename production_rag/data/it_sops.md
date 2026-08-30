# Enterprise IT Infrastructure & Cloud Services Playbooks (SOPs)

This knowledge base contains standardized operating procedures for diagnosing and mitigating infrastructure incidents across distributed systems, cloud services, databases, and microservice mesh environments.

---

## SOP-201: Kafka Consumer Group Rebalance & High Consumer Lag

### Incident Symptoms & Error Logs
- Microservice logs contain: `CommitFailedException`, `GroupCoordinatorNotAvailableException`, `Offset commit failed: RebalanceInProgressException`, or `Consumer lag exceeds threshold (lag > 50000)`.

### Root Cause
A consumer thread takes longer than `max.poll.interval.ms` to process a batch of records (often due to slow downstream DB calls or memory garbage collection pauses), causing the Kafka broker to mark the consumer dead and initiate a cluster-wide partition rebalance.

### Immediate Mitigation Steps
1. **Identify the lagging consumer group**:
   ```bash
   kafka-consumer-groups.sh --bootstrap-server kafka-broker.internal:9092 --describe --group order-processing-group
   ```
2. **Increase `max.poll.interval.ms`** or reduce `max.poll.records` in consumer configuration:
   ```properties
   max.poll.interval.ms=300000
   max.poll.records=100
   ```
3. **Restart consumer pods cleanly**:
   ```bash
   kubectl rollout restart deployment/order-processor-service -n production
   ```

### Verification
Run:
```bash
kafka-consumer-groups.sh --bootstrap-server kafka-broker.internal:9092 --group order-processing-group --describe | grep LAG
```
Ensure `LAG` decreases toward 0 across all partitions.

---

## SOP-202: Redis Cluster Out-of-Memory (OOM) & Key Eviction

### Incident Symptoms & Error Logs
- Application logs show: `OOM command not allowed when used memory > 'maxmemory'`, `RedisException: READONLY You can't write against a read only replica`, or `Key eviction rate spike`.

### Root Cause
Redis memory usage reached 100% of allocated limit, and `maxmemory-policy` is set to `noeviction` or eviction cannot keep up with high write throughput.

### Immediate Mitigation Steps
1. **Check current memory stats**:
   ```bash
   redis-cli -h redis-cluster.internal -p 6379 INFO memory
   ```
2. **Identify key memory consumers**:
   ```bash
   redis-cli -h redis-cluster.internal -p 6379 --bigkeys
   ```
3. **Update eviction policy to `allkeys-lru` or flush volatile cache**:
   ```bash
   redis-cli -h redis-cluster.internal -p 6379 CONFIG SET maxmemory-policy allkeys-lru
   ```
4. **Purge expired sessions or temp cache keys**:
   ```bash
   redis-cli -h redis-cluster.internal -p 6379 EVAL "return redis.call('del', unpack(redis.call('keys', 'cache:temp:*')))" 0
   ```

### Verification
Verify `used_memory_human` is below 80% of `maxmemory_human`:
```bash
redis-cli -h redis-cluster.internal -p 6379 INFO memory | grep human
```

---

## SOP-203: PostgreSQL Deadlocks & Replication Lag

### Incident Symptoms & Error Logs
- App logs show: `ERROR: deadlock detected`, `detail: Process 18402 waits for ExclusiveLock on relation`, or `PostgreSQL replica lag > 600s`.

### Root Cause
Concurrent transactions acquiring locks on the same database tables in opposing order, or high WAL writing workload overloading the read replicas.

### Immediate Mitigation Steps
1. **View active lock conflicts & deadlocks**:
   ```sql
   SELECT pid, blocked_by.pids AS blocked_by, query_to_xml(query, true, false, '') 
   FROM pg_stat_activity 
   JOIN (SELECT array_agg(pid) AS pids, blocking_pid FROM (
       SELECT pid, unnest(pg_blocking_pids(pid)) AS blocking_pid FROM pg_stat_activity
   ) sub GROUP BY blocking_pid) blocked_by ON pg_stat_activity.pid = blocked_by.blocking_pid;
   ```
2. **Terminate the blocking query session**:
   ```sql
   SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE pid = 18402;
   -- If cancel fails, force terminate:
   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = 18402;
   ```
3. **Check replication lag status on standby nodes**:
   ```sql
   SELECT client_addr, pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes FROM pg_stat_replication;
   ```

### Verification
Run:
```bash
psql -h pg-primary.internal -U dbadmin -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
```

---

## SOP-204: Nginx 502 Bad Gateway / Upstream Connection Refused

### Incident Symptoms & Error Logs
- Ingress logs show: `502 Bad Gateway`, `connect() failed (111: Connection refused) while connecting to upstream`, or `no live upstreams while connecting to upstream`.

### Root Cause
The backend application pod/process crashed or failed its TCP health check, leaving Nginx pointing to an inactive IP address.

### Immediate Mitigation Steps
1. **Test upstream target directly from Nginx instance**:
   ```bash
   curl -I http://10.244.2.45:8080/healthz
   ```
2. **Reload Nginx configuration to update DNS endpoints**:
   ```bash
   nginx -s reload
   ```
3. **Restart application backend deployment**:
   ```bash
   kubectl rollout restart deployment/payment-gateway-service -n production
   ```

### Verification
```bash
curl -Iv https://api.company.com/payment/health
```
Ensure HTTP response status is `200 OK`.

---

## SOP-205: AWS S3 Access Denied (403 Forbidden) & Rate Limiting (503 Slow Down)

### Incident Symptoms & Error Logs
- Logs contain: `com.amazonaws.services.s3.model.AmazonS3Exception: Access Denied (Service: Amazon S3; Status Code: 403)`, `RequestTimeout`, or `503 Slow Down (Please reduce your request rate)`.

### Root Cause
Bucket policy missing IAM permissions, KMS key decryption policy missing, or exceeding 3,500 PUT/DELETE requests per second per prefix.

### Immediate Mitigation Steps
1. **Fix KMS / S3 Bucket IAM Policy**: Ensure application IAM Role has `s3:GetObject`, `s3:PutObject`, and `kms:Decrypt` actions.
2. **Implement Hash Prefixes** for high-throughput S3 writes:
   * Instead of writing to `s3://my-bucket/logs/2026-08-29/...`, use `s3://my-bucket/logs/<hash_prefix>/2026-08-29/...`.
3. **Verify AWS STS credentials**:
   ```bash
   aws sts get-caller-identity
   ```

### Verification
Test object uploading using AWS CLI:
```bash
aws s3 cp /tmp/healthcheck.txt s3://production-data-bucket/test-check.txt
```

---

## SOP-206: Kubernetes Pod OOMKilled & CrashLoopBackOff

### Incident Symptoms & Error Logs
- Logs report: `Pod backend-service in namespace production terminated with exit code 137 (OOMKilled)`, `Out of memory: Kill process`.

### Immediate Mitigation Steps
1. Describe pod status:
   ```bash
   kubectl describe pod -n production backend-service-7f89
   ```
2. Increase RAM resource limits in deployment manifest:
   ```bash
   kubectl set resources deployment/backend-service -n production --limits=memory=2Gi,cpu=1000m
   ```

---

## SOP-207: Elasticsearch Cluster Red Status & Unassigned Shards

### Incident Symptoms & Error Logs
- Logs show: `ClusterHealthException: Cluster status is RED`, `unassigned_shards`, `ElasticsearchException: CircuitBreakingException [parent] Data too large`.

### Root Cause
One or more primary shards are unassigned due to node failure or low disk space (high watermark exceeded 85%).

### Immediate Mitigation Steps
1. **Check cluster health**:
   ```bash
   curl -X GET "http://es-cluster.internal:9200/_cluster/health?pretty"
   ```
2. **Identify unassigned shards reason**:
   ```bash
   curl -X GET "http://es-cluster.internal:9200/_cluster/allocation/explain?pretty"
   ```
3. **Reroute unassigned shards**:
   ```bash
   curl -X POST "http://es-cluster.internal:9200/_cluster/reroute?retry_failed=true"
   ```

---

## SOP-208: Expired SSL/TLS Certificates

### Incident Symptoms & Error Logs
- Logs show: `SSL handshake failed, certificate expired (CN=api.internal.net)`.

### Resolution Steps
```bash
certbot renew --non-interactive && systemctl reload nginx
```

---

## SOP-209: SSH Authentication Timeout & Port 22 Block

### Resolution Steps
Verify security group rules and SSH daemon:
```bash
ufw allow 22/tcp && systemctl restart sshd
```

---

## SOP-210: Server Disk Full (100% Usage) & Log Rotation Failure

### Incident Symptoms & Error Logs
- Logs report: `No space left on device`, `IOError: [Errno 28] No space left on device`.

### Resolution Steps
1. Find top space-consuming files:
   ```bash
   du -sh /var/log/* | sort -rh | head -n 10
   ```
2. Truncate bloated log files:
   ```bash
   truncate -s 0 /var/log/syslog
   ```
3. Force logrotate run:
   ```bash
   logrotate -f /etc/logrotate.conf
   ```

---

## SOP-211: Auth Service JWT Token Expiry & Signature Verification Failures

### Incident Symptoms & Error Logs
- Logs show: `ERROR auth_service.jwt.verifier: JWT Signature verification failed: Token expired at timestamp`, `com.auth.jwt.JWTVerifier.verifyToken`, `Token expired at 2026-08-30T...`.

### Root Cause
Client applications are passing access tokens that have exceeded their Time-To-Live (TTL), or server clock skew between `auth-service` and API gateways causing immediate token validation rejection.

### Immediate Mitigation Steps
1. **Inspect auth-service environment settings**:
   ```bash
   kubectl exec -it deployment/auth-service -n production -- env | grep JWT
   ```
2. **Rotate JWKS public keys and adjust JWT TTL in ConfigMap**:
   ```bash
   kubectl edit configmap auth-service-config -n production
   # Set JWT_ACCESS_TOKEN_TTL=7200 (Increase from 3600s to 7200s)
   ```
3. **Restart Auth Service Pods to reload signing keys**:
   ```bash
   kubectl rollout restart deployment/auth-service -n production
   ```
4. **Verify NTP Clock Synchronization**:
   ```bash
   chronyc tracking
   ```

### Verification & Health Check
Issue a fresh token request via the Auth API:
```bash
curl -X POST http://auth-service.internal:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"client_id": "api_client_01", "client_secret": "prod_secret_key"}'
```

---

## SOP-212: PostgreSQL Long-Running Queries & High CPU / Lock Contention

### Incident Symptoms & Error Logs
- Logs report: `postgres.slow_query - Long running transaction detected: PID 19204 running for 412s`, `seq_scan on table orders`, `Wait Event: IO:DataFileRead`, or `ExclusiveLock on relation 'orders'`.

### Root Cause
Unindexed sequential table scan (`seq_scan`) on large multi-million row tables (`orders`, `transactions`) causing runaway queries to hold locks, consume database connections, and spike server CPU utilization.

### Immediate Mitigation Steps
1. **Identify long-running query PIDs and durations**:
   ```sql
   SELECT pid, now() - query_start AS duration, query, state, wait_event_type 
   FROM pg_stat_activity 
   WHERE state != 'idle' AND (now() - query_start) > interval '3 minutes'
   ORDER BY duration DESC;
   ```
2. **Terminate offending long-running backend PID**:
   ```sql
   SELECT pg_cancel_backend(19204);
   -- If cancel fails, force terminate:
   SELECT pg_terminate_backend(19204);
   ```
3. **Set statement timeout to prevent future runaway queries**:
   ```sql
   ALTER DATABASE production_db SET statement_timeout = '30s';
   ```
4. **Create composite index concurrently to prevent table scans**:
   ```sql
   CREATE INDEX CONCURRENTLY idx_orders_status_created_at ON orders (status, created_at DESC);
   ```

### Verification & Health Check
Verify query execution plan switches from `Seq Scan` to `Index Scan`:
```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'PENDING' ORDER BY created_at DESC;
```
Ensure execution time drops below 10ms and connection pool active count drops below 50%.
