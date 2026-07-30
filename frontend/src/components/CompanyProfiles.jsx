import { useState } from "react";
import { createProfile, deleteProfile } from "../api/client.js";

function SkillEditor({ label, skills, setSkills }) {
  const [name, setName] = useState("");
  const [weight, setWeight] = useState(2);

  const add = () => {
    if (!name.trim()) return;
    setSkills({ ...skills, [name.trim().toLowerCase()]: Number(weight) });
    setName("");
  };
  const remove = (key) => {
    const next = { ...skills };
    delete next[key];
    setSkills(next);
  };

  return (
    <div style={{ marginBottom: 18 }}>
      <label className="field-label">{label}</label>
      <div className="skill-chip-input">
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. kubernetes" onKeyDown={(e) => e.key === "Enter" && add()} />
        <select value={weight} onChange={(e) => setWeight(e.target.value)} style={{ width: 120 }}>
          <option value={1}>Weight 1</option>
          <option value={2}>Weight 2</option>
          <option value={3}>Weight 3</option>
        </select>
        <button className="btn btn-ghost btn-sm" onClick={add}>+ Add</button>
      </div>
      <div className="skills-wrap">
        {Object.entries(skills).map(([k, w]) => (
          <span key={k} className="skill-tag skill-match">
            {k} <span className="weight-badge">w{w}</span>{" "}
            <span style={{ cursor: "pointer", color: "var(--danger)" }} onClick={() => remove(k)}>✕</span>
          </span>
        ))}
      </div>
    </div>
  );
}

export default function CompanyProfiles({ profiles, refreshProfiles }) {
  const [companyName, setCompanyName] = useState("");
  const [roleTitle, setRoleTitle] = useState("");
  const [required, setRequired] = useState({});
  const [preferred, setPreferred] = useState({});
  const [minYears, setMinYears] = useState(0);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const save = async () => {
    if (!companyName.trim() || !roleTitle.trim()) {
      setError("Company name and role title are required.");
      return;
    }
    setError("");
    setSaving(true);
    try {
      await createProfile({
        company_name: companyName,
        role_title: roleTitle,
        required_skills: required,
        preferred_skills: preferred,
        min_experience_years: Number(minYears) || 0,
        notes,
      });
      setCompanyName(""); setRoleTitle(""); setRequired({}); setPreferred({}); setMinYears(0); setNotes("");
      await refreshProfiles();
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to save profile.");
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id) => {
    await deleteProfile(id);
    await refreshProfiles();
  };

  return (
    <>
      <div className="alert">🏢 Define what "good candidate" means for each company &amp; role. Saved profiles show up as a scoring option on the Analyzer tab.</div>

      <div className="card">
        <div className="card-title">New Skill Profile</div>
        <div className="grid2">
          <div>
            <label className="field-label">Company name</label>
            <input type="text" value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="e.g. Acme Corp" style={{ marginBottom: 14 }} />
          </div>
          <div>
            <label className="field-label">Role title</label>
            <input type="text" value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} placeholder="e.g. Backend Engineer" style={{ marginBottom: 14 }} />
          </div>
        </div>

        <SkillEditor label="Required skills (weighted 3x)" skills={required} setSkills={setRequired} />
        <SkillEditor label="Preferred skills (nice-to-have)" skills={preferred} setSkills={setPreferred} />

        <label className="field-label">Minimum experience (years)</label>
        <input type="number" min="0" value={minYears} onChange={(e) => setMinYears(e.target.value)} style={{ marginBottom: 14, width: 140 }} />

        <label className="field-label">Notes (context only, shown to reviewers)</label>
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="e.g. Prefers candidates with fintech or regulated-industry background." style={{ minHeight: 70 }} />

        {error && <div className="alert alert-error" style={{ marginTop: 14 }}>{error}</div>}

        <div className="actions">
          <button className="btn btn-primary" onClick={save} disabled={saving}>{saving ? "Saving..." : "💾 Save Profile"}</button>
        </div>
      </div>

      <div className="card-title" style={{ marginTop: 8 }}>Saved Profiles ({profiles.length})</div>
      {profiles.length === 0 && (
        <div className="empty"><div className="empty-icon">🏢</div><h3>No profiles yet</h3><p>Create one above to customize scoring per company.</p></div>
      )}
      {profiles.map((p) => (
        <div className="card profile-card" key={p.id}>
          <div>
            <h4>{p.company_name} — {p.role_title}</h4>
            <div className="profile-sub">
              {Object.keys(p.required_skills).length} required · {Object.keys(p.preferred_skills).length} preferred
              {p.min_experience_years ? ` · min ${p.min_experience_years}y exp` : ""}
            </div>
            <div className="skills-wrap">
              {Object.entries(p.required_skills).map(([k, w]) => <span key={k} className="skill-tag skill-match">{k} <span className="weight-badge">w{w}</span></span>)}
              {Object.entries(p.preferred_skills).map(([k, w]) => <span key={k} className="skill-tag" style={{ color: "var(--accent2)", borderColor: "rgba(6,182,212,0.3)" }}>{k} <span className="weight-badge">w{w}</span></span>)}
            </div>
          </div>
          <button className="btn btn-danger btn-sm" onClick={() => remove(p.id)}>Delete</button>
        </div>
      ))}
    </>
  );
}
