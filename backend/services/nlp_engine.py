"""
nlp_engine.py — the actual scoring logic.

Three signals are blended into an overall score:
  1. Semantic similarity  — TF-IDF + cosine similarity between the JD and
     resume text (spaCy is used for lemmatized tokenization so "managing"
     and "management" count as the same signal).
  2. Skill overlap        — keyword/phrase matching against a skill
     taxonomy. If a company SkillProfile is supplied, weighted required +
     preferred skills from THAT company are used instead of the generic
     list, so scoring reflects what that company actually cares about.
  3. Experience bonus     — years-of-experience extracted via regex,
     compared against a company's minimum if set.

This keeps everything runnable locally with no external API key (no LLM
call), which is what makes it a genuinely free/self-hosted screener.
"""
import re
from typing import Dict, List, Optional, Tuple

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    _NLP = spacy.load("en_core_web_sm")
except OSError:  # model not downloaded yet
    _NLP = spacy.blank("en")

# Generic fallback taxonomy used when a company hasn't defined its own
# skill profile. Extend freely — this is just a sane default.
DEFAULT_SKILLS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "react", "vue", "angular", "node.js", "next.js", "django", "flask", "fastapi",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd",
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow",
    "scikit-learn", "pandas", "numpy", "spark", "airflow",
    "rest api", "graphql", "microservices", "git", "agile", "scrum",
]

YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\b", re.IGNORECASE)


def _lemmatize(text: str) -> str:
    """Lowercase + lemmatize so word forms don't hurt TF-IDF matching."""
    doc = _NLP(text)
    tokens = [t.lemma_.lower() for t in doc if not t.is_space]
    return " ".join(tokens) if tokens else text.lower()


def compute_semantic_score(jd: str, resume: str) -> float:
    """TF-IDF cosine similarity between JD and resume, scaled to 0-100."""
    jd_l, resume_l = _lemmatize(jd), _lemmatize(resume)
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf = vectorizer.fit_transform([jd_l, resume_l])
        sim = cosine_similarity(tfidf[0], tfidf[1])[0][0]
    except ValueError:
        return 0.0
    # Raw cosine similarity on short texts tends to sit low (0.1-0.4) even
    # for strong matches, so we apply a mild boost curve rather than a
    # flat linear scale — keeps the number meaningful to a human reader.
    boosted = min(1.0, sim * 1.8)
    return round(boosted * 100, 1)


def extract_years_experience(text: str) -> Optional[float]:
    matches = [float(m) for m in YEARS_RE.findall(text)]
    return max(matches) if matches else None


def extract_skills(text: str, taxonomy: List[str]) -> List[str]:
    text_l = text.lower()
    found = []
    for skill in taxonomy:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_l):
            found.append(skill)
    return found


def compute_weighted_skill_score(
    resume_text: str,
    required_skills: Dict[str, int],
    preferred_skills: Dict[str, int],
) -> Tuple[float, List[str], List[str]]:
    """Weighted skill score using a company's custom taxonomy.

    required_skills / preferred_skills: {skill_name: weight 1-3}
    Required skills count 3x as much toward the score as preferred ones.
    """
    resume_l = resume_text.lower()
    all_skills = {**{k: v * 3 for k, v in required_skills.items()},
                  **{k: v for k, v in preferred_skills.items() if k not in required_skills}}
    if not all_skills:
        return 0.0, [], []

    matched, missing = [], []
    earned, total = 0, 0
    for skill, weight in all_skills.items():
        total += weight
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, resume_l):
            matched.append(skill)
            earned += weight
        else:
            missing.append(skill)

    score = round((earned / total) * 100, 1) if total else 0.0
    return score, matched, missing


def score_candidate(
    jd: str,
    resume_text: str,
    profile: Optional[dict] = None,
) -> dict:
    """
    profile (optional): {
        "required_skills": {...}, "preferred_skills": {...},
        "min_experience_years": int
    }
    Returns a dict of all scoring signals for one candidate.
    """
    semantic = compute_semantic_score(jd, resume_text)
    years = extract_years_experience(resume_text)

    if profile and (profile.get("required_skills") or profile.get("preferred_skills")):
        skill_score, matched, missing = compute_weighted_skill_score(
            resume_text,
            profile.get("required_skills", {}),
            profile.get("preferred_skills", {}),
        )
    else:
        jd_skills = extract_skills(jd, DEFAULT_SKILLS)
        matched = extract_skills(resume_text, jd_skills) if jd_skills else []
        missing = [s for s in jd_skills if s not in matched]
        skill_score = round((len(matched) / len(jd_skills)) * 100, 1) if jd_skills else 0.0

    exp_bonus = 0.0
    min_years = (profile or {}).get("min_experience_years", 0)
    if years is not None:
        if min_years and years >= min_years:
            exp_bonus = min(10.0, (years - min_years) * 1.5 + 5)
        elif not min_years:
            exp_bonus = min(10.0, years * 1.2)

    overall = round(min(98.0, semantic * 0.45 + skill_score * 0.45 + exp_bonus), 1)

    return {
        "overall_score": overall,
        "semantic_score": semantic,
        "skill_score": skill_score,
        "experience_years": years,
        "matched_skills": matched,
        "missing_skills": missing,
    }


def build_summary(name: str, result: dict) -> str:
    score = result["overall_score"]
    tier = "a strong" if score >= 70 else "a moderate" if score >= 45 else "a weak"
    years = result["experience_years"]
    exp_txt = f" with {years:.0f}+ years of relevant experience" if years else ""
    matched_n = len(result["matched_skills"])
    missing_n = len(result["missing_skills"])
    return (
        f"{name} is {tier} match ({score}%){exp_txt}. "
        f"Matched {matched_n} required skill(s); missing {missing_n}."
    )
