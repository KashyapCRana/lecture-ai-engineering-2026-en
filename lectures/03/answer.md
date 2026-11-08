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

**Levels completed:** Basic, Implementation, Advanced (Google ADK and Pi Coding Agent)

### Advanced Option A - Google ADK

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

### Implementation - Learning log with approval

I implemented `save_learning_log` to save learning records as JSON files inside the `learning_log/` folder.

I registered the tool with `requires_approval=True` and updated the CLI to handle `DeferredToolRequests` and `DeferredToolResults`.

I tested it using a LoRA learning note.

**Approval test:**

The agent paused and asked for permission before executing the tool. I answered `y`, and the record was saved successfully in:

`learning_log/20261108T102709Z_7c122325.json`

**Rejection test:**

I repeated the same request and answered `n`. The agent reported that the save operation was denied. I compared the saved files before and after using `diff`, and there were no changes.

The existing automated tests also passed (18 tests).

**Observation:**

One useful detail was that setting `requires_approval=True` alone wasn't enough. The CLI also needs to handle the deferred request and resume execution after receiving the user's decision. This is useful for operations that change files or other persistent data.

### Basic - Instruction change experiment

I compared the agent's behavior before and after changing one instruction.

Original instruction:
`End your answer by indicating the relevant session (Lecture NN).`

Temporary instruction:
`End your answer with one review question for the learner.`

I asked the same question both times: "What is the difference between LoRA and QLoRA?"

| Observation | Original | Modified |
|---|---|---|
| Tool calls | 2 | 2 |
| LLM requests | 2 | 2 |
| Glossary queries | LoRA, QLoRA | LoRA, QLoRA |
| Output tokens | 236 | 214 |
| Ending | Lecture 02 | Review question |

Both traces showed `search_glossary` being called separately for LoRA and QLoRA.

Both runs searched the same glossary terms. The noticeable difference was the ending: one gave the lecture number, while the other asked a review question.

I restored the original instruction after the experiment.

### Advanced Option B - Pi Coding Agent

I installed Pi in Codespaces using:
`npm install -g --ignore-scripts @earendil-works/pi-coding-agent`

I started Pi and selected Gemini 3.5 Flash-Lite. My earlier attempt with Gemini 2.5 Flash had returned a model-availability error.

I asked Pi to describe its available tools without running commands or modifying files. It identified four tools: `read`, `bash`, `edit`, and `write`.

I compared Pi's published `packages/coding-agent/src/core/system-prompt.ts` with the `INSTRUCTIONS` in my `app/agent.py`.

**Similarities:** Both establish the agent's role and provide instructions for using available tools to help the user.

**Pi-specific instructions:** Pi is a general coding assistant. Its default prompt supports inspecting files, executing commands, and modifying code. Its prompt builder also supports project context, tool descriptions, working-directory information, optional skills, concise responses, and clear file paths.

**My agent's instructions:** My agent is specific to AIE2026. It must check the glossary for course terms, retrieve lecture summaries when needed, avoid unsupported guesses, mention the relevant lecture, and guide learners with hints.

**Tools and confirmation:** Pi has general file and shell tools, while my agent has course-specific learning tools. Pi's default system prompt does not impose a universal confirmation requirement, although runtime behavior can depend on configuration. My `save_learning_log` tool explicitly requires approval, which I tested with both `y` and `n`.

I did not ask Pi to edit files or run commands, so my comparison of those abilities is based on its published source and tool descriptions rather than an execution test.

Pi can work directly with a codebase, while my agent mainly helps students understand course material. It only saves learning notes after the user approves.
