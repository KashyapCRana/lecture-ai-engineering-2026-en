# Lecture 01 Answers

## Exercises

- Model's answer to the course-specific question (the 3 homework levels; a summary is fine):
- What you noticed when comparing it with the correct meaning in the glossary:
- Token counts you displayed (input / output):

## Homework

- Level attempted: Basic / Implementation / Advanced
- What you did:
- Results:
- Observations and questions:

# ---------------------------------------------------------------------------------------------------------

# Lecture 01 — Homework

# Part 1: Basic Level — LLM Response Comparison

## 1. Objective

The objective of this experiment was to investigate the consistency, variability, and reliability of Large Language Model (LLM) responses by repeatedly asking identical questions using two different Gemini models.

I evaluated both a general technical question and a course-specific question to understand how models behave when answering familiar topics versus questions requiring specialized information.

## 2. Experimental Setup

**Models evaluated:**
- `gemini-3.5-flash-lite`
- `gemini-3.1-flash-lite`

**Questions:**
1. "What is LoRA?"
2. "What are the 3 homework levels in the AIE2026 course?"

**Experimental configuration:**
- Each question was asked three times per model.
- Total API requests: 12.
- Models were selected using the `AIE_MODEL` environment variable.
- No explicit temperature adjustments were made.
- All experiments were conducted using the `app.ask` application in GitHub Codespaces.

**Example commands:**

```bash
uv run python -m app.ask "What is LoRA?"

AIE_MODEL=gemini-3.1-flash-lite uv run python -m app.ask "What is LoRA?"
```

## 3. Experiment 1 — General Technical Question

**Question:** "What is LoRA?"

### Model A: gemini-3.5-flash-lite

**Run 1:** Explained Low-Rank Adaptation using a library and notebook analogy. Emphasized frozen base weights, parameter efficiency, and adapter swapping.

**Run 2:** Used a textbook and sticky-note analogy. Included additional technical information about low-rank matrices, memory savings, and merging adapter weights.

**Run 3:** Used a library analogy, emphasizing efficient training, compact adapters, and practical applications.

**Observation:**

All three responses consistently explained LoRA as a parameter-efficient fine-tuning method. However, they differed in explanation structure, analogies, supporting examples, and technical details.

### Model B: gemini-3.1-flash-lite

**Run 1:** Explained frozen model weights and adapter training using a textbook and Post-it note analogy. Also discussed catastrophic forgetting.

**Run 2:** Explained low-rank matrices, hardware requirements, modularity, and practical applications.

**Run 3:** Emphasized parameter efficiency, small adapter sizes, and practical applications using a filing-cabinet analogy.

**Observation:**

The fundamental explanation remained consistent across all three runs, but the supporting examples, numerical estimates, and presentation varied.

### Comparison

Both models correctly described the central concept of LoRA: keeping pretrained model weights frozen while training a smaller number of parameters represented through low-rank updates.

However, the responses varied in their level of detail, explanation styles, numerical estimates, and illustrative analogies.

Some responses also made broad claims about hardware requirements, parameter percentages, and catastrophic forgetting. These claims depend on the specific model and implementation and should not be treated as universally applicable without verification.

**Key finding:** Even when the fundamental answer is correct, repeated generations can produce different explanations and supporting claims.

---

## 4. Experiment 2 — Course-Specific Question

**Question:** "What are the 3 homework levels in the AIE2026 course?"

The correct answer was verified using the `homework-levels` entry in `data/glossary.json`.

**Ground-truth answer:**
1. Basic — Review lecture content
2. Implementation — Write your own code
3. Advanced — Research and experimentation

### Model A: gemini-3.5-flash-lite

**Run 1:** Explicitly stated that it did not have access to the AIE2026 course syllabus and could not reliably identify the homework levels.

**Run 2:** Again acknowledged that it lacked the specific course information and could not provide a reliable answer.

**Run 3:** Generated a plausible but incorrect structure with Foundation/Basics, Application/Intermediate, and Mastery/Advanced levels. It also suggested alternative names without evidence.

**Observation:**

The model appropriately expressed uncertainty in two runs but generated unsupported course-specific details in the third run.

### Model B: gemini-3.1-flash-lite

**Run 1:** Incorrectly identified AIE2026 as "Artificial Intelligence for Everyone 2026" and invented Conceptual, Applied, and Technical levels.

**Run 2:** Generated a different structure consisting of Core/Foundational, Applied/Intermediate, and Advanced/Research & Innovation levels.

**Run 3:** Generated another unsupported structure consisting of Concept Checks, Implementation Exercises, and Application/Project Tasks.

**Observation:**

All three responses generated plausible but incorrect descriptions rather than reproducing the official homework-level names and definitions.

### Comparison and Hallucination Analysis

| Evaluation | Gemini 3.5 Flash Lite | Gemini 3.1 Flash Lite |
|---|---|---|
| Runs expressing uncertainty | 2/3 | 0/3 |
| Runs generating unsupported course-level descriptions | 1/3 | 3/3 |
| Runs accurately identifying the official three levels | 0/3 | 0/3 |

These observations are specific to the six recorded calls and should not be interpreted as a general benchmark of either model.

The experiment demonstrated an important limitation of bare LLMs: they may generate convincing answers even when they lack reliable information about a particular course.

This behavior illustrates the problem of **LLM hallucination**, where generated text appears credible but contains unsupported or incorrect information.

The experiment also reinforced the importance of verifying answers against authoritative sources instead of relying solely on the apparent confidence or fluency of generated text.

## 5. Challenges and Lessons Learned

The main challenge was distinguishing a plausible explanation from a verified, accurate answer.

For general technical questions, both models provided useful explanations, but their supporting details varied.

For course-specific questions, some responses fabricated information rather than acknowledging uncertainty.

I learned how to:
- Configure and run an LLM application using GitHub Codespaces.
- Securely access the Gemini API through environment variables.
- Switch models using the `AIE_MODEL` variable.
- Conduct repeated experiments with identical questions.
- Compare outputs against trusted reference information.
- Identify response variability, uncertainty, and hallucinations.

## 6. Basic Level Conclusion

Across 12 experiments involving two models and two questions, I observed that LLM responses can vary even when the input remains identical.

The general technical question produced broadly consistent explanations, while the course-specific question exposed limitations in model knowledge and factual reliability.

The central lesson is that AI outputs should be systematically evaluated for accuracy, consistency, and usefulness rather than judged only by their fluency.

---

# Part 2: Implementation Level — Multi-Turn Conversation

## 1. Objective

Extend `app/ask.py` to support follow-up questions while preserving conversation history across multiple interactions.

The goal was to transform the original single-question application into an interactive, context-aware conversation interface.

## 2. Implementation Details

I extended the existing Google GenAI SDK application by introducing an interactive `--chat` command-line option.

The implementation includes:

1. **Interactive conversation mode:** Users can enter multiple questions in a single session.

2. **Conversation history:** Both user messages and model responses are retained in an in-memory history.

3. **Context preservation:** Previous successful messages are included in subsequent Gemini API requests.

4. **Session termination:** Users can exit the interactive session by entering `exit` or `quit`.

5. **API error handling:** API errors are handled without discarding the previously successful conversation history.

6. **Backward compatibility:** The original single-question command remains available.

The conversation history is stored in memory during the running session and is not persisted across application restarts.

**Command:**

```bash
uv run python -m app.ask --chat
```

## 3. Verification — Multi-Turn Conversation

I tested the implementation using the following conversation:

**User:** What is LoRA?

**Gemini:** Explained Low-Rank Adaptation and its applications.

**User:** Explain it using a simple real-world analogy.

**Gemini:** Provided a master-chef analogy relating LoRA adapters to a recipe cheat sheet.

**User:** What was the first question I asked you?

**Gemini:** "The first question you asked was: **What is LoRA?**"

**User:** exit

### Result

The application successfully maintained conversation context across multiple turns.

In particular, Gemini correctly recalled the first user question without that question being repeated in the final prompt.

This provided direct evidence that previous conversation messages were retained and supplied to subsequent model requests.

## 4. Additional Exercise — Token Usage Tracking

I also modified the original `ask()` function to display input and output token counts using the Gemini API response metadata.

The implementation uses:

- `response.usage_metadata.prompt_token_count`
- `response.usage_metadata.candidates_token_count`

It also handles missing usage metadata without crashing.

**Verified example:**

| Metric | Value |
|---|---|
| Model | gemini-3.5-flash-lite |
| Question | What is LoRA? |
| Input tokens | 6 |
| Output tokens | 758 |

These figures represent one observed API request, not an average across experiments.

This modification helped demonstrate how token usage can be inspected when developing LLM applications.

## 5. Testing and Validation

The updated application was tested using the repository's automated test suite.

**Test command:**

```bash
uv run pytest -q
```

**Result:**

```text
14 passed, 1 warning in 3.87s
```

The tests passed successfully.

A deprecation warning originated from the Google GenAI dependency under Python 3.14. It did not cause test failures.

The following additional validation command also completed without reporting whitespace errors:

```bash
git diff --check
```

The implementation was further verified through a live interactive conversation with Gemini.

## 6. Challenges and Lessons Learned

The key challenge was maintaining a consistent conversation history while preserving the original single-question behavior.

I learned that multi-turn conversations require explicitly preserving and supplying previous messages to the model. Without this history, independent API requests do not automatically retain earlier context.

I also learned the importance of safely handling API errors, inspecting token usage, reviewing AI-generated code, and validating changes through automated tests and actual application behavior.

## 7. Implementation Conclusion

The implementation successfully extended the original single-question application into a multi-turn conversational interface.

It supports follow-up questions, retains conversation history during a session, handles API errors, and preserves the existing command-line functionality.

The successful memory-recall test and passing automated tests provide evidence that the implemented features work as intended.

---

# Overall Conclusion

Lecture 01 provided practical experience in LLM experimentation, AI-assisted coding, API integration, and GitHub-based development.

The Basic experiments demonstrated response variability, hallucinations, and the importance of verification against trusted information.

The Implementation assignment demonstrated how maintaining conversation history enables context-aware follow-up questions.

Together, these exercises reinforced three important AI engineering principles:

1. Evaluate model outputs rather than assuming they are correct.
2. Design applications that manage context and API interactions deliberately.
3. Verify AI-assisted code through tests and actual execution.

**Homework levels completed: Basic and Implementation.**

**Additional exercise completed: Input and output token-count display.**