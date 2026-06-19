$ErrorActionPreference = "Stop"

$Source = "C:\Users\dhama\Downloads\Idea Submission Template _ Redrob (1).pptx"
$OutDir = Join-Path $PSScriptRoot "outputs"
$OutPptx = Join-Path $OutDir "redrob_ai_ranker_submission_deck.pptx"
$OutPdf = Join-Path $OutDir "redrob_ai_ranker_submission_deck.pdf"

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
Copy-Item -LiteralPath $Source -Destination $OutPptx -Force

function Set-ShapeText {
  param(
    [object]$Shape,
    [string]$Text,
    [double]$FontSize = 16,
    [int]$Color = 0
  )
  $Shape.TextFrame.TextRange.Text = $Text
  $Shape.TextFrame.WordWrap = -1
  $Shape.TextFrame.AutoSize = 0
  $Shape.TextFrame.TextRange.Font.Size = $FontSize
  $Shape.TextFrame.TextRange.Font.Name = "Aptos"
  $Shape.TextFrame.TextRange.Font.Color.RGB = $Color
  try {
    $Shape.TextFrame.TextRange.ParagraphFormat.Bullet.Visible = 0
    $Shape.TextFrame.TextRange.ParagraphFormat.SpaceAfter = 2
    $Shape.TextFrame.TextRange.ParagraphFormat.SpaceBefore = 0
  } catch {}
}

function Set-SlideBody {
  param(
    [object]$Slide,
    [string]$Text,
    [double]$FontSize = 16
  )
  $body = $null
  foreach ($shape in $Slide.Shapes) {
    if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
      $current = $shape.TextFrame.TextRange.Text
      if ($current -notmatch "^(Solution Overview|JD Understanding|Ranking Methodology|Explainability|End-to-End Workflow|Results|Technologies Used|Submission Assets)") {
        $body = $shape
      }
    }
  }
  if ($null -eq $body) { throw "Body placeholder not found on slide $($Slide.SlideIndex)" }
  $body.Left = 60
  $body.Top = 105
  $body.Width = 830
  $body.Height = 390
  Set-ShapeText -Shape $body -Text $Text -FontSize $FontSize
}

function Add-Box {
  param(
    [object]$Slide,
    [double]$X,
    [double]$Y,
    [double]$W,
    [double]$H,
    [string]$Text,
    [int]$Fill = 16773866,
    [int]$Line = 10958754
  )
  $shape = $Slide.Shapes.AddShape(5, $X, $Y, $W, $H)
  $shape.Fill.ForeColor.RGB = $Fill
  $shape.Line.ForeColor.RGB = $Line
  $shape.Line.Weight = 1.25
  Set-ShapeText -Shape $shape -Text $Text -FontSize 12
  $shape.TextFrame.MarginLeft = 6
  $shape.TextFrame.MarginRight = 6
  $shape.TextFrame.MarginTop = 4
  $shape.TextFrame.MarginBottom = 4
  return $shape
}

$ppt = New-Object -ComObject PowerPoint.Application
$presentation = $null
try {
  $presentation = $ppt.Presentations.Open($OutPptx, $false, $false, $false)

  foreach ($shape in $presentation.Slides.Item(1).Shapes) {
    if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
      $text = $shape.TextFrame.TextRange.Text.Trim()
      if ($text -eq "Team Name :") {
        Set-ShapeText -Shape $shape -Text "Team Name : OM DHAMANE" -FontSize 19
      } elseif ($text -eq "Team Leader Name :") {
        Set-ShapeText -Shape $shape -Text "Team Leader Name : OM DHAMANE" -FontSize 19
      } elseif ($text -eq "Problem Statement :") {
        Set-ShapeText -Shape $shape -Text "Problem Statement : Data & AI Challenge - Intelligent Candidate Discovery" -FontSize 18
      }
    }
  }

  Set-SlideBody -Slide $presentation.Slides.Item(2) -FontSize 14.5 -Text @"
Redrob FitRanker is a deterministic candidate discovery engine built for the Senior AI Engineer JD.

- Ranks 100K profiles by production search, retrieval, ranking, embeddings, and recommender-system evidence.
- Combines career trajectory, trusted skill signals, product-company context, availability, and consistency checks.
- Differentiator: interprets what the JD requires, not just which keywords appear in a resume.
- Down-weights AI-keyword stuffing unless career history proves shipped ranking/retrieval ownership.
"@

  Set-SlideBody -Slide $presentation.Slides.Item(3) -FontSize 12.7 -Text @"
JD interpretation:
- Senior AI/ML engineer who can ship search, matching, ranking, retrieval, embeddings, and evaluation systems.
- Strong Python, ML engineering, vector search, relevance metrics, product ownership, and production mindset.

Candidate evaluation signals:
- Titles and career evidence: Senior, Lead, Staff, AI/ML, NLP, Search, Recommender, Applied Scientist.
- Technical depth: LTR, BM25, hybrid search, ANN/vector DBs, embeddings, reranking, MLOps.
- Trust: skill duration/proficiency/endorsements, GitHub, interviews/offers, response behavior, recency.
- Negative filters: pure research-only, generic GenAI demos, consulting-only profiles, stale or inconsistent data.
"@

  Set-SlideBody -Slide $presentation.Slides.Item(4) -FontSize 12.9 -Text @"
Hybrid scoring stack:
1. Role and career prior: senior AI/ML/search/recsys/NLP titles and shipped ranking work.
2. Evidence parser: explicit and plain-language signals for relevance systems, retrieval, and matching.
3. Trusted skills: embeddings, FAISS/Qdrant/Milvus/Weaviate, Python, ML systems, ranking metrics.
4. Product and delivery context: ownership at product companies, MLOps, experimentation, scale.
5. Behavior/logistics: activity recency, response rate, notice period, open-to-work, location fit.

Final score = weighted fit components + JD-specific bonuses - risk penalties, sorted deterministically.
"@

  Set-SlideBody -Slide $presentation.Slides.Item(5) -FontSize 12.9 -Text @"
Explainability:
- Every row includes profile-grounded reasoning: title, years, location, named skills, project evidence, availability.
- No LLM candidate calls during ranking; reasons are derived only from dataset fields.
- Output is reproducible and auditable: same input, same ranks, same reasons.

Validation and risk controls:
- Schema checks, rank ordering, score monotonicity, and official validator pass.
- Consistency checks for career duration, stale activity, unsupported expert skills, and weak evidence.
- Keyword-heavy profiles are capped unless career history confirms production ownership.
"@

  Set-SlideBody -Slide $presentation.Slides.Item(6) -FontSize 15 -Text @"
1. Input: candidates.jsonl + fixed Senior AI Engineer JD
2. Parse JSON and normalize profile, career, skills, and Redrob signals
3. Extract JD evidence and structured candidate features
4. Score using hybrid components, gates, caps, and penalties
5. Sort deterministically and generate top 100 candidates
6. Validate with official script and sanity-check the top ranks

Output columns: candidate_id, rank, score, reasoning
"@

  $s7 = $presentation.Slides.Item(7)
  Add-Box -Slide $s7 -X 45 -Y 112 -W 105 -H 52 -Text "JD`nrequirements" -Fill 14743295 -Line 2763519 | Out-Null
  Add-Box -Slide $s7 -X 45 -Y 208 -W 105 -H 52 -Text "100K candidate`nJSONL" -Fill 14743295 -Line 2763519 | Out-Null
  Add-Box -Slide $s7 -X 185 -Y 154 -W 105 -H 70 -Text "Feature builder`ncareer + skills + signals" | Out-Null
  Add-Box -Slide $s7 -X 315 -Y 154 -W 105 -H 70 -Text "Hybrid scorer`nfit + evidence + trust" | Out-Null
  Add-Box -Slide $s7 -X 445 -Y 154 -W 105 -H 70 -Text "Risk gates`ncaps + penalties" | Out-Null
  Add-Box -Slide $s7 -X 575 -Y 154 -W 105 -H 70 -Text "Submission`nCSV + reasoning" -Fill 15794152 -Line 3978590 | Out-Null
  Add-Box -Slide $s7 -X 180 -Y 285 -W 370 -H 55 -Text "Deterministic, CPU-only, no network, no GPU, reproducible within the 5-minute / 16GB rule" -Fill 16382457 -Line 12829635 | Out-Null
  foreach ($lineSpec in @(@(150,189,35), @(290,189,25), @(420,189,25), @(550,189,25))) {
    $line = $s7.Shapes.AddLine($lineSpec[0], $lineSpec[1], $lineSpec[0] + $lineSpec[2], $lineSpec[1])
    $line.Line.ForeColor.RGB = 10958754
    $line.Line.Weight = 2
    $line.Line.EndArrowheadStyle = 3
  }

  Set-SlideBody -Slide $presentation.Slides.Item(8) -FontSize 12.9 -Text @"
Run characteristics:
- Processes 100,000 candidates locally on CPU in under one minute on the prepared bundle.
- Uses only Python standard library for the ranker; no hosted model calls, no GPU, no external services.
- Official validator result: submission is valid.

Submission quality:
- 100 ranked candidates with monotonic scores and deterministic tie handling.
- Top ranks concentrate on Senior/Lead/Staff AI/ML/NLP/search profiles with production ranking or retrieval evidence.
- Reasoning fields are short, profile-grounded, and reviewable by judges.
"@

  Set-SlideBody -Slide $presentation.Slides.Item(9) -FontSize 15 -Text @"
- Python 3 standard library: streaming JSONL parsing, scoring, CSV generation.
- Deterministic feature scoring: career evidence, semantic keywords, trusted skills, behavioral availability.
- Streamlit optional sandbox demo for small-sample exploration.
- Artifact-tool rendering plus PowerPoint export for the required submission deck/PDF.
- Codex used for development, inspection, QA, and packaging; candidate ranking itself does not depend on hosted LLM calls.
"@

  Set-SlideBody -Slide $presentation.Slides.Item(10) -FontSize 12.8 -Text @"
Files ready for submission:
- Ranked output: redrob_submission.csv
- Deck PDF: redrob_ai_ranker_submission_deck.pdf
- Deck source: redrob_ai_ranker_submission_deck.pptx
- Code: rank.py, README.md, requirements.txt, app.py

Reproduce:
python rank.py --candidates ./candidates.jsonl --out ./redrob_submission.csv
python path/to/validate_submission.py redrob_submission.csv

GitHub repository URL: enter the public repo link in the Hack2Skill form.
"@

  $presentation.Save()
  if (Test-Path -LiteralPath $OutPdf) { Remove-Item -LiteralPath $OutPdf -Force }
  $presentation.SaveAs($OutPdf, 32)
}
finally {
  if ($presentation -ne $null) { $presentation.Close() }
  $ppt.Quit()
}

Get-Item -LiteralPath $OutPptx, $OutPdf | Select-Object FullName, Length
