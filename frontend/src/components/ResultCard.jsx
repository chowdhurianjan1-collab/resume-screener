import ScoreBar from "./ScoreBar.jsx";

function scoreClass(s) {
  if (s >= 70) return "score-high";
  if (s >= 45) return "score-mid";
  return "score-low";
}

export default function ResultCard({ result, rank }) {
  const rankClass = rank === 1 ? "rank-1" : rank === 2 ? "rank-2" : "rank-other";
  const badge = rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank;

  return (
    <div className={`result-card ${rankClass}`}>
      <div className="result-top">
        <div className="rank-badge">{badge}</div>
        <div style={{ flex: 1 }}>
          <div className="result-name">{result.name}</div>
          <div className="result-sub">
            {result.source_filename ? `${result.source_filename} · ` : ""}
            {result.matched_skills.length} skills matched · {result.missing_skills.length} missing
            {result.experience_years ? ` · ~${result.experience_years}y experience` : ""}
          </div>
          {(result.extracted_email || result.extracted_phone) && (
            <div className="contact-row">
              {result.extracted_email && <span>✉ {result.extracted_email}</span>}
              {result.extracted_phone && <span>☎ {result.extracted_phone}</span>}
            </div>
          )}
        </div>
        <div className={`score-pill ${scoreClass(result.overall_score)}`}>{result.overall_score}%</div>
      </div>

      <div className="grid2">
        <ScoreBar label="Overall Match" value={result.overall_score} />
        <ScoreBar label="Semantic Score" value={result.semantic_score} />
        <ScoreBar label="Skill Overlap" value={result.skill_score} />
      </div>

      <div className="skills-wrap">
        {result.matched_skills.map((s) => (
          <span key={`m-${s}`} className="skill-tag skill-match">✓ {s}</span>
        ))}
        {result.missing_skills.map((s) => (
          <span key={`x-${s}`} className="skill-tag skill-miss">✗ {s}</span>
        ))}
      </div>

      {result.summary && <div className="summary-box">{result.summary}</div>}
    </div>
  );
}
