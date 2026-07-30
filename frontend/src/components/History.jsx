import { useEffect, useState } from "react";
import { listHistory, getHistoryRun } from "../api/client.js";
import ResultCard from "./ResultCard.jsx";

export default function History() {
  const [runs, setRuns] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listHistory().then(setRuns).finally(() => setLoading(false));
  }, []);

  const openRun = async (id) => {
    const data = await getHistoryRun(id);
    setSelected(data);
  };

  if (selected) {
    return (
      <>
        <button className="btn btn-ghost btn-sm" onClick={() => setSelected(null)} style={{ marginBottom: 16 }}>← Back to history</button>
        <div className="card">
          <div className="card-title">Job Description</div>
          <p style={{ fontSize: 13, lineHeight: 1.7, color: "var(--muted)" }}>{selected.job_description}</p>
        </div>
        {selected.results.map((r, i) => (
          <ResultCard key={i} result={{ ...r, summary: "" }} rank={i + 1} />
        ))}
      </>
    );
  }

  if (loading) return <div className="loading-wrap"><div className="spinner" /><div className="loading-text">Loading history...</div></div>;

  if (runs.length === 0) {
    return <div className="empty"><div className="empty-icon">🗂️</div><h3>No runs yet</h3><p>Analyze some resumes and they'll show up here.</p></div>;
  }

  return (
    <div className="card">
      <div className="card-title">Past Analysis Runs</div>
      {runs.map((run) => (
        <div key={run.id} className="history-row" onClick={() => openRun(run.id)}>
          <div>
            <div style={{ fontWeight: 700 }}>Run #{run.id} · {run.candidate_count} candidate(s)</div>
            <div className="results-meta">{new Date(run.created_at).toLocaleString()}</div>
          </div>
          {run.top_candidate && (
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 13 }}>{run.top_candidate}</div>
              <div className="results-meta">top score: {run.top_score}%</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
