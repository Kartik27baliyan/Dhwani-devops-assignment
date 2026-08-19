# AI Usage Log

## Tool Used: ChatGPT

---

### What I used it for:

1. **Initial project scaffolding:** Generating the base Flask application structure, Dockerfile and docker-compose.yml.

2. **Part B written answers:** GPT provided the initial diagnosis of the faulty configuration. I reviewed each finding against the
   symptoms described in the assignment.

3. **Part C written answers:** GPT drafted the initial memory allocation and backup strategy. I adjusted the figures to match the exact constraints given (4GB RAM, 2 vCPU).

4. **Part D pipeline review:** GPT identified the blocking issues.I re-ordered them by severity and added the "Fine as written"
   section after reviewing which parts were genuinely acceptable.

---

### Where I corrected or rejected AI output:

1. **Volume path bug (Part B Problem 1):** Claude initially said the volume path `/var/lib/mysql/data` was "possibly wrong." I
   confirmed it was definitively wrong by running `docker compose exec db ls /var/lib/mysql` myself and verifying that no `/data` subdirectory existed in the official MariaDB image.

2. **Part B - Deliberate setting:** Claude initially flagged the `127.0.0.1:3306:3306` port binding as a potential problem. I
   overrode this and correctly identified it as deliberate and secure.Exposing a database port only on localhost is a security best
   practice, not a bug.

3. **Memory allocation (Part C1):** Claude's first draft gave MariaDB only 1 GB. I increased it to 1.5 GB because the assignment
   specifies 40 concurrent users with month-end spikes, and MariaDB's. InnoDB buffer pool needs adequate RAM to avoid disk I/O becoming
   the bottleneck.

4. **Part D - SSH deployment:** Claude's first draft flagged the SSH deployment mechanism itself as a blocking issue. I disagreed and
   moved it to "Fine as written" because for a single-server deployment at this scale, SSH plus docker compose is appropriate
   and proportionate. The problems are around it, not the mechanism itself.

5. **Dockerfile debugging:** The `cat` commands to write file content in Git Bash were not working correctly. I identified that VS Code
   was the more reliable method and switched approaches independently.