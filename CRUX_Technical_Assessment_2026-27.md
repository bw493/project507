# CRUX — Technical Program Assessment

**Prepared:** July 17, 2026
**Scope:** Technical curriculum and program design, 2026–27 cycle
**Purpose:** Reference document for the next planning phase

---

## 1. Basis of Assessment

This assessment draws on the following materials:

| Source | Contents |
| --- | --- |
| `CruX Syl 26-27.docx` | Fall and Winter quarter syllabus and timeline |
| `26-27 WS1: Introduction to Neurotech.pptx` | Workshop 1 slide deck |
| `26-27 WS3: Preprocessing I & II.pptx` | Workshop 3 slide deck |
| `Summer Planning 26-27 workshops.xlsx` | Workshop planning grid, lead assignments, prior-year feedback |
| `Operations Summer Meeting Notes.docx` | Board structure and cross-department context |
| `24-25 Technical / OpenBCI Headset Tutorial` | Hardware tutorial video (existence noted; not analyzed) |

**Important limitation.** No code repository, member roster, project outcomes, or competition results were available. Accordingly, this document assesses **curriculum and program design**, not execution outcomes. Any claim about what members actually build would require evidence not present in these materials.

---

## 2. Demonstrated Technical Strengths

### 2.1 Coherent, industry-aligned pipeline
The curriculum follows the real BCI workflow end to end: data collection → preprocessing → feature extraction → classification → evaluation → project deployment. Workshop 1 states this pipeline explicitly, and each subsequent workshop occupies a defined stage within it. Members finish with a transferable mental model rather than a set of isolated topics.

### 2.2 Technically sound preprocessing content
The Preprocessing deck is the strongest material in the set. It justifies filtering rather than merely demonstrating it:

- Establishes canonical EEG bands — delta (0.5–4 Hz), theta (4–8 Hz), alpha (8–13 Hz), beta (13–30 Hz), gamma (30+ Hz) — with associated brain states.
- Establishes artifact spectra separately — slow drift (<0.5–1 Hz), EMG (>30–40 Hz), power line (60 Hz US / 50 Hz EU).
- Motivates filtering as exploitation of that spectral separation, then introduces high-pass, low-pass, band-pass, and notch filters, each tied to a specific noise problem.
- Extends beyond filtering into artifact rejection (ocular, muscular, movement) and epoching.

The logical ordering is correct and well pitched for undergraduates without prior signal-processing background.

### 2.3 Low barrier to entry paired with real depth
The syllabus requires no prior coding or neuroscience knowledge, yet the program builds toward Fourier analysis, machine-learning classifiers, and hardware streaming. Carrying a true beginner to that endpoint within one academic year is a meaningful pedagogical achievement.

### 2.4 Genuine hardware exposure
Members work with physical OpenBCI EEG/EMG equipment. Winter quarter includes Hardware I/II and a data-streaming session (BrainFlow, LSL). Acquisition experience — not offline analysis alone — distinguishes CRUX from purely lecture-based organizations.

### 2.5 Evidence of deliberate iteration
The planning spreadsheet documents active refinement rather than reuse: consolidating the two preprocessing workshops, dropping ICA as too advanced for the level, adding a full pipeline overview to WS1, and proposing parallel "biology" and "coding" tracks. Prior-year feedback ("pacing is too fast," "more detail") is recorded and being acted upon. This responsiveness is a sign of institutional health.

---


## 3. Partner-Matching Framework

This section translates the strengths described above into a standard for evaluating candidate organizations, so that future mapping proceeds consistently rather than case by case. It connects that standard to the outreach tiers (A/B/C) through an explicit decision rule, and defines the cooperation groups so that they serve the full breadth of the membership — computational biology and neuroscience, mathematics and statistics, and business and economics, as well as engineering and computer science.

### 3.1 Matching characteristics (the standard)

A candidate organization is a strong match to the degree that it exhibits the following characteristics:

- **Technical and domain overlap** with CRUX's core pipeline — noninvasive EEG acquisition, preprocessing, feature extraction, and classification — or with the scientific, quantitative, and commercial questions that surround it. The closer a partner's work sits to this territory, the more directly members across disciplines can contribute.
- **Stack and hardware compatibility** — familiarity with OpenBCI-class hardware, BrainFlow/LSL streaming, or an MNE-Python and scikit-learn software environment lowers onboarding cost for both parties.
- **Stage and receptiveness** — early-to-mid-stage companies (roughly pre-seed through Series B) and labs without an established undergraduate pipeline tend to derive the most value from student engagement.
- **Geographic proximity** — California, and Southern California in particular, permits in-person collaboration, site visits, and guest sessions.
- **Defined engagement surface** — a scoped problem, dataset, study, or business question that a student team can realistically address within a single academic term. Because the membership is multidisciplinary, this surface need not be an engineering task; it may equally be a signal-analysis or validation study, a modeling problem, or a market, user, or partnership question.

These criteria are cumulative rather than absolute. An organization need not satisfy all five to warrant contact; the number and strength of matches provide a consistent basis for prioritization.

### 3.2 Tier decision rule (the dividing lines)

Two of the five characteristics serve as the decisive dividing lines for tiering: **technical and domain overlap** and **US geography (California preferred)**. Applying them in sequence assigns each candidate an unambiguous tier, operationalizing the Sub-goal 1.1 target of 40–50 startups without leaving tier placement to case-by-case judgment.

| Tier | Technical / domain overlap | Geography | Target count |
| --- | --- | --- | --- |
| **A** | Strong — direct overlap with a CRUX project or pipeline stage | US-based, ideally California | 10–15 |
| **B** | Relevant category but adjacent rather than direct — *or* strong overlap located outside the US | exactly one Tier-A line unmet | 15–20 |
| **C** | Category-adjacent or exploratory; engagement surface not yet identifiable | any | remainder to reach 40–50 |

Stated as a single rule: an organization is **Tier A only if it clears both the overlap line and the US-geography line**; missing exactly one of the two places it in **Tier B**; missing both, or lacking any identifiable engagement surface, places it in **Tier C**. Outreach then sequences A → B → C, and the three counts sum to the 40–50 total.

### 3.3 Cooperation categories (cross-disciplinary)

Prospective partners fall into four broad groups. Groups 1 through 3 correspond to the categories in which CRUX holds demonstrable credibility; Group 4 extends the same framework to academic collaborators. Each group and its matching signal:

1. **Brain–Computer Interface** — direct overlap with CRUX's decoding and classification pipeline.
2. **Consumer Neurotech** — applied EEG, wearables, and neurofeedback products.
3. **Tools & Infrastructure** — hardware, acquisition systems, SDKs, and analysis software.
4. **Research Institutes & Academic Labs** — neural-engineering and neuroprosthetics research programs.

Crucially, each group offers an engagement surface for every discipline in the membership, not for engineers alone. The matrix below shows how members from each background plug in:

| Group | Engineering & CS | Comp bio & neuro | Math & stats | Business & econ |
| --- | --- | --- | --- | --- |
| **1. BCI** | Pipeline builds, streaming, classifier implementation | Paradigm design, biomarker and signal interpretation | Decoding models, validation methodology | Use-case framing, partnership scoping |
| **2. Consumer Neurotech** | Firmware, app and device integration | Physiological grounding, effect validation | Experimental design, statistical analysis | User research, positioning, go-to-market |
| **3. Tools & Infrastructure** | Integration, tooling, benchmarking | Validation datasets, domain testing | Performance benchmarking, methods comparison | Developer-market and pricing analysis |
| **4. Research Institutes & Labs** | Software and acquisition support | Wet-lab and analysis collaboration | Modeling and statistical support | Program operations, outreach, impact framing |

Cooperation modes across all four groups remain sponsorships, scoped student consulting engagements, product or analysis collaborations, guest talks, and student placement — drawn from whichever disciplines a given partner most needs. Recording each candidate against these four groups, against the discipline matrix, and against the characteristics in Section 3.1 keeps future mapping consistent, comparable across cycles, and useful to the entire membership rather than its engineering subset alone.
