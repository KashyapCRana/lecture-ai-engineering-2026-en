# Lecture 03 Answers

## Exercises

**Differences between the plain LLM and the agent:**

I tried asking both the same question about the three homework levels.

The plain LLM couldn't answer because it didn't have information about this specific course. However, the agent correctly answered Basic, Implementation, and Advanced. This helped me understand why giving an LLM access to external information through tools is useful.

**Tool calls observed with `--trace`:**

For the LoRA vs QLoRA question, I got these calls:

- `search_glossary({'query': 'LoRA'})`
- `search_glossary({'query': 'QLoRA'})`

There were 2 tool calls and 2 LLM requests. I noticed that the agent searched the two terms separately, which makes sense because the tool description says to search one term at a time.

**Tool added:**

I implemented `make_quiz(lecture: int)` in `app/tools.py` and registered it in `app/agent.py`.

It selects a random glossary term from the requested lecture and returns a question with its answer. I also handled the case where no terms are found.

The docstring explains that this tool should be used when a learner asks for a review question or quiz.

I tested it using "Give me one review question from Lecture 02". The trace showed `make_quiz({'lecture': 2})`, and the agent generated a question about Pretraining with a hint.

All 18 tests passed.

## Homework

**Level: Advanced (Option A - Google ADK)**

**What I did:**

I recreated the learning support agent using Google ADK. I created the agent files under `adk_agent/glossary_agent/` and reused the same instructions and three tools from the Pydantic AI implementation.

In Pydantic AI, tools are registered using `agent.tool_plain()`, whereas in ADK, I passed the functions directly through the `tools` argument. ADK also uses `root_agent`, and I ran it using the `adk run` command.

**Results:**

I tested both agents with the same three questions.

| Question | Pydantic AI | Google ADK |
|---|---|---|
| Three homework levels | Correct | Correct |
| LoRA vs QLoRA | Correct explanation | Correct explanation |
| Lecture 02 review question | Pretraining | Fine-tuning |

Both agents gave similar answers for the first two questions. For the quiz, they selected different terms, which is expected since `make_quiz` uses random selection.

The ADK agent ran successfully without errors. Unlike the Pydantic AI CLI with `--trace`, the ADK terminal output didn't show the individual tool calls, so I couldn't compare their exact call counts.

**Observations and questions:**

The main thing I learned was that the same instructions and tools can be reused with different agent frameworks without changing the underlying functionality.

I found Pydantic AI's trace output helpful for understanding which tools the model called. ADK was also straightforward to set up, especially with the interactive CLI.

I would be interested in comparing their execution time and token usage more carefully. The answers were similar in my tests, but I don't think these few questions are enough to say which framework performs better.

I used AI assistance while working on the code and write-up, and verified the reported behavior by running the commands and tests in Codespaces.
