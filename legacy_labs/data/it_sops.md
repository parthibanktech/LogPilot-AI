# SysOps SOP: IT Systems Operations & Troubleshooting Standard Operating Procedures

This document provides step-by-step resolution procedures for common infrastructure and systems incidents.

---

## SOP-101: Database Connection Pool Exhaustion (PostgreSQL / MySQL)

### Incident Description
An application service raises errors indicating it cannot acquire a database connection, or connection limits are exceeded. Typical log messages contain: `connection limit exceeded` or `connection pool exhausted`.

### Diagnostic Steps
1. Log into the database server or check DB metrics to verify current connection count:
   ```bash
   psql -U admin_user -d production_db -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"
   ```
2. Identify idle connections holding onto sessions for too long.

### Resolution Steps
If active sessions exceed thresholds, perform the following actions:
1. **Terminate idle connections** immediately to free up slots:
   ```sql
   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < current_timestamp - interval '5 minutes';
   ```
2. **Increase Database max_connections** temporarily if hardware capacity permits:
   * Edit `postgresql.conf` or equivalent parameter group to increase `max_connections` value.
   * Reload PostgreSQL configurations without restarting the database:
     ```bash
     pg_ctl reload -D /var/lib/postgresql/data
     ```
3. **Configure Connection Pooler** (e.g., PgBouncer) or check the application's maximum pool size setting. Ensure application side `max_connections_limit` is set to less than the database's hard limit.

### Verification
Run:
```bash
psql -U admin_user -d production_db -c "SELECT count(*) FROM pg_stat_activity;"
```
Verify the output count is below 80% of `max_connections`.

---

## SOP-102: Expired SSL/TLS Certificates (Web Servers & API Gateways)

### Incident Description
Clients report connection errors (e.g., `ERR_CERT_DATE_INVALID` or `SSL handshake failed`). Logs show warning/error messages: `SSL handshake failed, certificate expired` or `handshake alert: certificate expired`.

### Diagnostic Steps
1. Query the domain or internal API gateway endpoint to verify the certificate expiration date:
   ```bash
   openssl s_client -connect api.internal.net:443 -servername api.internal.net 2>/dev/null | openssl x509 -noout -dates
   ```
2. Verify local certificate file expiry:
   ```bash
   openssl x509 -in /etc/ssl/certs/api_internal_net.crt -noout -enddate
   ```

### Resolution Steps
1. **Generate a new certificate** or fetch the renewed certificate from the CA (e.g., Let's Encrypt / AWS ACM):
   ```bash
   certbot renew --non-interactive
   ```
   *For manual cert installation, place the new key and cert files in `/etc/ssl/certs/` and `/etc/ssl/private/`.*
2. **Validate Cert and Key match**:
   ```bash
   openssl x509 -noout -modulus -in /etc/ssl/certs/api_internal_net.crt | openssl md5
   openssl rsa -noout -modulus -in /etc/ssl/private/api_internal_net.key | openssl md5
   ```
   *Both MD5 hashes must be identical.*
3. **Reload / Restart the service** hosting the certificate:
   * **Nginx**:
     ```bash
     nginx -t && systemctl reload nginx
     ```
   * **HAProxy**:
     ```bash
     systemctl restart haproxy
     ```
   * **Envoy / API Gateway**: Reload gateway configuration.

### Verification
Verify connection using curl:
```bash
curl -Iv https://api.internal.net
```
Ensure output displays the new validity dates.

---

## SOP-103: Kubernetes Pod Out-of-Memory (OOM) Crash

### Incident Description
Kubernetes pods crash frequently, reporting status `CrashLoopBackOff` or terminating with `OOMKilled` (Exit Code 137). Logs contain: `Out of memory: Kill process` or `Killed process score`.

### Diagnostic Steps
1. Describe the pod to check its last termination state:
   ```bash
   kubectl describe pod -n production backend-service-7f89
   ```
   Look for `Terminated` status with reason `OOMKilled` and exit code `137`.
2. Check memory usage metrics:
   ```bash
   kubectl top pod -n production backend-service-7f89
   ```

### Resolution Steps
1. **Identify memory leak**: If memory growth is monotonic, inspect the application code or profile memory usage.
2. **Increase Memory Resource Limits**:
   * Edit the deployment configuration:
     ```bash
     kubectl edit deployment -n production backend-service
     ```
   * Under `resources.limits.memory`, increase the memory limit (e.g., from `512Mi` to `1Gi` or `2Gi`).
3. **Check Node Availability**: If the entire node is running low on memory, scale the node pool or migrate the pod:
   ```bash
   kubectl cordon node-01 && kubectl drain node-01 --ignore-daemonsets
   ```

### Verification
Run:
```bash
kubectl get pods -n production -w
```
Verify the pod remains in `Running` state and restarts count does not increment.

---

## SOP-104: SSH Connection Timeout / Authentication Failure

### Incident Description
Operators are unable to log into remote servers via SSH, receiving `Connection timed out` or `Permission denied (publickey)`. Logs in `/var/log/auth.log` or `/var/log/secure` show authentication failure alerts.

### Diagnostic Steps
1. Test port 22 connectivity from the local machine:
   ```bash
   nc -zv server-ip 22
   ```
2. Run SSH in verbose debug mode:
   ```bash
   ssh -vvv user@server-ip
   ```

### Resolution Steps
1. **Firewall Block**: If port 22 is timed out, verify cloud Security Groups or local firewall rules (UFW/firewalld):
   ```bash
   ufw allow 22/tcp
   ```
2. **Fix File Permissions**: SSH is highly sensitive to permissions. Ensure the target user's home and `.ssh` directory permissions are correct:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   chown -R user:user ~/.ssh
   ```
3. **Restart SSH Daemon**: If config changes were made, restart `sshd`:
   ```bash
   systemctl restart sshd
   ```

### Verification
Run connection test:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 user@server-ip "echo SSH_OK"
```
Should print `SSH_OK`.
