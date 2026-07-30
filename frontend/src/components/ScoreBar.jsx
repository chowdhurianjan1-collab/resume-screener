function barColor(s) {
  if (s >= 70) return "#10b981";
  if (s >= 45) return "#f59e0b";
  return "#ef4444";
}

export default function ScoreBar({ label, value }) {
  return (
    <div className="score-bar-wrap">
      <div className="score-bar-label">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="score-bar-bg">
        <div className="score-bar-fill" style={{ width: `${value}%`, background: barColor(value) }} />
      </div>
    </div>
  );
}
