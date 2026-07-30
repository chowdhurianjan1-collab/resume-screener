import { useRef, useState } from "react";

export default function UploadSection({
  mode, setMode,
  jd, setJd,
  resumes, setResumes, names, setNames,
  files, setFiles,
  profiles, selectedProfileId, setSelectedProfileId,
  onAnalyze, loading,
}) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const addResume = () => {
    setResumes([...resumes, ""]);
    setNames([...names, `Candidate ${names.length + 1}`]);
  };

  const handleFiles = (fileList) => {
    const incoming = Array.from(fileList).filter((f) =>
      /\.(pdf|docx|txt)$/i.test(f.name)
    );
    setFiles([...files, ...incoming]);
  };

  return (
    <>
      <div className="card">
        <div className="card-title">01 — Job Description</div>
        <textarea value={jd} onChange={(e) => setJd(e.target.value)} placeholder="Paste the job description here..." />

        {profiles.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <label className="field-label">Company skill profile (optional — customizes scoring)</label>
            <select value={selectedProfileId ?? ""} onChange={(e) => setSelectedProfileId(e.target.value ? Number(e.target.value) : null)}>
              <option value="">None — use generic skill detection</option>
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>{p.company_name} · {p.role_title}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-title">02 — Candidate Resumes</div>

        <div className="mode-toggle">
          <button className={`mode-btn${mode === "paste" ? " active" : ""}`} onClick={() => setMode("paste")}>📝 Paste Text</button>
          <button className={`mode-btn${mode === "upload" ? " active" : ""}`} onClick={() => setMode("upload")}>📄 Upload PDF/DOCX</button>
        </div>

        {mode === "paste" ? (
          <>
            <div className="resume-list">
              {resumes.map((r, i) => (
                <div key={i} className="resume-item">
                  <div><div className="resume-num">#{i + 1}</div></div>
                  <div style={{ flex: 1 }}>
                    <input
                      type="text"
                      value={names[i]}
                      onChange={(e) => { const n = [...names]; n[i] = e.target.value; setNames(n); }}
                      placeholder="Candidate name"
                      style={{ marginBottom: 8 }}
                    />
                    <textarea
                      value={r}
                      onChange={(e) => { const rs = [...resumes]; rs[i] = e.target.value; setResumes(rs); }}
                      placeholder={`Paste resume text for candidate ${i + 1}...`}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="actions">
              <button className="btn btn-ghost btn-sm" onClick={addResume}>+ Add Resume</button>
              {resumes.length > 1 && (
                <button className="btn btn-ghost btn-sm" onClick={() => { setResumes(resumes.slice(0, -1)); setNames(names.slice(0, -1)); }}>− Remove Last</button>
              )}
            </div>
          </>
        ) : (
          <>
            <div
              className={`dropzone${dragOver ? " dragover" : ""}`}
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
            >
              <div className="dz-icon">📤</div>
              <div>Drag & drop resumes here, or click to browse</div>
              <div style={{ fontSize: 11, marginTop: 6, fontFamily: "'JetBrains Mono', monospace" }}>PDF · DOCX · TXT — up to 8MB each</div>
              <input
                ref={inputRef} type="file" multiple accept=".pdf,.docx,.txt" style={{ display: "none" }}
                onChange={(e) => handleFiles(e.target.files)}
              />
            </div>
            {files.length > 0 && (
              <div className="file-list">
                {files.map((f, i) => (
                  <div key={i} className="file-chip">
                    <span className="fname">📄 {f.name} <span style={{ color: "var(--muted)" }}>({(f.size / 1024).toFixed(0)}KB)</span></span>
                    <button onClick={() => setFiles(files.filter((_, idx) => idx !== i))}>✕</button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      <div className="actions">
        <button className="btn btn-primary" onClick={onAnalyze} disabled={loading || !jd.trim()}>
          {loading ? "⏳ Analyzing..." : "🚀 Analyze Resumes"}
        </button>
      </div>
    </>
  );
}
