# Engineering Day Coding Challenge
**Subtitle**: *Engineering Day 2026 — Coding Competition Platform*

A production-ready, full-stack college competitive programming platform built to support ~100 simultaneous participants across 3 distinct contest rounds.

---

## 🚀 Technology Stack

- **Frontend**: Next.js 15+ (App Router), TypeScript, Tailwind CSS, Lucide Icons, Monaco Editor (`@monaco-editor/react`)
- **Backend**: Python 3.13+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Bcrypt, PyJWT
- **Database**: SQLite (default zero-config local development) / PostgreSQL (production AWS EC2/RDS compatible)
- **Code Execution**: Pure Judge0 Integration (`JUDGE0_URL`) with fail-safe `503 Service Unavailable` handling (NO local execution fallbacks).
- **Deployment**: AWS EC2 Free Tier (Ubuntu + Nginx + Systemd) for Backend & Vercel for Frontend.

---

## 🎯 Competition Rounds

1. **Round 1 — Coding Aptitude**: 20 Multiple Choice Questions covering DSA, C/C++, Java, Python, Time Complexity, OOP, and Output Prediction. Includes server-authoritative timer, question status palette (Answered, Unanswered, Marked for Review), and auto-submit.
2. **Round 2 — Debug the Code**: 5 Debugging Challenges. Monaco Code Editor with 15-second interval autosave, event-triggered autosaves, "Run Code" against sample test cases, and "Submit Solution" against hidden test cases.
3. **Round 3 — Final Coding Challenge**: 3 Algorithmic Problems (Easy $\rightarrow$ Medium $\rightarrow$ Hard). Features Monaco Editor, language selector (C, C++, Java, Python), partial scoring based on passed test cases, and hidden test-case protection.

---

## ⚡ Key Features & Safety Mechanisms

- **Pure Judge0 Execution**: Participant code is executed remotely via Judge0 REST API. Direct local execution (`subprocess`, `eval`, `exec`) is strictly prohibited. If Judge0 is offline, backend returns a clear `"Code execution service unavailable"` message.
- **Draft Autosave & State Recovery**: Monaco editor drafts save automatically every 15 seconds and on key actions (Run, Submit, problem switch, tab exit). Page refreshes or crashes restore exact draft code and remaining server time.
- **`contest_settings` Database Control**: Central database table managing global settings, Maintenance Mode, Emergency Participant Lock, and per-user rate limits.
- **3-Tier Leaderboard Tie-Breaking**:
  1. Highest Total Score ($\text{Score}_{R1} + \text{Score}_{R2} + \text{Score}_{R3}$)
  2. Lowest Total Contest Time
  3. Earliest Final Accepted Submission Timestamp
- **Anti-Cheating Tracking**: Tab switching and window blur listeners log violations to backend with timestamp and cause warning popups.
- **Database Backup & Results Export**: Safe admin-only JSON database snapshot generator (`/api/admin/export?format=json`) and CSV leaderboard exporter (`/api/admin/export?format=csv`).

---

## 🛠️ Local Development Setup

### 1. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize & seed database (Creates admin user & 3 contest rounds with sample questions)
python -m app.seed

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

FastAPI Interactive Docs will be accessible at: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

Next.js Frontend will be accessible at: `http://localhost:3000`

---

## 🔐 Development Credentials

### Admin Account
- **Email**: `admin@engday.edu`
- **Password**: `admin123`
- **Console Route**: `http://localhost:3000/admin/login`

---

## 🧪 Automated Tests & 100-Participant Load Test

### 1. Pytest Test Suite
Run the automated Pytest suite covering timer enforcement, rate limiting, Judge0 failure handling, autosave recovery, emergency lock, maintenance mode, and leaderboard tie-breaking:

```bash
cd backend
python -m pytest tests/test_competition.py
```

### 2. 100-Participant Load Test Simulation
Simulate 100 concurrent participants logging in, starting rounds, answering MCQs, autosaving code drafts, and accessing leaderboard:

```bash
cd backend
python tests/load_test_100_sim.py
```

---

## ☁️ AWS EC2 Free Tier Deployment Manual

1. **Launch EC2 Instance**:
   - Ubuntu 22.04 LTS or 24.04 LTS (t2.micro / t3.micro - Free Tier eligible)
   - Allow Security Group Ports: `80` (HTTP), `443` (HTTPS), `22` (SSH)

2. **Clone & Run Setup Script**:

```bash
git clone https://github.com/your-org/engineering-day-coding.git
cd engineering-day-coding
chmod +x deployment/aws/setup_ec2.sh
./deployment/aws/setup_ec2.sh
```

3. **Backend Service Management**:

```bash
sudo systemctl status engday-backend
sudo systemctl restart engday-backend
```

---

## 🌐 Vercel Deployment for Frontend

1. Connect your GitHub repository to Vercel.
2. Set Root Directory to `frontend`.
3. Configure Environment Variable: `NEXT_PUBLIC_API_URL=https://your-ec2-domain.com/api`
4. Deploy!
