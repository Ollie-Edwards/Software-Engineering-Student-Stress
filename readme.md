# Testing and Coverage report

See the most recent coverage report here:

https://ollie-edwards.github.io/Software-Engineering-Student-Stress/index.html

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

## 3. Installation

1. `git clone https://github.com/Ollie-Edwards/Software-Engineering-Student-Stress.git`

2. Install NPM and Node.js from https://nodejs.org/en

3. `cd .\Software-Engineering-Student-Stress\`

4. Ensure docker desktop is installed and open

## 4. Starting the application

Run: `.\start.bat` in the root directory to start the application
