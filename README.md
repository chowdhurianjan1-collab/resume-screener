# AI Resume Screener

A full-stack resume screening tool: upload PDF/DOCX resumes (or paste text),
score candidates against a job description with NLP, and customize the
skill taxonomy per company/role so scoring reflects what *that* company
actually cares about.

## What it does

- **Scans real files.** Upload PDF/DOCX/TXT resumes — text, email, and phone
  are extracted automatically (PyMuPDF + python-docx).
- **Scores with NLP, not just keyword matching.** TF-IDF + cosine similarity
  (with spaCy lemmatization) for semantic fit, plus weighted skill overlap.
- **Company-customized skills.** Define required vs. preferred skills (each
  weighted 1–3) per company and role in the "Company Skills" tab — no more
  one-size-fits-all keyword list.
- **History.** Every analysis run is saved (SQLite by default) so you can
  revisit past screenings.

## Project structure

```
resume-screener/
├── backend/                  FastAPI app
│   ├── main.py                Entrypoint, CORS, router registration
│   ├── database.py            SQLAlchemy engine/session (SQLite by default)
│   ├── models/
│   │   ├── db_models.py       SkillProfile, AnalysisRun, CandidateResult
│   │   └── schemas.py         Pydantic request/response models
│   ├── routes/
│   │   ├── analyze.py         POST /api/analyze (pasted text)
│   │   ├── upload.py          POST /api/upload-analyze (PDF/DOCX/TXT)
│   │   ├── skills.py          CRUD /api/skill-profiles
│   │   └── history.py         GET /api/history
│   ├── services/
│   │   ├── pdf_extractor.py   Text/email/phone extraction from files
│   │   └── nlp_engine.py      Scoring logic (semantic + skill + experience)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 React (Vite) app
│   └── src/
│       ├── App.jsx
│       ├── api/client.js      Axios wrapper for the backend
│       └── components/        UploadSection, ResultCard, CompanyProfiles, History
└── docker-compose.yml
```

## Quick start (local, no Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
uvicorn main:app --reload
```
Backend runs at `http://localhost:8000` (interactive docs at `/docs`).

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Frontend runs at `http://localhost:5173`.

## Quick start (Docker)

```bash
docker-compose up --build
```
Frontend: `http://localhost:3000` · Backend: `http://localhost:8000`

## Customizing skills per company

1. Open the **Company Skills** tab.
2. Enter a company name and role title.
3. Add required skills (weighted 3x in scoring) and preferred skills
   (nice-to-have), each on a 1–3 importance scale.
4. Save. On the **Analyzer** tab, pick that profile from the dropdown
   before analyzing — scoring will use the company's exact taxonomy
   instead of the generic keyword list.

## API reference (once backend is running)

Full interactive docs: `http://localhost:8000/docs`

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/analyze` | Score pasted resume text against a JD |
| POST | `/api/upload-analyze` | Upload PDF/DOCX/TXT resumes, scan + score |
| POST | `/api/skill-profiles` | Create a company skill profile |
| GET | `/api/skill-profiles` | List saved profiles |
| PUT/DELETE | `/api/skill-profiles/{id}` | Update / delete a profile |
| GET | `/api/history` | List past analysis runs |
| GET | `/api/history/{id}` | View one past run in full |

## Deploying (Render + Vercel)

**Backend → Render**
1. New Web Service → connect your repo → root directory `backend` (or use the
   included `render.yaml` for one-click config).
2. Render's Docker runtime auto-injects `$PORT`; the Dockerfile already binds
   to it (`CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`), so no
   changes needed there.
3. In the service's **Environment** tab, set `ALLOWED_ORIGINS` to your
   Vercel URL, e.g. `https://your-frontend.vercel.app`. (`*.vercel.app` is
   also allowed automatically as a fallback in `main.py`, but set this too.)
4. Deploy, then sanity-check `https://<your-backend>.onrender.com/health`
   directly in a browser — should return `{"status":"ok"}`.
   Free-tier Render services sleep after inactivity; the first request after
   sleeping can take 30–60s.

**Frontend → Vercel**
1. New Project → import repo → root directory `frontend`.
2. **Settings → Environment Variables** → add
   `VITE_API_URL=https://<your-backend>.onrender.com` (no trailing slash).
   Vite bakes this in at build time — a `.env` file alone won't affect an
   already-deployed site, and changing this variable requires a redeploy.
3. Deploy. Test with browser DevTools → Network tab open; a failed request
   there will show you whether it's hitting the right URL and what the
   actual error is (CORS vs. 404 vs. timeout).

## Notes

- No LLM API key required — scoring runs locally via spaCy + scikit-learn.
- Default DB is SQLite (zero setup). Set `DATABASE_URL` to point at
  Postgres/MySQL in production.
- Deploy target suggestions: backend → Render/Railway/Fly.io, frontend →
  Vercel/Netlify, DB → Supabase/managed Postgres.
