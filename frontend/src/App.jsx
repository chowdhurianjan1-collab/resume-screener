import { useEffect, useState } from "react";
import "./index.css";
import UploadSection from "./components/UploadSection.jsx";
import ResultCard from "./components/ResultCard.jsx";
import CompanyProfiles from "./components/CompanyProfiles.jsx";
import History from "./components/History.jsx";
import { analyzeText, analyzeUpload, listProfiles } from "./api/client.js";

const DEMO_JD = `We are looking for a Python Backend Developer with experience in FastAPI, PostgreSQL, and Docker. Knowledge of machine learning and NLP is a plus. The candidate should have 2+ years of experience building REST APIs and be comfortable with cloud deployment on AWS.`;

const DEMO_RESUMES = [
  { name: "Priya Sharma", text: "Experienced Python developer with 3 years of experience. Built REST APIs using FastAPI and Django. Worked with PostgreSQL and Redis. Deployed applications on AWS using Docker and Kubernetes. Strong knowledge of NLP using spaCy and scikit-learn. Also worked with React for frontend tasks." },
  { name: "Rahul Verma", text: "Java developer with 2 years experience. Worked on Spring Boot microservices. Basic knowledge of Python and Flask. Some experience with MySQL databases. Built simple REST APIs. Currently learning Docker and cloud platforms." },
];

export default function App() {
  const [tab, setTab] = useState("analyzer");

  // Analyzer state
  const [mode, setMode] = useState("paste"); // "paste" | "upload"
  const [jd, setJd] = useState(DEMO_JD);
  const [resumes, setResumes] = useState(DEMO_RESUMES.map((r) => r.text));
  const [names, setNames] = useState(DEMO_RESUMES.map((r) => r.name));
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [jdSkills, setJdSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Company profiles
  const [profiles, setProfiles] = useState([]);
  const [selectedProfileId, setSelectedProfileId] = useState(null);

  const refreshProfiles = async () => {
    try {
      setProfiles(await listProfiles());
    } catch {
      // backend may not be running yet — analyzer still degrades gracefully
    }
  };

  useEffect(() => { refreshProfiles(); }, []);

  const analyze = async () => {
    if (!jd.trim()) return;
    setError("");
    setLoading(true);
    setResults(null);
    try {
      let data;
      if (mode === "paste") {
        const nonEmpty = resumes.filter((r) => r.trim());
        if (nonEmpty.length === 0) { setError("Add at least one resume."); setLoading(false); return; }
        data = await analyzeText({
          job_description: jd,
          resumes,
          names,
          profile_id: selectedProfileId,
        });
      } else {
        if (files.length === 0) { setError("Upload at least one resume file."); setLoading(false); return; }
        const form = new FormData();
        form.append("job_description", jd);
        if (selectedProfileId) form.append("profile_id", selectedProfileId);
        files.forEach((f) => form.append("files", f));
        data = await analyzeUpload(form);
      }
      setResults(data.results);
      setJdSkills(data.jd_skills_detected || []);
    } catch (e) {
      setError(e?.response?.data?.detail || "Analysis failed. Is the backend running on the expected port?");
    } finally {
      setLoading(false);
    }
  };

  const resetDemo = () => {
    setJd(DEMO_JD);
    setResumes(DEMO_RESUMES.map((r) => r.text));
    setNames(DEMO_RESUMES.map((r) => r.name));
    setFiles([]);
    setResults(null);
    setError("");
  };

  return (
    <div className="app">
      <div className="header">
        <div className="header-badge">AI × NLP × Full Stack</div>
        <h1>AI Resume Screener</h1>
        <p>Upload real resumes (PDF/DOCX) or paste text, score them against a job description, and customize the skill taxonomy per company.</p>
      </div>

      <div className="tabs">
        {[["analyzer", "🔍 Analyzer"], ["profiles", "🏢 Company Skills"], ["history", "🗂️ History"]].map(([id, label]) => (
          <button key={id} className={`tab${tab === id ? " active" : ""}`} onClick={() => setTab(id)}>{label}</button>
        ))}
      </div>

      {tab === "analyzer" && (
        <>
          <UploadSection
            mode={mode} setMode={setMode}
            jd={jd} setJd={setJd}
            resumes={resumes} setResumes={setResumes}
            names={names} setNames={setNames}
            files={files} setFiles={setFiles}
            profiles={profiles}
            selectedProfileId={selectedProfileId} setSelectedProfileId={setSelectedProfileId}
            onAnalyze={analyze} loading={loading}
          />

          <div className="actions" style={{ marginTop: -10, marginBottom: 20 }}>
            <button className="btn btn-ghost btn-sm" onClick={resetDemo}>↺ Reset Demo Data</button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <div>
            {loading && (
              <div className="loading-wrap">
                <div className="spinner" />
                <div className="loading-text">Scanning resumes & running NLP scoring...</div>
              </div>
            )}

            {results && !loading && (
              <>
                <div className="results-header">
                  <div className="results-title">📊 Results</div>
                  <div className="results-meta">{results.length} candidate(s) ranked · {jdSkills.length} skill(s) tracked</div>
                </div>
                {results.map((r, i) => <ResultCard key={i} result={r} rank={i + 1} />)}
              </>
            )}

            {!results && !loading && (
              <div className="empty">
                <div className="empty-icon">🎯</div>
                <h3>Ready to analyze</h3>
                <p>Fill in the job description above, add resumes (paste or upload), then click Analyze.</p>
              </div>
            )}
          </div>
        </>
      )}

      {tab === "profiles" && <CompanyProfiles profiles={profiles} refreshProfiles={refreshProfiles} />}

      {tab === "history" && <History />}
    </div>
  );
}
