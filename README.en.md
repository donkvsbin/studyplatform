# LearnHub

[简体中文](README.md) | **English**

A free programming learning platform in Chinese and English, built with Vue 3, TypeScript, Flask, and SQLite. Features include a course catalog, phone-number registration and login, lessons, saved learning progress, video resume, course quizzes and result history, an admin dashboard, and a DeepSeek-powered learning assistant.

The interface uses a black-and-white theme. Sign-up is available from the login page. Every new visit or page refresh follows your system appearance; click the sun/moon icon to switch between light and dark modes for the current page session.

## Download

Visit the [GitHub repository](https://github.com/donkvsbin/studyplatform) and select **Code → Download ZIP**, or clone it with Git:

```powershell
git clone https://github.com/donkvsbin/studyplatform.git
cd studyplatform
```

After downloading or extracting the project, open its root folder and follow the steps below to install dependencies and run the website locally.

## Windows setup

Tested versions: Python **3.14.2**, Node.js **24.12.0**, and npm **11.6.2**. Install Python and Node.js on your computer before running setup. Dependencies must be installed separately on each computer.

For the first run, double-click `setup.bat` in the project root, or run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

To start the website, double-click `start.bat`, or run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Keep the terminal open; press Ctrl+C to stop the server. The startup script runs database migrations, initializes demo courses without overwriting existing content, builds the frontend, and starts Waitress. Existing accounts, progress, results, and manual edits are preserved.

You can also open the entire project in PyCharm and select `backend/.venv/Scripts/python.exe` as the interpreter. Run `start.bat` once to build the frontend, then stop the server. Right-click `backend/run.py` and select **Run** to start the app at the same address. After changing frontend code, rebuild it or use development mode.

## Accounts and administration

Learners can register on the website using a phone number. Registration does not send an SMS. There is no public default administrator account or password.

To create an administrator, run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m flask --app app:create_app create-admin
```

Enter a phone number and password when prompted, then log in on the website and open **Administration**. Administrators can manage bilingual categories, courses, chapters, lessons, and quizzes; publish or unpublish courses; and search, enable, or disable learner accounts.

Unpublish a course before editing it. Archiving preserves learning history. Publishing requires complete bilingual content, valid lessons, and at least three complete quiz questions.

Learners can open **My learning → Quiz history** to review scores and explanations. Existing results remain available after a course is unpublished.

To reset a forgotten password, run this command from `backend`:

```powershell
.\.venv\Scripts\python.exe -m flask --app app:create_app reset-password
```

Resetting a password invalidates existing sessions.

## DeepSeek assistant

Set `DEEPSEEK_API_KEY` in `backend/.env`, then restart the server. The key is read only by the backend. Configure the model with `DEEPSEEK_MODEL`.

When no key is configured, the assistant displays a configuration notice and the other learning features remain available. Conversations stay on the current page and are not saved to the database.

## Development and testing

For development, run the backend and frontend in separate terminals:

```powershell
# Terminal A: from backend
.\.venv\Scripts\python.exe -m flask --app app:create_app run --host 127.0.0.1 --port 5000 --debug

# Terminal B: from frontend, using Node.js 24
npm.cmd run dev
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173).

Run tests from the indicated folders:

```powershell
# From backend
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q

# From frontend
npm.cmd test
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e
```

End-to-end tests use a temporary database and ports 5001/5174. Test administrator and learner accounts exist only in that temporary database; tests leave your regular data untouched.

The demo video is an original 12-second silent clip. Its source is in `scripts/generate_demo_video.py`. FFmpeg is not required to run the website.

## Data, backups, and another computer

SQLite is stored at `backend/instance/learnhub.db`, regardless of the working directory. To back it up, run this command from the project root:

```powershell
.\backend\.venv\Scripts\python.exe scripts/backup_db.py
```

Backups are written to `backend/instance/backups/`. Before restoring, stop the server and back up the current file, then replace `learnhub.db` with the selected backup. Do not merge databases through Git.

On another computer, download the same commit or tag, install the tested tools, run `setup.bat`, and create your own administrator account. Environment files, secrets, the instance folder, virtual environments, `node_modules`, and build outputs are excluded from Git. Each computer has its own accounts and learning records.

When `SECRET_KEY` is empty, a random key is generated in the instance folder. Changing the key signs out existing sessions. To select a Python executable on Windows, set the `LEARNHUB_PYTHON` environment variable to its path before running setup.

### macOS / Linux

The following workflow has not yet been tested on macOS or Linux:

```bash
# From the project root
cd backend
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -m flask --app app:create_app db upgrade
.venv/bin/python -m flask --app app:create_app seed-demo

cd ../frontend
npm ci
npm run build

cd ../backend
.venv/bin/python run.py
```

The source is available on [GitHub](https://github.com/donkvsbin/studyplatform). After downloading it, install dependencies and verify startup on each computer.
