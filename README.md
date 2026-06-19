# Redrob Senior AI Engineer Ranker

Deterministic, CPU-only ranking system for the Redrob India Runs Data & AI Challenge.

The released JD is not asking for the most AI keywords. It asks for a founding Senior AI Engineer who has shipped production search, retrieval, ranking, recommendation, and evaluation systems, ideally in a product-company environment and with strong hiring availability signals. This ranker encodes that interpretation directly.

## Reproduce Submission

From the repository root:

```bash
python rank.py --candidates "./[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl" --out redrob_submission.csv
python "./[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" redrob_submission.csv
```

Expected validator output:

```text
Submission is valid.
```

The ranking step is dependency-free, performs no network calls, uses CPU only, and ran locally on 100,000 candidates in about 32 seconds.

## Methodology

The model is a hybrid structured scorer with explicit anti-trap gates:

- **Role fit:** strong prior for Senior AI Engineer, Search Engineer, Recommendation Systems Engineer, Applied ML Engineer, Senior/Staff ML Engineer, NLP Engineer, and adjacent ML roles.
- **Production ranking evidence:** lexical evidence from summaries and career history for retrieval, ranking, recommendation systems, hybrid search, semantic search, embeddings, vector infrastructure, NDCG/MRR/MAP, A/B testing, and shipped production systems. The scorer also recognizes plain-language signals such as "connect users with relevant information", "surface relevant content", "matching layer", "search and discovery", and "ranking calibration".
- **Skill quality:** weighted skills for information retrieval, ranking systems, search backend/infrastructure, content matching, vector representations, text encoders, learning to rank, vector search, FAISS/Qdrant/Milvus/Weaviate/Pinecone/OpenSearch/Elasticsearch, sentence transformers, BM25, Python, MLOps, and LLM fine-tuning. Skill duration, proficiency, and endorsements affect trust.
- **Career context:** product-company and AI/product industry exposure is rewarded; service-only consulting backgrounds are down-weighted because the JD explicitly flags this as a fit risk.
- **Experience fit:** 5-9 years is ideal, with controlled allowance for exceptional adjacent profiles.
- **Behavioral availability:** recency, recruiter response rate, response speed, open-to-work status, notice period, GitHub activity, interview completion, offer acceptance, profile completeness, recruiter saves, and verification signals affect the final score. Very stale or low-response candidates receive an additional bounded penalty.
- **Senior ownership:** reachable Senior/Lead/Staff profiles in the 5-9 year band receive a small close-call bonus because the JD is for a founding senior owner, not only a skill match.
- **Location/logistics:** Pune/Noida and major Indian tech hubs are rewarded; relocation willingness helps.
- **Honeypot resistance:** penalties catch inconsistent dates, implausible career totals, jobs before known founding years, and many expert/advanced skills with near-zero duration.
- **JD-specific domain signal:** small capped bonuses reward candidate-JD matching, recruiter-facing search, recruiter engagement, time-to-shortlist, behavioral-signal integration, and senior ownership of relevance infrastructure.

The final score uses a weighted base plus multiplicative relevance gates. This prevents generic profiles with many AI keywords from outranking candidates whose career history actually shows production ranking/retrieval work.

## Output

The generated file is:

```text
redrob_submission.csv
```

Format:

```text
candidate_id,rank,score,reasoning
```

Each reasoning entry references concrete facts from the candidate profile and connects them to the JD, while noting availability or fit concerns when present.

## Optional Demo

For a hosted sandbox, install Streamlit and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app accepts a small `.jsonl` candidate file and returns a ranked CSV preview. The core ranking logic remains the same as `rank.py`.

## AI Usage

Codex was used to inspect the bundle, design the scoring approach, write code, and validate the output. No candidate data is sent to hosted LLM APIs during ranking.
# The-Data-AI-Challenge-redrob_ai
