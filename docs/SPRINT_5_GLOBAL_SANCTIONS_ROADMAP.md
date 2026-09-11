# Phase 3 — Sprint 5: Global Sanction & Entity Screening Engine

## 1. Sprint objective
Build the complete sanctions screening system described in the Global Sanction & Entity Screening Engine specification. **This is Phase 3, Sprint 5.** Sprint 5 includes jurisdiction/source selection, deterministic matching, alias/transliteration/phonetic evaluation, contextual attributes, LLM-assisted review, source-specific scoring, jurisdiction breakdown, Consensus Risk Index (CRI), sanctions verdicts, explainability, company and relationship-party screening, persistence, APIs, and end-to-end testing.

## 2. Current repository baseline

### Active sanctions sources
1. UNSC
2. OFAC SDN
3. OFAC Consolidated Non-SDN
4. UK Sanctions List
5. EU Consolidated Financial Sanctions List
6. India MHA/UAPA

`app/services/providers/sanctions_registry.py` is the current active source registry and currently contains these six sources.

### Provider architecture already in place
`app/services/providers/` contains one provider adapter per official source plus shared contracts/registries. Each provider follows the broad downloader/parser/normalizer/matcher/provider pattern. The provider layer should remain; **Phase 3 Sprint 5 adds a higher-level sanctions engine above it rather than replacing it.**

### Existing investigation/screening flow
Current flow is approximately:

Investigation API -> investigation service -> company/individual screening subjects -> screening plan -> sanctions source registry -> provider registry -> provider execution -> ScreeningResult persistence -> investigation screening response/review endpoints.

Company screening already includes the company/legal entity itself plus configured relationship parties such as directors, authorized persons, authorized signatories, shareholders, controllers, and UBOs.

## 3. Architecture to build

Keep the existing provider layer:

```text
app/services/providers/
    unsc/
    ofac/
    ofac_non_sdn/
    uk_sanctions/
    eu_sanctions/
    india_uapa/
```

Add a separate sanctions engine layer:

```text
app/services/sanctions/
    __init__.py
    models.py
    source_models.py
    source_catalog.py
    jurisdiction.py
    source_selector.py
    candidate.py
    entity_matcher/
    phonetic_matcher/
    attribute_evaluator/
    llm_reviewer/
    consensus_engine/
    explainability/
    screening_orchestrator/
```

Conceptual flow:

```text
Target / Investigation
        ↓
Company + relationship subjects
        ↓
Country / jurisdiction resolution
        ↓
Applicable official source catalogue
        ↓
Global provider framework / source adapter
        ↓
Candidate normalization
        ↓
Entity matching
        ↓
Phonetic + alias + transliteration checks
        ↓
DOB / country / ID / entity-type signals
        ↓
LLM contextual review
        ↓
Source-specific match scores
        ↓
Jurisdiction/source breakdown
        ↓
Consensus Risk Index (CRI)
        ↓
Final sanctions verdict
        ↓
Explainability report
```

## 4. Phase 3 Sprint 5 roadmap

### Step 0 — Repository cleanup and contracts
- Remove/ignore stale unfinished Australia provider code before it can be mistaken for an active source. The current GitHub tree still contains `app/services/providers/australia_sanctions`, while Australia is not in the active source registry.
- Verify the active six-source registry and provider registry agree.
- Preserve the existing company relationship screening behavior.
- Define shared Sprint 5 schemas for target, candidate, source result, CRI result, LLM review result, and explainability output.
- Build and verify the common deterministic matching foundation before changing live provider integration.
- CRI execution formula is locked as:

```text
CRI = [1 - Π(1 - (S_i × W_i))] × 100
```

where each `S_i` is the normalized source-level score and `W_i` is its explicit source weight. The CRI must not use simple average or simple maximum.

- Build the foundation so applicable official sources can remain represented even when Sentinel AI does not yet have a provider adapter.

### Step 1 — Global official-source provider framework **(LOCKED)**
Sprint 5 is intended to provide **country-agnostic sanctions-provider capability**, not a separate hardcoded architecture per country.

Required architecture:

```text
Country / jurisdiction
        ↓
Verified official-source catalogue
        ↓
Applicable source records
        ↓
Provider capability lookup
        ↓
Generic official-source provider framework
        ↓
Source-specific adapter only where necessary
        ↓
Common SanctionsCandidate
        ↓
Common matching engine
```

Rules:
- Do **not** build the system as a growing list of unrelated `SingaporeProvider`, `JapanProvider`, `FranceProvider`, etc. classes when a common adapter can handle the official source format.
- A new jurisdiction should normally require source registration/configuration plus an adapter only when the official source format or access mechanism is materially different.
- The source catalogue must be independent from provider implementation status.
- An applicable source with no implemented adapter must remain visible as `NOT_IMPLEMENTED`; it must never be silently discarded.
- Maintain provenance: official authority, official source/list name, issuing jurisdiction, source URL/reference, retrieval metadata, source UID/list UID where available.
- Keep `app/services/providers/` as the official-source adapter layer.
- Use `app/services/sanctions/` for jurisdiction resolution, common matching, scoring, consensus, verdicts, and explainability.

### Step 2 — Jurisdiction and source catalogue
Build a verified source catalogue independent from provider implementation.

Required capabilities:
- Accept one country or multiple countries/jurisdictions.
- Normalize country names/codes.
- Distinguish global sources from jurisdiction-specific sources.
- Return the applicable sources for the target/investigation.
- Keep source metadata: source name, issuing authority, issuing country/region, source type, active status, official source reference, provider implementation status.
- Do not hard-code country logic into provider classes.
- Do not invent unsupported country sources; add jurisdiction-specific entries only from verified official sources.
- The catalogue should be able to represent a real official source as `NOT_IMPLEMENTED` until its adapter is built.

### Step 3 — Common candidate model
Create one normalized candidate representation across all providers.

Required fields should support at minimum:
- source/list ID
- canonical name
- aliases
- subject type
- issuing country/authority
- countries/nationalities/addresses where available
- dates of birth / birth year where available
- identifiers / tax IDs / registration numbers where available
- program/regime
- provenance/evidence

Preserve the raw provider evidence for auditability.

### Step 4 — Deterministic entity matching
Replace provider-specific `SequenceMatcher`-only logic as the primary engine with a common matcher.

Required matching signals:
- Jaro-Winkler similarity
- Levenshtein similarity/distance
- token-aware comparison
- token reordering
- exact alias matching
- alias/transliteration support
- phonetic similarity using Metaphone/Soundex or an equivalent deterministic implementation
- entity-type consistency
- DOB/birth-year comparison
- country/jurisdiction comparison
- identifier/tax-ID comparison

Provider-specific matching should feed candidate evidence into the common matcher instead of independently deciding final sanctions risk.

### Step 5 — Signal scoring and penalties
Implement the Sprint 5 source-level scoring methodology.

Baseline specification:
- Direct/alias name similarity: Jaro-Winkler + Levenshtein, base 0.0–1.0.
- Phonetic agreement: +0.10.
- Birth year agreement: +0.15.
- Country/jurisdiction agreement: +0.15.
- Tax ID/identifier agreement: +0.15.
- Gender discrepancy: penalty in the specified -0.20 to -0.40 range.
- Clear DOB mismatch: penalty in the specified -0.20 to -0.40 range.
- Conflicting organization structural codes/entity types: penalty in the specified -0.20 to -0.40 range.

Implement the scoring as explicit signals so every score is explainable.

### Step 6 — LLM-assisted contextual review
Create the LLM reviewer defined by the supplied system prompt.

The LLM receives structured target + official candidate evidence, not an ungrounded name-only question.

Required responsibilities:
- Compare target against candidate canonical name and aliases.
- Resolve contextual identity evidence.
- Assess transliteration/context where deterministic scoring is uncertain.
- Explain matching and mismatch reasons.
- Return strict structured JSON.
- Never become the authoritative source of sanctions data; official provider evidence remains the source of record.

### Step 7 — Source/jurisdiction result model
Every candidate/source result must preserve:
- source name
- issuing country/region
- raw match score
- canonical matched name
- matched alias
- confidence tier
- matching signals
- mismatch signals
- provenance/source UID
- LLM decision/reasoning when invoked

Required confidence tiers:
- HIGH
- MEDIUM
- LOW

### Step 8 — Consensus Risk Index (CRI)
Build a dedicated consensus engine.

Hard requirements:
- Do NOT use simple average.
- Do NOT use simple maximum.
- Preserve explicit source weights.
- Compute the CRI using the locked execution formula:

```text
CRI = [1 - Π(1 - (S_i × W_i))] × 100
```

Validation requirements:
- `S_i` must be normalized to 0.0–1.0.
- `W_i` must be normalized to 0.0–1.0.
- Duplicate source names must be rejected within one CRI component set.
- Invalid score/weight values must raise validation errors rather than being silently clamped.

### Step 9 — Final sanctions verdict and hard overrides
Map CRI and source evidence to:
- `FLAGGED_HIGH_RISK`
- `POTENTIAL_MATCH_REVIEW`
- `CLEAR`

Current explicit default thresholds are:
- CRI >= 85.0 -> `FLAGGED_HIGH_RISK`
- CRI >= 65.0 -> `POTENTIAL_MATCH_REVIEW`
- CRI < 65.0 -> `CLEAR`

These thresholds must remain explicit/configurable.

Add explicit hard overrides for critical sanctions findings so a consensus calculation cannot dilute a confirmed/authoritative match.

Current hard override rule implemented in the foundation:
- Exact identifier match -> at minimum CRI 85.0 and `FLAGGED_HIGH_RISK`.

### Step 10 — Company and relationship screening integration
Keep the existing subject expansion behavior, but route every subject through the new Sprint 5 engine.

For a company:
- company itself
- UBOs
- owners/shareholders
- directors
- controllers
- authorized persons
- authorized signatories
- every other configured relationship party

Each subject is evaluated independently against the applicable sources.

The external response remains a flat `screening[]` structure, while the consensus engine keeps the internal grouping needed for jurisdiction/source analysis.

### Step 11 — Database and API model changes
Extend the persistence layer as required to store Sprint 5 outputs without destroying the current raw evidence.

Potential additions include:
- issuing jurisdiction/authority
- source/list name
- raw provider score
- deterministic entity-match score
- CRI / consensus result
- final sanctions verdict
- matched alias
- matching signals
- mismatch signals
- LLM review decision and reasoning
- explainability payload
- screening execution/version metadata

Do not remove existing raw `evidence`, source UID, subject identity, or relationship information.

### Step 12 — API redesign
Upgrade the existing investigation screening endpoints to return the Sprint 5 structure while preserving compatibility where practical.

Target JSON shape:

```json
{
  "query_metadata": {
    "target_name": "<INPUT_NAME>",
    "target_type": "Individual | Entity",
    "screening_timestamp": "<ISO_TIMESTAMP>"
  },
  "consensus_summary": {
    "consensus_risk_index": 0,
    "final_verdict": "FLAGGED_HIGH_RISK | POTENTIAL_MATCH_REVIEW | CLEAR",
    "primary_flagged_jurisdiction": "<COUNTRY/GLOBAL>",
    "total_sources_evaluated": 0,
    "sources_with_positive_matches": 0
  },
  "source_breakdown": [],
  "explainability_report": "<HUMAN_READABLE_SUMMARY>"
}
```

For investigations with multiple company relationships, keep the existing flat screening rows and attach subject/relationship context to every result.

### Step 13 — End-to-end testing
Build deterministic test cases for:
- exact sanctioned name
- exact alias
- fuzzy near-match
- false positive with similar but unrelated name
- transliteration
- reversed word order
- person/entity type conflict
- DOB agreement
- DOB mismatch
- country agreement
- country mismatch
- identifier exact match
- multiple positive sources
- one strong source + multiple weak sources
- all clear
- company plus multiple relationship parties
- jurisdiction-specific source selection
- LLM review with structured JSON validation
- CRI and hard-override behavior
- applicable source with no provider adapter yet
- generic provider onboarding for a new jurisdiction/source format

Regression cases already observed during development must remain tests, including:
- `KAIDA` / OFAC alias behavior
- `KAIDA` / UNSC fuzzy false-positive behavior
- CloudWalk / OFAC Non-SDN parser and exact entity identification
- EU XML parsing and multilingual alias preservation
- Singapore TSOFA / Mas Selamat should be used as a jurisdiction-source verification case once the official source is registered and its provider is implemented

## 5. Locked architecture decisions for Phase 3 Sprint 5
- Keep `app/services/providers/` as the official-source adapter layer.
- Add a separate `app/services/sanctions/` engine above the providers.
- Build a **global, country-agnostic provider framework**, not a hardcoded one-provider-per-country architecture.
- New jurisdictions should normally be added by registering verified official sources and using a generic adapter; create a specialized adapter only when the official source format/access mechanism requires it.
- Separate source applicability from provider implementation status.
- Never silently discard an applicable source because its provider is not implemented yet.
- Do not let one provider's raw fuzzy score become the final overall sanctions risk.
- Do not use `max()` for final consensus risk.
- Do not use simple average for final consensus risk.
- Use the exact CRI formula supplied for Sprint 5: `CRI = [1 - Π(1 - (S_i × W_i))] × 100`.
- Keep provider evidence and provenance for auditability.
- Screen company + relationship parties independently.
- One overall sanctions decision per screening target/consensus context, not one provider-specific overall decision.
- **Phase 3 Sprint 5 owns the complete sanctions system, including provider capability, source selection, LLM review and CRI.**
- **No sanctions-related capability is deferred to a later sprint.**
- **These architecture decisions remain locked until Sprint 5 is formally completed.**

## 6. Known current-state gaps observed in the pushed repository
- The active sanctions source registry is static and contains six sources.
- Provider-level matchers still rely heavily on `difflib.SequenceMatcher`; they do not yet implement the Sprint 5 Jaro-Winkler + Levenshtein + phonetic + attribute methodology.
- `ScreeningResult` currently stores provider result, matched name, confidence, evidence, source UID and some match metadata, but not the full Sprint 5 CRI/source-breakdown/LLM explainability model.
- The current screening service directly executes all entries in `SANCTIONS_SOURCE_REGISTRY` and contains legacy provider-score-based recommendation logic.
- Company subject expansion already exists and is the correct starting point for relationship-aware Sprint 5 integration.
- The current GitHub tree still contains an unfinished `australia_sanctions` directory even though Australia is not active in the sanctions registry; clean this up before Sprint 5 implementation begins.
- The new Sprint 5 foundation currently exists locally and has been exercised interactively; provider integration remains the next major workstream.

## 7. Phase 3 Sprint 5 completion criteria
Sprint 5 is complete only when:
1. A target can be screened against the correct global + jurisdiction-specific sources.
2. A new jurisdiction can be onboarded through the global provider framework without changing the core matching engine.
3. Every provider candidate is normalized into one common candidate structure.
4. Matching uses the Sprint 5 deterministic methodology.
5. LLM review is grounded in official candidate evidence and produces validated JSON.
6. Source-level scores and jurisdiction breakdown are preserved.
7. CRI is calculated using the exact approved formula.
8. Hard overrides work for critical findings.
9. Company and all configured relationship parties are independently screened.
10. Final API output contains the required consensus/source breakdown/explainability fields.
11. Regression and end-to-end tests pass for the known false-positive and exact-match cases.
12. Applicable sources without adapters remain visible as unavailable rather than silently omitted.
