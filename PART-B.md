# Part B — Diagnosis of Faulty Deployment

---

## Problem 1 — Wrong Volume Mount Path

**1. Faulty Line:**
volumes:
dbdata:/var/lib/mysql/data

**2. Symptom Explained:** S2 — Data loss after server reboot.

**3. How to Confirm:**
Run `docker volume inspect dbdata` and examine the Mountpoint on the
host. Then check inside the running container:
docker compose exec db ls /var/lib/mysql
You will see MariaDB system files there (ibdata1, aria_log etc).
Now check `/var/lib/mysql/data` — it will be empty or missing entirely.
This proves data was never written to the volume, only to the
container's ephemeral layer which is destroyed on reboot.

**4. Fix:**
volumes:

dbdata:/var/lib/mysql

---

## Problem 2 — App Does Not Wait for Database to be Ready

**1. Faulty Line:**
depends_on:

db

**2. Symptom Explained:** S4 — Application starts unable to reach
database roughly one reboot in three.

**3. How to Confirm:**
Run `docker compose logs app` immediately after a failed boot.
You will see repeated connection errors such as:
`Can't connect to MySQL server on 'db'`
This happens because MariaDB takes variable time to initialize
depending on server load at boot time. One in three reboots the
server is under higher load, so MariaDB takes longer, and the app
gives up before the database is ready.

**4. Fix:**
Add a healthcheck to the db service and use condition: service_healthy:
db:
healthcheck:
test: ["CMD", "mysqladmin", "ping", "-h", "localhost",
"-u", "root", "-p${DB_ROOT_PASSWORD}"]
interval: 5s
timeout: 5s
retries: 5

app:
depends_on:
db:
condition: service_healthy

---

## Problem 3 — Missing Forwarded Protocol Headers

**1. Faulty Line:**
nginx.conf is missing:
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Proto $scheme;

**2. Symptom Explained:** S3 — Browser security warnings and links
pointing to unreachable addresses.

**3. How to Confirm:**
Open the browser Network tab and perform a login or any redirect action.
Inspect the Location header in the response. It will show
`http://grants.district.example.gov.in/...` instead of `https://`.
This is because the app receives the request from Nginx over plain
HTTP internally and has no way of knowing the original request came
in over HTTPS via the load balancer. It therefore generates all
internal redirect URLs with http://, which the browser rejects as
Mixed Content when the outer connection is HTTPS.

**4. Fix:**
Add to nginx.conf location block:
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
The application also needs to be configured to trust the
X-Forwarded-Proto header, which in most Python frameworks means
setting SECURE_PROXY_SSL_HEADER or equivalent.

---

## Problem 4 — Memory Limit Causing OOM Kills

**1. Faulty Line:**
deploy:
resources:
limits:
memory: 256M
on the app service.

**2. Symptom Explained:** S1 — Application restarts 2-3 times a day
with nothing unusual in application logs.

**3. How to Confirm:**
Run this command immediately after a restart occurs:
docker inspect dhwani-devops-assignment-app-1 --format '{{.State.OOMKilled}}'
If it returns true, the container was killed by the Linux OOM killer
because it exceeded its memory limit. The reason nothing appears in
the application logs is that the process is killed externally by the
kernel, not by the application itself, so there is nothing for the
app to log.

**4. Fix:**
Profile the application memory usage first using docker stats, then
set the limit to observed peak plus 20% headroom:
deploy:
resources:
limits:
memory: 512M

---

## Problem 5 — Credentials Committed to Git History

**1. Faulty Setting:** The .env file containing DB_ROOT_PASSWORD was
added in the third commit and deleted in the ninth.

**2. Symptom Explained:** None of S1 to S4. This is a critical
security vulnerability independent of the reported symptoms.

**3. How to Confirm:**
git log --oneline
git show <third-commit-hash>:.env
This will display the password in plain text from history even though
the file was deleted in a later commit. The secret is permanently
embedded in the repository history.

**4. Fix:**
Use BFG Repo-Cleaner or git-filter-repo to purge the file from all
history, then immediately rotate the database root password:
Using BFG
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
Then rotate the password in the live database immediately.

---

## Deliberate and Correct Setting

**Setting:**
ports:

"127.0.0.1:3306:3306"
on the db service.

**Defence:** This is intentional and correct. By binding the MariaDB
port to 127.0.0.1 rather than 0.0.0.0, the database is only
reachable from the local machine and the internal Docker network.
It is not exposed to the public internet. Changing this would make
the deployment significantly worse by allowing anyone on the internet
to attempt a direct connection to the database. This setting should
be left exactly as it is.