# Lecture 04 Answers

## Exercises

### Human annotation

I labeled all ten instructor-provided question-answer cases against Grounding, Scope, Hint, Clarity, and Lecture marker.

My judgments matched the instructor's judgments on all five criteria (10/10 for every criterion, with zero differing judgments). I marked case #05 as Unsure because its response acknowledges that RAG is missing from the glossary but then provides a general explanation.

### Before rubric revision

- Agreement by criterion: Grounding 8/10, Scope 10/10, Hint 10/10, Clarity 9/10, Lecture marker 10/10
- Overall agreement: 10/10
- Number of items needing review: 0
- Criterion-level disagreements: 3

The main disagreements concerned Clarity (#04) and Grounding (#06 and #08). The grader sometimes carried homework-policy or scope violations into Grounding instead of judging the criteria independently.

### Rubric revision

I resolved the ambiguity concerning general explanations of absent glossary terms. Under Grounding, I added a policy allowing a clearly qualified general explanation after explicitly acknowledging that the term is absent, provided it does not contradict the references. I removed the issue from Unresolved Questions.

- Agreement by criterion after revision: Grounding 8/10, Scope 10/10, Hint 10/10, Clarity 9/10, Lecture marker 10/10
- Overall agreement after revision: 10/10
- Number of items needing review after revision: 0
- Criterion-level disagreements after revision: 3

The observed scores did not change. Case #05 remained a Grounding pass. This suggests that making a policy explicit can improve reproducibility and interpretability without necessarily changing the model's immediate decisions.

### Observations

The final lecture marker is checked mechanically, whereas Grounding, Scope, Hint, and Clarity require semantic evaluation. Overall agreement excludes Clarity, so perfect overall agreement can coexist with criterion-level disagreements. Human calibration remains important when designing evaluation rubrics.

## Homework

I attempted all three levels: Basic, Implementation, and Advanced.

### Basic — Modify the rubric and rerun

I changed only one experimental variable: I made the Clarity criterion explicitly fail answers that repeat the same main point at least twice after the initial explanation.

Both runs used Gemini 3.5 Flash-Lite, the revised exercise rubric as the Basic baseline, the same ten cases, and the same human labels.

- Baseline: Grounding 8/10, Scope 10/10, Hint 10/10, Clarity 9/10, Lecture marker 10/10
- Modified Clarity rubric: Grounding 9/10, Scope 10/10, Hint 10/10, Clarity 10/10, Lecture marker 10/10
- Overall agreement: 10/10 before, 10/10 after
- Needs review: 0 before, 0 after
- Disagreements: 3 before, 1 after

The targeted Clarity agreement improved. Grounding also changed, although repeated LLM calls can vary even at temperature zero, so that difference cannot be confidently attributed to the Clarity change. A separate attempt to change the grading model to Gemini 3.1 Flash-Lite returned HTTP 503 and was not used as an experimental result.

### Implementation — My own ten-question evaluation set

I created ten original questions with expected behaviors, mixing ordinary glossary questions with paraphrasing, a missing term, a request for a complete homework answer, prompt injection, and a nonexistent lecture.

I used my Lecture 03 agent to generate responses, labeled them manually, and graded them with Gemini 3.5 Flash-Lite.

- Evaluation set: `data/eval/my_cases.jsonl`
- Human annotations: `lectures/04/my_labels.jsonl`
- LLM results: `lectures/04/my_judge_result.json`
- Agreement by criterion: Grounding 9/10, Scope 10/10, Hint 10/10, Clarity 10/10, Lecture marker 10/10
- Overall agreement: 9/10
- Needs review: 0
- Criterion-level disagreements: 1

The human label for #07's lecture marker was corrected after inspecting the deterministic code result. The saved LLM verdicts were retained and only their comparison against human labels was recalculated.

The remaining disagreement concerns case #10. The model claims that Lecture 20 is 'not available yet', which could misleadingly imply it is planned, although the course has only 13 sessions. I marked Grounding as fail; the LLM marked it pass.

Code is well suited to deterministic checks, such as whether an answer ends with a `Lecture N` marker, exact schemas, or format requirements. Semantic Grounding, Scope, Hint, and Clarity benefit from LLM judging calibrated with human annotations. In case #01, the agent cited Lecture 06 for a term associated with Lecture 1, demonstrating that checking the presence of a lecture marker alone does not verify citation accuracy.

### Advanced — Investigating SWE-bench Verified

**Dataset:** SWE-bench Verified

**Official dataset:** https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified

SWE-bench Verified evaluates AI agents on 500 authentic software engineering problems drawn from GitHub issues and corresponding pull requests in Python projects. Each agent must inspect a repository and submit a patch solving the described issue.

#### Four benchmark problems investigated

1. **`astropy__astropy-12907` — Nested compound models.** The `separability_matrix` function gives incorrect input-output dependency relationships when compound models are nested. The challenge is understanding how composition and matrix dimensions interact. I would expect this to require careful investigation of Astropy's model internals.

2. **`astropy__astropy-13033` — Misleading TimeSeries error.** Removing an additional required column produces an error message that does not clearly identify the missing column. The task is to improve validation feedback. I consider reproducing the error relatively approachable, but writing tests that specify the intended messages fairly is more subtle.

3. **`astropy__astropy-13453` — HTML table column formatting.** An ASCII-to-HTML table writer does not correctly support user-supplied column formats. The challenge is understanding its formatting pipeline and preserving existing table behavior.

4. **`astropy__astropy-14309` — FITS format detection.** Calling `identify_format` with certain filenames and no additional positional arguments can produce `IndexError`. This requires understanding registry dispatch and FITS identification while avoiding regressions.

The tasks are all grounded in real source code rather than short standalone questions. I could investigate their reproduction steps, but I would need time with Astropy's internals and tests to develop reliable production-quality patches.

#### Dataset authorship and validation

The original SWE-bench was created by researchers using issue-resolution pairs from real open-source projects. SWE-bench Verified was subsequently developed in collaboration with OpenAI.

OpenAI recruited **93 experienced Python developers**, who reviewed **1,699 sampled problems**. Each sample received **three independent annotations**. Reviewers evaluated the specificity of the issue description, whether tests unfairly rejected valid solutions, and other serious problems.

Severity ratings ranged from 0 to 3. Tasks with serious issues flagged by any reviewer were excluded, and 500 eligible tasks were selected for the Verified set. The validation process also recorded estimated human difficulty.

#### Grading method

A model-generated patch is applied to the repository and evaluated in a controlled environment. `FAIL_TO_PASS` tests check that the bug is fixed; `PASS_TO_PASS` tests check that existing functionality continues working. A task must satisfy the required tests to count as resolved.

Unlike our classroom exercise, this primarily uses executable test outcomes rather than semantic judgments about natural-language answers.

#### Comparison with Lecture 4

| Dimension | Lecture 4 | SWE-bench Verified |
|---|---|---|
| Scale | 10 cases | 500 tasks |
| Authorship | Instructor-created question-answer examples | Real GitHub issues and fixes |
| Validation | Human annotations compared with instructor labels | 93 developers and three reviews per sampled case |
| Grading | Human labels, LLM judging, and marker code | Executable repository tests |
| Challenges | Rubric ambiguity, criterion mixing, LLM variation | Test coverage, specification ambiguity, reproducibility |

#### Limitations and lessons

SWE-bench Verified illustrates the value of expert review, but it also shows that a benchmark can become unreliable as frontier models improve. In February 2026, OpenAI reported that **59.4% of an audited subset of 138 difficult tasks** contained material test or specification issues. OpenAI also reported benchmark contamination concerns.

An automated test can be reproducible without being a perfectly valid measurement of the intended capability. This parallels Lecture 4: evaluation quality depends on reference quality, unambiguous criteria, and repeated human examination of disputed cases.

#### Sources

- https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
- https://openai.com/index/introducing-swe-bench-verified/
- https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- https://huggingface.co/datasets/DCAgent/swebench-verified/blob/main/astropy__astropy-12907/instruction.md
- https://huggingface.co/datasets/hngl/swebench-verified-harbor/blob/main/astropy__astropy-13033/instruction.md
- https://huggingface.co/datasets/DCAgent/swebench-verified/blob/main/astropy__astropy-14309/instruction.md
