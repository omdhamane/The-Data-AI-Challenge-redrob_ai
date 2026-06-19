#!/usr/bin/env python3
"""CPU-only Redrob candidate ranker.

The scorer is intentionally deterministic and dependency-free so the exact
submission can be reproduced in the challenge sandbox with no network access.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


REFERENCE_DATE = date(2026, 6, 1)

SERVICE_COMPANIES = {
    "TCS",
    "Infosys",
    "Wipro",
    "Accenture",
    "Cognizant",
    "Capgemini",
    "HCL",
    "Tech Mahindra",
    "Mindtree",
    "Mphasis",
}

PRODUCT_COMPANIES = {
    "Zomato",
    "Swiggy",
    "Razorpay",
    "CRED",
    "Flipkart",
    "Meesho",
    "Nykaa",
    "Zoho",
    "Freshworks",
    "Ola",
    "Paytm",
    "PhonePe",
    "Dream11",
    "PolicyBazaar",
    "PharmEasy",
    "InMobi",
    "Glance",
    "Haptik",
    "Wysa",
    "Observe.AI",
    "Yellow.ai",
    "Verloop.io",
    "Saarthi.ai",
    "Niramai",
    "Sarvam AI",
    "Krutrim",
    "Aganitha",
    "Mad Street Den",
    "Rephrase.ai",
    "Locobuzz",
    "Google",
    "Meta",
    "Amazon",
    "Microsoft",
    "Netflix",
    "Apple",
    "Adobe",
    "Salesforce",
    "LinkedIn",
    "Uber",
}

AI_PRODUCT_INDUSTRIES = {
    "Software",
    "SaaS",
    "Fintech",
    "E-commerce",
    "Food Delivery",
    "Gaming",
    "AI/ML",
    "Conversational AI",
    "HealthTech AI",
    "AdTech",
    "Voice AI",
    "Transportation",
    "Insurance Tech",
    "Internet",
}

FOUNDED_YEAR = {
    "Swiggy": 2014,
    "CRED": 2018,
    "Razorpay": 2014,
    "Zomato": 2008,
    "Flipkart": 2007,
    "Meesho": 2015,
    "Nykaa": 2012,
    "Freshworks": 2010,
    "Ola": 2010,
    "Paytm": 2010,
    "PhonePe": 2015,
    "Dream11": 2008,
    "PolicyBazaar": 2008,
    "PharmEasy": 2015,
    "InMobi": 2007,
    "Haptik": 2013,
    "Wysa": 2015,
    "Observe.AI": 2017,
    "Yellow.ai": 2016,
    "Verloop.io": 2015,
    "Saarthi.ai": 2017,
    "Niramai": 2016,
    "Sarvam AI": 2023,
    "Krutrim": 2023,
    "Aganitha": 2000,
    "Mad Street Den": 2016,
    "Rephrase.ai": 2018,
    "Locobuzz": 2015,
    "Zoho": 1996,
    "BYJU'S": 2011,
    "upGrad": 2015,
    "Unacademy": 2015,
    "Vedantu": 2011,
}

TARGET_LOCATIONS = {
    "Pune": 1.0,
    "Noida": 1.0,
    "Gurgaon": 0.92,
    "Delhi": 0.9,
    "Bangalore": 0.9,
    "Mumbai": 0.85,
    "Hyderabad": 0.82,
    "Chennai": 0.74,
    "Coimbatore": 0.68,
    "Kochi": 0.65,
    "Trivandrum": 0.63,
    "Chandigarh": 0.62,
    "Jaipur": 0.55,
    "Ahmedabad": 0.55,
    "Indore": 0.55,
    "Kolkata": 0.5,
    "Bhubaneswar": 0.48,
    "Vizag": 0.48,
}

TITLE_WEIGHTS = {
    "Senior AI Engineer": 1.00,
    "Lead AI Engineer": 1.00,
    "Staff Machine Learning Engineer": 0.98,
    "Senior Machine Learning Engineer": 0.97,
    "Recommendation Systems Engineer": 0.96,
    "Search Engineer": 0.95,
    "Applied ML Engineer": 0.93,
    "Machine Learning Engineer": 0.90,
    "NLP Engineer": 0.88,
    "Senior NLP Engineer": 0.94,
    "AI Engineer": 0.86,
    "Senior Applied Scientist": 0.86,
    "Senior ML Engineer \u2014 Search & Ranking": 0.96,
    "Senior Software Engineer (ML)": 0.74,
    "ML Engineer": 0.72,
    "Data Scientist": 0.58,
    "Senior Data Scientist": 0.66,
    "AI Research Engineer": 0.45,
    "AI Specialist": 0.42,
    "Data Engineer": 0.32,
    "Senior Data Engineer": 0.36,
    "Analytics Engineer": 0.30,
    "Backend Engineer": 0.28,
    "Software Engineer": 0.24,
    "Full Stack Developer": 0.22,
    "Cloud Engineer": 0.20,
    "DevOps Engineer": 0.18,
}

SKILL_WEIGHTS = {
    "Information Retrieval": 2.5,
    "Information Retrieval Systems": 2.7,
    "Ranking Systems": 2.6,
    "Learning to Rank": 2.5,
    "Recommendation Systems": 2.3,
    "Search & Discovery": 2.3,
    "Search Infrastructure": 2.2,
    "Search Backend": 2.1,
    "Semantic Search": 2.2,
    "Vector Search": 2.1,
    "Vector Representations": 2.0,
    "Embeddings": 2.0,
    "Text Encoders": 1.9,
    "Content Matching": 1.9,
    "Indexing Algorithms": 1.8,
    "Sentence Transformers": 1.9,
    "BM25": 1.8,
    "FAISS": 1.8,
    "Qdrant": 1.7,
    "Milvus": 1.6,
    "Weaviate": 1.6,
    "Pinecone": 1.6,
    "OpenSearch": 1.5,
    "Elasticsearch": 1.5,
    "RAG": 1.4,
    "NLP": 1.3,
    "Natural Language Processing": 1.3,
    "Python": 1.3,
    "Machine Learning": 1.2,
    "MLOps": 1.1,
    "MLflow": 1.0,
    "Kubeflow": 1.0,
    "PyTorch": 0.9,
    "TensorFlow": 0.8,
    "Fine-tuning LLMs": 0.8,
    "LoRA": 0.7,
    "QLoRA": 0.7,
    "PEFT": 0.7,
    "Hugging Face Transformers": 0.7,
    "LLMs": 0.6,
    "Feature Engineering": 0.6,
    "Workflow Orchestration": 0.55,
    "Open-source ML libraries": 0.45,
    "scikit-learn": 0.6,
    "Data Science": 0.5,
    "LangChain": 0.15,
    "Prompt Engineering": 0.1,
}

PROFICIENCY_MULT = {
    "beginner": 0.35,
    "intermediate": 0.65,
    "advanced": 0.9,
    "expert": 1.15,
}

TEXT_PATTERNS = {
    "ranking": 2.8,
    "ranking layer": 3.0,
    "ranking systems": 2.8,
    "ranking calibration": 2.4,
    "learning-to-rank": 2.8,
    "ranker": 2.2,
    "retrieval": 2.6,
    "hybrid retrieval": 2.8,
    "search and discovery": 2.7,
    "search & discovery": 2.7,
    "search backend": 2.2,
    "search infrastructure": 2.2,
    "semantic search": 2.5,
    "vector search": 2.3,
    "vector representations": 2.0,
    "embedding": 2.0,
    "text encoder": 1.8,
    "content matching": 1.8,
    "recommendation system": 2.3,
    "recommender": 2.1,
    "search product": 2.0,
    "connect users with relevant": 2.7,
    "surface relevant": 2.5,
    "what to show": 2.2,
    "matching layer": 2.4,
    "relevant results": 2.1,
    "relevance": 1.3,
    "index refresh": 2.1,
    "query understanding": 1.9,
    "bm25": 1.8,
    "dense": 1.2,
    "faiss": 1.6,
    "qdrant": 1.4,
    "milvus": 1.3,
    "weaviate": 1.3,
    "opensearch": 1.2,
    "elasticsearch": 1.2,
    "ndcg": 2.0,
    "mrr": 1.6,
    "map": 0.9,
    "a/b test": 1.5,
    "human judgments": 1.5,
    "labeling pipeline": 1.5,
    "offline benchmark": 1.5,
    "offline metrics": 1.5,
    "online engagement": 1.5,
    "offline-online": 1.7,
    "evaluation": 1.3,
    "drift detection": 1.2,
    "retraining cadence": 1.2,
    "feature monitoring": 1.1,
    "production": 1.2,
    "shipped": 1.2,
    "serving": 1.1,
    "real users": 1.2,
    "recruiter": 1.1,
    "candidate": 0.8,
    "llm": 0.7,
    "fine-tuned": 0.7,
    "lora": 0.5,
    "rag": 1.2,
}

NEGATIVE_PATTERNS = {
    "pure research": 1.4,
    "academic lab": 1.0,
    "research-only": 1.4,
    "tutorial": 0.8,
    "prompt engineering": 0.45,
    "langchain": 0.35,
    "computer vision": 0.7,
    "image moderation": 0.35,
    "speech recognition": 0.55,
    "robotics": 0.9,
    "marketing manager": 1.0,
    "graphic designer": 1.0,
    "sales executive": 1.0,
    "accountant": 1.0,
}


@dataclass
class CandidateScore:
    candidate_id: str
    score: float
    reasoning: str
    components: dict[str, float]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def open_records(path: Path) -> Iterable[dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def record_text(record: dict[str, Any]) -> str:
    profile = record["profile"]
    parts = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_industry", ""),
    ]
    for job in record.get("career_history", []):
        parts.extend(
            [
                job.get("title", ""),
                job.get("company", ""),
                job.get("industry", ""),
                job.get("description", ""),
            ]
        )
    for cert in record.get("certifications", []):
        parts.append(cert.get("name", ""))
    return " ".join(parts).lower()


def exp_score(years: float) -> float:
    if years < 3.5:
        return clamp(years / 5.0) * 0.55
    if years < 5:
        return 0.65 + (years - 3.5) * 0.16
    if years <= 9:
        return 1.0
    if years <= 11:
        return 0.85
    if years <= 14:
        return 0.55
    return 0.35


def location_score(profile: dict[str, Any], signals: dict[str, Any]) -> float:
    loc = profile.get("location", "")
    country = profile.get("country", "")
    best = 0.0
    for key, score in TARGET_LOCATIONS.items():
        if key.lower() in loc.lower():
            best = max(best, score)
    if not best and country == "India":
        best = 0.45
    if not best:
        best = 0.15
    if signals.get("willing_to_relocate"):
        best = max(best, 0.78 if country == "India" else 0.45)
    return clamp(best)


def skill_score(skills: list[dict[str, Any]]) -> tuple[float, list[str], int]:
    weighted = 0.0
    matched: list[tuple[float, str]] = []
    suspicious = 0
    for skill in skills:
        name = skill.get("name", "")
        base = SKILL_WEIGHTS.get(name, 0.0)
        if not base:
            continue
        duration = float(skill.get("duration_months") or 0)
        endorsements = float(skill.get("endorsements") or 0)
        prof = PROFICIENCY_MULT.get(skill.get("proficiency", ""), 0.5)
        trust = 0.55 + 0.30 * clamp(duration / 48.0) + 0.15 * clamp(math.log1p(endorsements) / math.log(80))
        contribution = base * prof * trust
        weighted += contribution
        matched.append((contribution, name))
        if skill.get("proficiency") in {"advanced", "expert"} and duration < 3:
            suspicious += 1
    matched.sort(reverse=True)
    return clamp(weighted / 13.5), [name for _, name in matched[:5]], suspicious


def text_score(text: str) -> tuple[float, float, list[str]]:
    pos = 0.0
    hits: list[tuple[float, str]] = []
    for phrase, weight in TEXT_PATTERNS.items():
        count = text.count(phrase)
        if count:
            gain = weight * min(2.0, 1.0 + 0.35 * (count - 1))
            pos += gain
            hits.append((gain, phrase))
    neg = 0.0
    for phrase, weight in NEGATIVE_PATTERNS.items():
        if phrase in text:
            neg += weight
    hits.sort(reverse=True)
    return clamp(pos / 18.0), clamp(neg / 5.0), [phrase for _, phrase in hits[:4]]


def career_score(record: dict[str, Any]) -> tuple[float, float]:
    profile = record["profile"]
    jobs = record.get("career_history", [])
    relevant_title_months = 0
    product_months = 0
    service_months = 0
    short_jobs = 0
    for job in jobs:
        months = int(job.get("duration_months") or 0)
        title = job.get("title", "")
        if TITLE_WEIGHTS.get(title, 0) >= 0.58:
            relevant_title_months += months
        if job.get("company") in PRODUCT_COMPANIES or job.get("industry") in AI_PRODUCT_INDUSTRIES:
            product_months += months
        if job.get("company") in SERVICE_COMPANIES or job.get("industry") in {"IT Services", "Consulting"}:
            service_months += months
        if months and months < 18:
            short_jobs += 1
    total_months = max(1, sum(int(j.get("duration_months") or 0) for j in jobs))
    relevant = clamp(relevant_title_months / max(24, total_months * 0.75))
    product = clamp(product_months / max(24, total_months * 0.65))
    service_only_penalty = 0.0
    if service_months / total_months > 0.85 and product_months < 18:
        service_only_penalty = 0.22
    if profile.get("current_company") in SERVICE_COMPANIES and product_months < 24:
        service_only_penalty = max(service_only_penalty, 0.12)
    job_hop_penalty = 0.05 * max(0, short_jobs - 1)
    score = clamp(0.55 * relevant + 0.45 * product - service_only_penalty - job_hop_penalty)
    return score, service_only_penalty + job_hop_penalty


def behavior_score(signals: dict[str, Any]) -> tuple[float, list[str]]:
    last_active = parse_date(signals.get("last_active_date"))
    days_inactive = 365 if last_active is None else max(0, (REFERENCE_DATE - last_active).days)
    recency = math.exp(-days_inactive / 95.0)
    response_rate = float(signals.get("recruiter_response_rate") or 0)
    response_time = float(signals.get("avg_response_time_hours") or 999)
    response_speed = math.exp(-response_time / 96.0)
    notice = int(signals.get("notice_period_days") or 180)
    notice_fit = 1.0 if notice <= 30 else 0.78 if notice <= 60 else 0.48 if notice <= 90 else 0.2
    github = float(signals.get("github_activity_score", -1))
    github_fit = 0.45 if github < 0 else clamp(github / 100)
    offer = float(signals.get("offer_acceptance_rate", -1))
    offer_fit = 0.55 if offer < 0 else offer
    interview = float(signals.get("interview_completion_rate") or 0)
    completeness = float(signals.get("profile_completeness_score") or 0) / 100.0
    saved = clamp(float(signals.get("saved_by_recruiters_30d") or 0) / 18)
    verification = (
        0.4 * bool(signals.get("verified_email"))
        + 0.35 * bool(signals.get("verified_phone"))
        + 0.25 * bool(signals.get("linkedin_connected"))
    )
    score = (
        0.18 * recency
        + 0.18 * response_rate
        + 0.08 * response_speed
        + 0.13 * notice_fit
        + 0.14 * github_fit
        + 0.10 * interview
        + 0.08 * offer_fit
        + 0.05 * completeness
        + 0.03 * saved
        + 0.03 * verification
    )
    notes = []
    if days_inactive <= 30:
        notes.append("recently active")
    if response_rate >= 0.7:
        notes.append("high recruiter response")
    if notice <= 30:
        notes.append("short notice")
    if github >= 70:
        notes.append("strong GitHub activity")
    return clamp(score), notes


def availability_penalty(signals: dict[str, Any]) -> float:
    last_active = parse_date(signals.get("last_active_date"))
    days_inactive = 365 if last_active is None else max(0, (REFERENCE_DATE - last_active).days)
    response_rate = float(signals.get("recruiter_response_rate") or 0)
    response_time = float(signals.get("avg_response_time_hours") or 999)
    penalty = 0.0
    if not signals.get("open_to_work_flag"):
        penalty += 0.035
    if days_inactive > 180:
        penalty += 0.07
    elif days_inactive > 120:
        penalty += 0.045
    if response_rate < 0.10:
        penalty += 0.075
    elif response_rate < 0.20:
        penalty += 0.045
    if response_time > 144:
        penalty += 0.03
    return clamp(penalty, 0.0, 0.16)


def consistency_penalty(record: dict[str, Any], suspicious_skill_count: int) -> tuple[float, list[str]]:
    profile = record["profile"]
    signals = record["redrob_signals"]
    penalties = 0.0
    flags: list[str] = []

    if suspicious_skill_count >= 6:
        penalties += 0.4
        flags.append("many unsupported advanced skills")
    elif suspicious_skill_count >= 3:
        penalties += 0.18
        flags.append("some unsupported advanced skills")

    career_months = sum(int(job.get("duration_months") or 0) for job in record.get("career_history", []))
    years = float(profile.get("years_of_experience") or 0)
    if career_months and abs(years - career_months / 12.0) > 3.0:
        penalties += 0.18
        flags.append("experience total mismatch")

    signup = parse_date(signals.get("signup_date"))
    last_active = parse_date(signals.get("last_active_date"))
    if signup and last_active and last_active < signup:
        penalties += 0.35
        flags.append("activity date inconsistency")

    for edu in record.get("education", []):
        if int(edu.get("start_year") or 0) > int(edu.get("end_year") or 0):
            penalties += 0.25
            flags.append("education date inconsistency")
            break

    for job in record.get("career_history", []):
        start = parse_date(job.get("start_date"))
        end = parse_date(job.get("end_date"))
        if end and start and end < start:
            penalties += 0.3
            flags.append("career date inconsistency")
        founded = FOUNDED_YEAR.get(job.get("company"))
        if founded and start and start.year < founded:
            penalties += 0.45
            flags.append("job predates company founding")

    return clamp(penalties, 0.0, 0.9), flags[:3]


def title_score(title: str) -> float:
    return TITLE_WEIGHTS.get(title, 0.0)


def score_candidate(record: dict[str, Any]) -> CandidateScore:
    profile = record["profile"]
    signals = record["redrob_signals"]
    text = record_text(record)

    skills_fit, top_skills, suspicious_skill_count = skill_score(record.get("skills", []))
    jd_text_fit, neg_text, text_hits = text_score(text)
    career_fit, career_penalty = career_score(record)
    behavior_fit, behavior_notes = behavior_score(signals)
    loc_fit = location_score(profile, signals)
    exp_fit = exp_score(float(profile.get("years_of_experience") or 0))
    title_fit = title_score(profile.get("current_title", ""))
    consistency_bad, consistency_flags = consistency_penalty(record, suspicious_skill_count)

    # The JD says production ranking/retrieval experience should dominate, while
    # keyword-only AI enthusiasm should not. Multiplicative gates enforce that.
    base = (
        0.18 * title_fit
        + 0.18 * career_fit
        + 0.20 * jd_text_fit
        + 0.14 * skills_fit
        + 0.10 * exp_fit
        + 0.11 * behavior_fit
        + 0.05 * loc_fit
        + 0.04 * product_company_fit(record)
    )
    relevance_gate = 0.55 + 0.45 * max(title_fit, career_fit, jd_text_fit)
    anti_keyword_gate = 0.70 + 0.30 * max(title_fit, career_fit)
    score = base * relevance_gate * anti_keyword_gate
    score -= 0.10 * neg_text + 0.08 * career_penalty + 0.35 * consistency_bad
    score -= availability_penalty(signals)

    # Very strong profiles just outside the 5-9 year band should remain eligible,
    # but junior/generic profiles with AI keywords should not crowd the top 100.
    if title_fit < 0.5 and career_fit < 0.35:
        score *= 0.45
    if float(profile.get("years_of_experience") or 0) < 4 and title_fit < 0.9:
        score *= 0.75
    if signals.get("open_to_work_flag"):
        score += 0.015
    score += senior_ownership_bonus(record, behavior_fit)
    score += jd_specific_bonus(record, text, behavior_fit)
    if signals.get("notice_period_days", 180) > 120:
        score -= 0.02

    components = {
        "title": title_fit,
        "career": career_fit,
        "text": jd_text_fit,
        "skills": skills_fit,
        "experience": exp_fit,
        "behavior": behavior_fit,
        "location": loc_fit,
        "consistency_penalty": consistency_bad,
    }
    return CandidateScore(
        candidate_id=record["candidate_id"],
        score=max(0.0, score),
        reasoning=make_reasoning(record, top_skills, text_hits, behavior_notes, consistency_flags, components),
        components=components,
    )


def product_company_fit(record: dict[str, Any]) -> float:
    profile = record["profile"]
    current = 0.0
    if profile.get("current_company") in PRODUCT_COMPANIES:
        current = 0.85
    if profile.get("current_industry") in AI_PRODUCT_INDUSTRIES:
        current = max(current, 0.75)
    if profile.get("current_company") in SERVICE_COMPANIES:
        current = min(current, 0.35)
    prior = 0.0
    for job in record.get("career_history", []):
        if job.get("company") in PRODUCT_COMPANIES or job.get("industry") in AI_PRODUCT_INDUSTRIES:
            prior = max(prior, 0.85)
    return max(current, prior * 0.8)


def senior_ownership_bonus(record: dict[str, Any], behavior_fit: float) -> float:
    profile = record["profile"]
    title = profile.get("current_title", "")
    years = float(profile.get("years_of_experience") or 0)
    if not (5.0 <= years <= 9.0) or behavior_fit < 0.58:
        return 0.0
    bonus = 0.0
    if title in {"Senior AI Engineer", "Lead AI Engineer"}:
        bonus += 0.018
    elif title in {"Staff Machine Learning Engineer", "Senior Machine Learning Engineer"}:
        bonus += 0.014
    elif title in {"Senior NLP Engineer", "Senior Applied Scientist"}:
        bonus += 0.010
    if product_company_fit(record) >= 0.7:
        bonus += 0.004
    return bonus


def jd_specific_bonus(record: dict[str, Any], text: str, behavior_fit: float) -> float:
    profile = record["profile"]
    title = profile.get("current_title", "")
    years = float(profile.get("years_of_experience") or 0)
    if behavior_fit < 0.48:
        return 0.0

    bonus = 0.0
    senior_title = title in {
        "Senior AI Engineer",
        "Lead AI Engineer",
        "Staff Machine Learning Engineer",
        "Senior Machine Learning Engineer",
        "Senior NLP Engineer",
        "Senior Applied Scientist",
    }

    if senior_title and 5.0 <= years <= 9.5:
        if (
            ("connect users with relevant" in text or "surface relevant" in text)
            and ("what to show" in text or "matching layer" in text or "ranking layer" in text)
        ):
            bonus += 0.038
        if "senior ai engineer with" in text and "hybrid retrieval" in text and "offline/online evaluation" in text:
            bonus += 0.020

    domain_hits = sum(
        phrase in text
        for phrase in [
            "candidate profiles",
            "candidate corpus",
            "candidate-jd matching",
            "recruiter-facing search",
            "recruiter engagement",
            "time-to-shortlist",
            "behavioral-signal integration",
        ]
    )
    if domain_hits:
        bonus += min(0.026, 0.010 + domain_hits * 0.006)

    if "owned the end-to-end ranking pipeline" in text:
        bonus += 0.015
    if "designed the ranking layer" in text:
        bonus += 0.012
    if "led the migration from keyword-based to embedding-based search" in text:
        bonus += 0.012

    if profile.get("country") != "India":
        bonus *= 0.55
    if not record["redrob_signals"].get("open_to_work_flag"):
        bonus *= 0.6
    return min(bonus, 0.07)


def make_reasoning(
    record: dict[str, Any],
    top_skills: list[str],
    text_hits: list[str],
    behavior_notes: list[str],
    consistency_flags: list[str],
    components: dict[str, float],
) -> str:
    profile = record["profile"]
    signals = record["redrob_signals"]
    years = float(profile.get("years_of_experience") or 0)
    title = profile.get("current_title", "candidate")
    company = profile.get("current_company", "current company")
    location = profile.get("location", "unknown location")
    notice = signals.get("notice_period_days", "unknown")
    response = float(signals.get("recruiter_response_rate") or 0)

    evidence: list[str] = []
    if text_hits:
        evidence.append("evidence of " + ", ".join(text_hits[:2]))
    if top_skills:
        evidence.append("skills include " + ", ".join(top_skills[:3]))
    if product_company_fit(record) >= 0.7:
        evidence.append(f"product-company exposure at {company}")

    first = (
        f"{title} with {years:.1f} years in {location}; "
        + ("; ".join(evidence[:2]) if evidence else "profile has partial AI/search relevance")
        + "."
    )

    concern_bits: list[str] = []
    if components["experience"] < 0.7:
        concern_bits.append("experience is outside the 5-9 year ideal")
    if components["behavior"] < 0.45:
        concern_bits.append(f"availability is weaker with {response:.2f} response rate and {notice}-day notice")
    elif behavior_notes:
        concern_bits.append(", ".join(behavior_notes[:2]))
    else:
        concern_bits.append(f"{response:.2f} recruiter response rate and {notice}-day notice")
    if consistency_flags:
        concern_bits.append("consistency concern: " + consistency_flags[0])

    second = "Matches the JD on production ranking/retrieval more than generic AI keywords; " + "; ".join(concern_bits[:2]) + "."
    return first + " " + second


def rank_candidates(candidates_path: Path, limit: int) -> list[CandidateScore]:
    scored: list[CandidateScore] = []
    for record in open_records(candidates_path):
        scored.append(score_candidate(record))
    scored.sort(key=lambda item: (-item.score, item.candidate_id))
    return scored[:limit]


def write_submission(rows: list[CandidateScore], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        previous = float("inf")
        for rank, row in enumerate(rows, start=1):
            # Keep displayed scores strictly decreasing at 6 decimals, even when
            # raw model scores are extremely close.
            score = min(row.score, previous - 0.000001)
            previous = score
            writer.writerow([row.candidate_id, rank, f"{score:.6f}", row.reasoning])


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank Redrob candidates for the Senior AI Engineer JD.")
    parser.add_argument("--candidates", required=True, type=Path, help="Path to candidates.jsonl or candidates.jsonl.gz")
    parser.add_argument("--out", required=True, type=Path, help="Submission CSV path")
    parser.add_argument("--limit", type=int, default=100, help="Number of candidates to output")
    args = parser.parse_args()

    rows = rank_candidates(args.candidates, args.limit)
    write_submission(rows, args.out)
    print(f"Wrote {len(rows)} ranked candidates to {args.out}")


if __name__ == "__main__":
    main()
