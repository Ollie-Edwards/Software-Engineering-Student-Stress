# Get Started

Follow these steps to set up the project locally.

## 1. Install Docker Desktop

Download and install Docker Desktop from [here](https://www.docker.com/products/docker-desktop/).  
After installation, log in with your Google account or email.

## 2. Set Up Database Viewer (DBeaver) (Optional)

1. Open **DBeaver**.
2. Click **New Connection**.
3. Select **PostgreSQL**.
4. Enter the following connection details:

   - **Host:** `localhost`
   - **Port:** `5432`
   - **Database:** `mydb`
   - **Username:** `myuser`
   - **Password:** `mypass`

5. Click **Download drivers** if prompted.

6. Once connected, view the databases on `Mydb > Schemas > public > Tables > subtasks / tasks / users`

### Note: Restarting Database after changing schema.sql or seed.sql

If you need to reset the database schema or seed data:

```bash
# Stop containers and delete volumes
docker-compose down -v

# Rebuild and start containers
docker compose up --build
```

## 4. Installation

1. `git clone https://github.com/Ollie-Edwards/Software-Engineering-Student-Stress.git`

2. `cd .\Software-Engineering-Student-Stress\`

3. Ensure docker desktop is installed and open

4. `.\start.bat`

## 5. Starting the application

Run: `.\start.bat` in the root directory to start the application
