# Dhwani RIS DevOps Assignment  
Created By: Kartik Baliyan

## How to Start the Stack

### Prerequisites
- Docker Desktop installed and running
- Git installed / Git Bash UI 

### Steps

# 1. Clone the repository
git clone https://github.com/Kartik27baliyan/dhwani-devops-assignment.git
cd dhwani-devops-assignment

# 2. Create the environment file
echo "DB_ROOT_PASSWORD=your_password_here" > .env

# 3. Start the stack
docker compose up -d --build

# 4. Visit the application
http://localhost

# 5. Check health endpoint
curl http://localhost/health

## Docker Images Output
REPOSITORY                       TAG       IMAGE ID       CREATED         SIZE
dhwani-devops-assignment-app     latest    249fbb8fff32   1 hour ago      531MB
mariadb                          10.6      92e50059ea0a   2 weeks ago     440MB
nginx                            alpine    4a73073bd557   3 weeks ago     93.6MB

## Architecture
Browser → Nginx (Port 80) → Flask App (Port 8000) → MariaDB (Port 3306)

## Memory Limits Justification
| Service | Limit | Reason |
|---------|-------|--------|
| MariaDB | 256MB | Small dataset, single app database |
| Flask App | 512MB | Handles requests and DB connections |
| Nginx | 128MB | Lightweight proxy, minimal memory needed |

## Most Awkward Requirement
The most awkward requirement was making the application wait until the database was genuinely ready to accept connections, not merely until its container had started. Initially, the app container would start and immediately try to connect to MariaDB, which was still initializing.
This caused connection errors on first boot. I first tried using only depends_on: db which only checks if the container is running, not if MariaDB is actually accepting connections. The fix required two things working together: a healthcheck on the db service using mysqladmin ping,and changing depends_on to use condition: service_healthy. This ensures Docker waits for MariaDB to pass its health check before starting the app container.

## Screen Recording
# LINK: 
