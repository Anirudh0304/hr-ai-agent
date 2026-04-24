# AI-Powered Talent Scouting & Engagement Agent

An end-to-end prototype that takes a Job Description (JD), discovers matching candidates from CSV input, simulates outreach conversations, and outputs a ranked shortlist on two dimensions:

- Match Score
- Interest Score

The final ranked list is designed to be immediately actionable for recruiters.

## Working Prototype

- Frontend: React + Vite dashboard
- Backend: FastAPI pipeline API
- LLM: Local Ollama (optional; automatic fallback to deterministic simulation if unavailable)

If you deploy the frontend to Netlify, it serves as the demo URL while backend runs locally or on your cloud host.

## Project Structure

```text
backend/
  app/
    main.py
    models.py
    routes/agent.py
    services/
      jd_parser.py
      matching_engine.py
      conversation_engine.py
      scoring_service.py
  requirements.txt
frontend/
  src/
    App.jsx
    main.jsx
    styles.css
  package.json
  vite.config.js
examples/
  sample_jd.json
  sample_candidates.csv
  sample_output.json
docs/
  architecture.md
```

## Local Setup

### 1) Backend setup

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Run backend tests:

```bash
pytest -q
```

API health check:
- GET `http://localhost:8000/health`

### 2) Optional Ollama setup (for LLM-based conversation simulation)

Install Ollama and pull a model:

```bash
ollama pull mistral
ollama serve
```

If Ollama is not available, the app still works using a deterministic fallback for Interest Score.

### 3) Frontend setup

```bash
cd frontend
npm install
# Optional if backend is not local:
# set VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Open:
- `http://localhost:5173`

## API Endpoints

- `POST /api/parse-jd`
  - Input: `{ "title": "...", "description": "..." }`
- `POST /api/upload-csv`
  - Multipart CSV with columns: `candidate_id,name,profile_text`
- `POST /api/run-pipeline`
  - Input: full pipeline payload
  - Output: parsed JD + ranked shortlist

## Pipeline Payload Example

```json
{
  "jd": {
    "title": "Senior AI Engineer",
    "description": "Need Python, FastAPI, LLM, AWS and Docker skills. Nice to have React."
  },
  "candidates": [
    {
      "candidate_id": "C-001",
      "name": "Anya Krish",
      "profile_text": "Senior Python engineer with FastAPI and AWS. Open to work."
    }
  ],
  "weights": {
    "match_weight": 0.6,
    "interest_weight": 0.4
  },
  "top_k": 10
}
```

## Scoring Logic

Detailed formulas and architecture are in:
- `docs/architecture.md`

Summary:
- Match Score combines semantic similarity and required-skill coverage.
- Interest Score comes from conversational outreach simulation.
- Final score combines both with configurable weights.

## Sample Inputs and Outputs

- JD sample: `examples/sample_jd.json`
- Candidate sample CSV: `examples/sample_candidates.csv`
- Ranked output sample: `examples/sample_output.json`

## Netlify Deployment (Frontend)

1. Push this repository to GitHub.
2. In Netlify, import the repo.
3. Configure build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
4. Deploy.

Set Netlify environment variable for backend API:
- Key: `VITE_API_BASE_URL`
- Value: your backend URL (example: `https://your-backend.onrender.com`)

No code changes are needed for API URL switching because frontend reads `VITE_API_BASE_URL`.

## Backend Cloud Deployment

You can deploy the backend to either Render or Railway.

### Option A: Render (Blueprint)

This repo includes `render.yaml` at project root.

1. Push repo to GitHub.
2. In Render, create a new Blueprint and connect the repo.
3. Render will detect `render.yaml` and provision the web service.
4. Set environment variable in Render service:
  - Key: `ALLOWED_ORIGINS`
  - Value: your Netlify URL (example: `https://your-site.netlify.app`)
5. Deploy and copy the backend URL.

Health check URL:
- `https://<your-render-service>/health`

### Option B: Railway

This repo includes `railway.json` at project root.

1. Push repo to GitHub.
2. In Railway, create a new project from the repo.
3. Railway uses `railway.json` to build and run the backend.
4. Set environment variable in Railway service:
  - Key: `ALLOWED_ORIGINS`
  - Value: your Netlify URL (example: `https://your-site.netlify.app`)
5. Deploy and copy the backend URL.

Health check URL:
- `https://<your-railway-service>/health`

### Connect Netlify Frontend to Hosted Backend

In Netlify site settings, add environment variable:
- Key: `VITE_API_BASE_URL`
- Value: your backend public URL from Render or Railway

Then trigger a Netlify redeploy.

## Notes for Submission Requirements

- Working prototype: provided with local setup and Netlify deployment steps.
- Source code in public repo: push this project to GitHub.
- Architecture and scoring logic: provided in `docs/architecture.md`.
- Sample input/output: provided in `examples/`.
