# Dhwani RIS DevOps Assignment
**Ref:** DEVOPS-ASSIGN-01

## How to Start the Stack

### Prerequisites
- Docker Desktop installed and running
- Git installed

### Steps
```bash
# 1. Clone the repository
git clone https://github.com/Kartik27baliyan/dhwani-devops-assignment.git
cd dhwani-devops-assignment

# 2. Create the environment file with your credentials
echo "DB_ROOT_PASSWORD=your_password_here" > .env

# 3. Start the stack
docker compose up -d --build

# 4. Visit the application
open http://localhost