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

**Important limitation.** No code repository, member roster, project outcomes, or competition results were available. Per board discussion, project artifacts remain the intellectual property of individual members and are not retained by the club. Accordingly, this document assesses **curriculum and program design**, not execution outcomes. Any claim about what members actually build would require evidence not present in these materials.

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

## 3. Identified Gaps and Recommended Additions

### 3.1 Epoching and event-locking
Currently defined but underdeveloped. The technically substantive content is *what determines the analysis window*:

- Baseline correction intervals.
- Latency of the target component — P300 at approximately 300 ms post-stimulus; ERD/ERS in motor imagery over roughly 0.5–2.5 s.
- How marker and trigger timing is actually recorded and synchronized.

Timing precision is where most undergraduate BCI projects fail silently. This deserves substantially more weight.

### 3.2 Feature extraction — make it paradigm-specific
Time, frequency, and spatial features are named but not grounded. Recommend mapping features to paradigms explicitly:

| Paradigm | Recommended features |
| --- | --- |
| Motor imagery | Band power in mu (8–13 Hz) and beta (13–30 Hz) over C3/C4/Cz; Common Spatial Patterns (CSP) |
| P300 / ERP | Downsampled time-domain amplitudes over post-stimulus window; Pz and parietal sites |
| SSVEP | Power or Canonical Correlation Analysis (CCA) at stimulus frequencies and harmonics |

**Note:** SSVEP is absent from the current curriculum. It is the highest-accuracy, lowest-effort paradigm available and is the strongest candidate for a first member project.

### 3.3 Classification and evaluation — raise to preprocessing-level rigor

**Baselines over exotica.** LDA on CSP features and shrinkage-LDA remain competitive on small EEG datasets. Riemannian geometry methods (covariance matrices with tangent-space mapping, via `pyriemann`) are the modern strong baseline and are notably robust with limited trials.

**Validation methodology is the highest-value addition.** Random k-fold cross-validation on epoched EEG leaks information across temporally adjacent trials and inflates reported accuracy. Recommend teaching:

- Blocked or session-wise cross-validation.
- Within-subject versus cross-subject evaluation, and why the latter is much harder.
- Chance-level context — report against a permutation-derived or binomial confidence bound, not naively against 50%.

### 3.4 Referencing and montage
Re-referencing (common average, mastoid, Laplacian) materially changes results, is conceptually accessible, and is currently absent. It belongs in the Preprocessing workshop.

### 3.5 Standardize the software stack
Naming a canonical stack would let each cohort inherit working code rather than rebuild it:

- **MNE-Python** — preprocessing, epoching, visualization
- **scikit-learn** — classification
- **pyriemann** — covariance-based methods
- **BrainFlow / LSL** — acquisition and streaming

### 3.6 Slide deck completeness
Several slides remain placeholders ("add data flow diagram," "insert demo video," blank slides). Instructional quality currently depends heavily on the individual presenter. Building out visual and code content would make material robust and reusable across leads.

### 3.7 Curriculum balance
Preprocessing is fully developed; feature extraction and classification exist largely as outlines. Bringing the later pipeline stages to comparable depth is the clearest path to a balanced curriculum.

---

## 4. The Compounding Problem

CRUX's strongest asset is a well-sequenced curriculum. Its structural weakness is that **nothing accumulates**: no project archive, no shared repository, no in-house dataset. Each cohort's technical work is effectively lost, so the program restarts rather than builds.

The board has determined that project IP belongs to individual members and cannot be retained by the club. That constraint is real but narrower than it may appear — **ownership of intellectual property and retention of institutional knowledge are separable**. Options that respect member ownership:

1. **Metadata-only archive.** Record paradigm, sampling rate, electrode montage, pipeline stages, and a lessons-learned paragraph. No code, no data, no results. This is closer to meeting minutes than to appropriation.
2. **Opt-in licensing.** Members choose at the showcase whether to license their work to the club. An MIT license permits reuse while leaving ownership with the author.
3. **Club-owned canonical dataset.** One afternoon of recorded eyes-open/eyes-closed alpha across board members — club-generated, therefore unencumbered — gives every future workshop real data to demonstrate on and gives new members something to classify by Week 4. This alone would substantially close the gap.

*This is a governance question for the board, and possibly for UCLA's student organization office. It is raised here as an option to consider, not as legal advice.*

---

## 5. Priority Summary for Next Phase

| Priority | Action | Rationale |
| --- | --- | --- |
| High | Record a club-owned canonical EEG dataset | Unblocks demonstrations and member projects; no IP conflict |
| High | Add rigorous validation methodology to WS6 | Highest-credibility gain per hour invested |
| High | Bring feature extraction and classification decks to preprocessing-level depth | Corrects the clearest curriculum imbalance |
| Medium | Add SSVEP as a paradigm | Best first-project on-ramp for new members |
| Medium | Standardize on MNE-Python and publish skeleton code | Enables cohort-to-cohort inheritance |
| Medium | Expand epoching and event-timing content | Addresses the most common silent failure mode |
| Medium | Resolve slide placeholders | Reduces dependence on individual presenters |
| Low | Add re-referencing to Preprocessing | Small addition, real conceptual value |
| Ongoing | Decide board policy on metadata-only project archive | Determines whether knowledge compounds |

---

## 6. Open Questions

- What is meant by "technical overlap" in the current planning discussion — overlap between the biology and coding tracks, between CRUX's curriculum and industry/research expectations, or with another organization's technical scope? Each implies a different deliverable.
- Does a skeleton code repository exist outside the reviewed materials? If so, its state is the most significant unassessed factor in this evaluation.
- Will the biology/coding track split diverge the pipeline, or converge on shared projects?
