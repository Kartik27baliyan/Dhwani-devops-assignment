# Part D — Pipeline Review

Reviewing: `.github/workflows/deploy.yml`
Format: Pull request comments

---

## BLOCKING — Must fix before merge

1. Secret printed to logs
env:
  REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
run: |
  echo "Authenticating with token $REGISTRY_TOKEN"
  Block reason: This prints the registry token in plain text to the GitHub Actions log. Anyone with read access to the repository can see the secret. Remove the echo line entirely. Authentication should happen silently:
run: |
  echo "$REGISTRY_TOKEN" | docker login registry.example.com -u _ --password-stdin docker build -t registry.example.com/grants:latest .
2. Tests are optional — failures are silently ignored
  - name: Run tests
  run: pytest tests/ || true
  lock reason: The || true means the pipeline continues and deploys to production even if every test fails. This defeats the entire purpose of running tests. 
  Remove || true:
- name: Run tests
  run: pytest tests/
3. Image pushed without authentication
- name: Push image
  run: docker push registry.example.com/grants:latest
  Block reason: There is no docker login step before this push.The build step sets the env var but never uses it to authenticate.
This will fail in a clean runner environment and if it somehow succeeds it means the registry is publicly writable, which is a security problem. Add a proper login step before build and push.
4. Deploying only latest tag — no version pinning docker build -t registry.example.com/grants:latest .
Block reason: Using only latest means there is no way to identify which version is running in production or roll back to a specific previous build. Tag with the Git SHA as well: 
   docker build \
  -t registry.example.com/grants:latest \
  -t registry.example.com/grants:${{ github.sha }} .
5. Unpinned action version
- uses: actions/checkout@master
Block reason: Pinning to master means the action can change without warning and silently break or compromise the pipeline.
Pin to a specific version:
- uses: actions/checkout@v4
NON-BLOCKING — Raise as comments, do not block merge
6. No deployment verification after deploy
After docker compose up -d, the pipeline has no step to confirm the new containers are actually healthy. The pipeline reports green
even if the app crashes immediately after starting. Suggest adding:
- name: Verify deployment
  run: |
    sleep 10
    curl -f https://prod.example.com/health || exit 1
7. SSH key management not visible
The deploy step uses SSH but there is no step showing how the SSH key is injected into the runner. This likely works because someone
added it manually to the runner, but it is not documented and will silently break if the runner is replaced. Suggest adding an explicit
ssh-agent step using a stored secret.
8. No rollback step
If the deployment fails, there is no automated rollback. For a production system serving 40 concurrent users, a manual rollback
means downtime. Suggest adding a rollback job triggered on failure.
9. Trigger on push to main
on:
  push:
    branches: [main]
This is correct and intentional. Deploying on every merge to main is a standard and valid CD pattern for a team of this size.
10. SSH-based deployment mechanism
ssh deploy@prod.example.com \
  "cd /srv/grants && docker compose pull && docker compose up -d"
For a single-server deployment without a Kubernetes cluster or container orchestration platform, SSH plus docker compose is a
perfectly reasonable deployment mechanism. It is simple, auditable and appropriate for the scale described. The mechanism itself is not
the problem — the problems are around it (no auth, no health check,no rollback).
