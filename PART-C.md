# Part C — Infrastructure Decisions Under Constraints

---

# C1. Allocate the 4 GB

My allocation for the single 2 vCPU / 4 GB VM:

| Component          | Allocation | Reason                                      |
|--------------------|------------|---------------------------------------------|
| Operating System   | 512 MB     | Minimum for Ubuntu/Debian stable operation  |
| MariaDB            | 1.5 GB     | Largest consumer; indexes and buffer pool   |
| Frappe Workers (2) | 1.0 GB     | Two gunicorn workers at ~512MB each         |
| Redis              | 256 MB     | Cache and job queue only                    |
| Nginx              | 64 MB      | Lightweight proxy                           |
| Buffer/Reserved    | 668 MB     | Prevents OOM kills during month-end spikes  |

**First thing I would reduce:** The number of Frappe/gunicorn worker
processes, dropping from 2 to 1.

**Symptom that tells me allocation is wrong:** The application starts returning 502 Bad Gateway or requests take over 30 seconds during normal hours — not just month-end. This means workers are being killed by the OOM killer, not just slow. I would confirm with:
`docker inspect <app-container> --format '{{.State.OOMKilled}}'`

---

# C2. Backups I Would Rely On

**Backup arrangement:**
- `mariadb-dump` runs every hour via cron, producing a compressed and encrypted SQL dump.
- Dumps are stored locally for 24 hours (fast restore).
- Every dump is also synced to an S3-compatible object storage bucket in a different geographic region within 5 minutes of creation.
- Daily snapshots retained for 30 days.
- Monthly snapshots retained for 12 months.
- Audit rules mean hard-deletes are prohibited, so backup size grows predictably and slowly.

**RPO:** 1 hour (maximum data loss if server dies between backups).
**RTO:** 2 hours (provision new VM, install stack, restore latest dump).

Q: How I know backups actually restore:
This is the part that matters. I would run an automated restore drill every Sunday at midnight:
1. A script pulls the latest backup from S3.
2. Restores it into a temporary Docker container running MariaDB.
3. Runs `SELECT COUNT(*) FROM tabBeneficiary` and three other critical tables.
4. If any query fails or returns zero rows, it sends an urgent SMS alert immediately.
5. The temporary container is destroyed after the check.

A backup that has never been restored is not a backup. This drill catches silent corruption before an emergency does.

---

# C3. Reply to Junior Engineer

"Hey, I'd stop before running that on production right now. Three specific problems with this plan:

**During the migration:**
If the migration locks the beneficiary table, all 40 users will see a frozen screen or errors until it completes. At 3 PM on a Wednesday
that is peak usage. Even a migration that takes 'a few minutes' on your machine can take much longer on production data.

**During the proposed restore:**
A morning backup is roughly 6 hours old. Restoring it means we permanently lose every record created today. Given our audit rules,
that data cannot be recreated and the loss cannot be explained away.'Just restore it' is not a safe recovery here.

**What I would do instead:**
1. Test the migration on a copy of production data in a staging container first. Time it exactly.
2. Schedule the migration for 6:00 PM after users are off the system.
3. Take a fresh manual backup immediately before running it, not 6 hours before.
4. Have the rollback script ready before we start, not after something breaks.

Let's schedule it for this evening. I will be on the call with you."

---

# C4. Zero-Downtime Deployment on a Single Server

Honest answer: True zero-downtime is not achievable on this setup.**

A proper zero-downtime deployment (Blue-Green) requires running two full copies of the application simultaneously — the old version serving traffic while the new version starts up. On 4 GB RAM with MariaDB already consuming 1.5 GB, there is not enough memory to run two application stacks at once without triggering OOM kills.

**The best arrangement actually achievable:**
A planned maintenance window of 2 to 3 minutes during a low-traffic period (after 7 PM based on the usage pattern described):

1. Nginx serves a static maintenance page.
2. The old app container stops.
3. Database migrations run.
4. The new app container starts and passes a health check.
5. Nginx resumes routing to the live app.

Total downtime: 2 to 3 minutes, predictable and scheduled.

**What I would tell the department:**
"On a single server with the current budget, we can make deployments fast, safe and scheduled — but not invisible. Every deployment will
require a 2-3 minute window, which we will always announce in advance and schedule after working hours. If zero-downtime becomes a hard
requirement, it will require a second server, which we should plan for next financial year."