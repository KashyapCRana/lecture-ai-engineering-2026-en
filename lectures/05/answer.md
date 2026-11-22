# Lecture 05 Answers

## Exercises

For this lecture, I compared four approaches for answering questions using the course materials: Full Context, Vector Search, Tree Search, and Graph Search.

The question I used was:

**In Lecture 02, what does LoRA freeze and what does it train? What does QLoRA add?**

I ran the experiments in GitHub Codespaces using Python 3.12.16. Initially, Python 3.14 caused an issue with SQLite extension loading, so I switched to Python 3.12.

The Vector, Tree, and Graph methods use 214 indexed pages from Lectures 01–03. Full Context includes 398 pages across eight documents, so its input materials are not exactly the same.

### Results

These are the successful results using `gemini-3.1-flash-lite`.

| Method | Time | Input / Output Tokens | Estimated Cost (USD) |
|---|---:|---:|---:|
| Vector Search | 5.15 s | 2,759 / 242 | $0.001053 |
| Tree Search | 7.66 s | 9,442 / 310 | $0.002826 |
| Graph Search | 4.88 s | 5,190 / 275 | $0.001710 |
| Full Context | HTTP 503 | N/A | N/A |

All three successful methods answered the question correctly.

LoRA freezes the original model weights and trains two small matrices, A and B. QLoRA additionally uses 4-bit quantization for the frozen base weights to reduce memory requirements.

Vector Search retrieved the relevant material directly, including Lecture 2 pages 51 and 52. Page 52 explains both LoRA and QLoRA.

Tree Search navigated through the lecture structure until it reached page 52. It worked, but required four tool calls and more input tokens.

Graph Search also found the required information by starting with vector results and following relationships between pages.

One thing I noticed was that retrieving the correct page did not always mean the model would explicitly cite it. Some answers were correct but did not include the expected page reference.

Full Context returned an HTTP 503 error with Gemini 3.1. I had also tested it earlier using `gemini-3.5-flash-lite`, which completed successfully:

| Method | Time | Input / Output Tokens | Estimated Cost (USD) |
|---|---:|---:|---:|
| Full Context (Gemini 3.5) | 3.91 s | 95,824 / 258 | $0.029392 |

The answer was correct, but the input was much larger. Since this run used a different model and a broader collection of documents, I did not treat it as a direct same-model comparison.

For a straightforward question like this, I would choose Vector Search. It found the necessary evidence without needing to process much additional material.

## Homework

**Levels attempted: Implementation and Advanced**

### Implementation: Adjacent-Page Retrieval

For the Implementation homework, I modified `app/retrieval.py` to support retrieving adjacent pages along with the original vector search results.

Normally, Vector Search returns the five most similar pages. My implementation also retrieves the page immediately before and after each result, as long as they belong to the same document.

I used the existing page metadata from `load_pages()` to identify neighboring pages. I also made sure that duplicate pages were not returned, document boundaries were respected, and the original page content and citation metadata were preserved.

I kept the existing `search()` function unchanged so that I could compare the original and modified methods.

Since the underlying documents and embeddings were not changed, I did not need to rebuild the vector index.

I also added tests for adjacent-page expansion, duplicate removal, document boundaries, and invalid radius values.

#### Implementation Results

I tested three questions using `gemini-3.1-flash-lite`.

| Question | Method | Time | Input Tokens | Estimated Cost (USD) |
|---|---|---:|---:|---:|
| LoRA / QLoRA | Basic RAG | 5.15 s | 2,759 | $0.001053 |
| LoRA / QLoRA | Adjacent RAG | 7.88 s | 5,015 | $0.001677 |
| Compaction vs Memory | Basic RAG | 8.53 s | 4,002 | $0.001542 |
| Compaction vs Memory | Adjacent RAG | 4.56 s | 8,216 | $0.002573 |
| Unanswerable question | Basic RAG | 3.75 s | 2,886 | $0.001076 |
| Unanswerable question | Adjacent RAG | 5.40 s | 5,813 | $0.001962 |

Both approaches answered all three questions appropriately. For the unanswerable question about measured RAG performance, neither invented measurements that were missing from the lecture materials.

The main difference was the context size. Adjacent-page retrieval provided more information, but it also increased token usage and cost.

I did not observe an improvement in answer correctness for these three questions because the original vector results already contained the necessary information.

For example, in the compaction and memory question, Basic RAG had already retrieved the pages needed to explain the difference. Adding neighboring pages did not provide a clear benefit.

I think adjacent-page retrieval would be useful when an explanation continues onto another page. However, automatically adding adjacent pages to every search can introduce unnecessary information.

These were individual model runs, and the agent sometimes generated different search queries. Because of that, I would not draw strong conclusions from the response-time differences alone.

### Advanced: Combining Vector, Tree, and Graph Retrieval

For the Advanced homework, I wanted to test whether combining retrieval methods could help with questions that require information from different sections or lectures.

I implemented a Hybrid RAG approach in `app/lec05_hybrid.py`.

The method starts with normal Vector Search and then uses the Tree and Graph structures to find additional potentially relevant pages.

The retrieval process is:

1. Find the five most similar pages using Vector Search.
2. Consider neighboring pages using the adjacent-page method.
3. Use the Tree structure to find related pages within sections.
4. Follow Graph relationships to discover pages connected through neighboring pages or shared terms.
5. Remove duplicate candidates and rank the remaining pages.
6. Select pages within the configured context budget.

The implementation reuses the existing SQLite vector index, `tree.json`, and `graph.json`.

I limited Graph traversal by hop count and visited nodes to prevent the search from expanding indefinitely.

For the initial experiments, the Hybrid method selected at most ten pages, with a maximum serialized context size of 14,000 characters.

#### Initial Hybrid Results

I first tested the same three questions using `gemini-3.1-flash-lite`.

| Question | Time | Input Tokens | Estimated Cost (USD) |
|---|---:|---:|---:|
| LoRA / QLoRA | 4.32 s | 4,359 | $0.001433 |
| Compaction vs Memory | 9.49 s | 4,064 | $0.001662 |
| Unanswerable question | 5.38 s | 4,225 | $0.001472 |

Hybrid RAG answered all three questions appropriately.

It used fewer tokens than Adjacent RAG on these examples, although Basic RAG was still cheaper.

I also noticed that Graph expansion could generate many candidates. For the LoRA question, approximately 94 candidate pages were considered, even though only a small number were returned.

This made me realize that ranking the candidates was just as important as discovering them.

### Evaluation and Ablation Experiments

To test the retrieval methods more systematically, I created ten evaluation questions in `lectures/05/eval_questions.json`.

The questions covered single-page information, multiple pages, adjacent pages, cross-section information, cross-lecture information, and one unanswerable case.

I inspected the lecture materials and selected expected supporting page IDs before running the comparisons.

I then compared eight retrieval configurations using fixed question-specific retrieval queries and the same initial vector results.

| Retrieval Method | Questions with All Expected Evidence |
|---|---:|
| Vector Only | 8/9 |
| Vector + Adjacent | 8/9 |
| Vector + Tree | 8/9 |
| Vector + Graph | 9/9 |
| Full Hybrid | 9/9 |
| Hybrid without Adjacent | 9/9 |
| Hybrid without Tree | 9/9 |
| Hybrid without Graph | 8/9 |

The unanswerable question was excluded from the evidence-recall calculation because it had no expected supporting pages.

The most interesting result came from Q06:

**Why are a few successful outputs and public model rankings insufficient for evaluating an AI system?**

This question required information from two different lectures:

- `lec01-main-p035`: Why testing only a few successful outputs is insufficient.
- `lec02-main-p039`: Why public benchmarks do not necessarily reflect performance on a specific use case.

Basic Vector Search retrieved the first page but missed the second.

The Hybrid method retrieved both pages. When I disabled Graph expansion, the second page was missing again.

This was the clearest case where Graph retrieval found useful evidence that the other approaches missed.

#### Generated Answer Comparison for Q06

I also compared the actual answers using the same question, a fixed retrieval query, and `gemini-3.1-flash-lite`.

| Method | Evidence Retrieved | Time | Input Tokens | Estimated Cost (USD) |
|---|---:|---:|---:|---:|
| Vector Only | 1/2 | 4.53 s | 2,008 | $0.001371 |
| Vector + Adjacent | 1/2 | 4.51 s | 3,778 | $0.001858 |
| Hybrid | 2/2 | 4.52 s | 3,727 | $0.001886 |
| Hybrid without Graph | 1/2 | 4.47 s | 3,657 | $0.001589 |

The Hybrid answer was more complete.

It explained why checking a few successful outputs is insufficient, but also covered the limitations of public benchmarks, such as different evaluation conditions and the possibility that benchmark questions were included in model training.

It cited Lecture 2 page 39, which the other configurations had not retrieved.

However, this improvement required additional tokens and generation cost compared with Basic Vector Search.

The response times were similar in these individual runs, so I cannot conclude that any method was consistently faster.

### Improving the Hybrid Ranking

While inspecting Q06, I noticed another issue.

The Hybrid method successfully discovered Lecture 2 page 39, but initially ranked it tenth.

This meant that when I reduced the context budget, that important page was removed from the final results.

I inspected the candidate scores and found that page 39 matched several query terms in its title, even though it ranked below some pages with fewer relevant terms.

To address this, I modified the ranking to consider matches in page titles more strongly.

I added a bonus of 12 points for each query term appearing in the page title. This was an experimental heuristic rather than a parameter selected through an independent optimization procedure.

I then used Gemini's `count_tokens` API to measure retrieval-context tokens and repeated the Q06 experiment under three token caps.

#### Q06 Token-Budget Results

| Maximum Retrieval Tokens | Original Hybrid Ranking | Updated Hybrid Ranking |
|---|---|---|
| 1,600 | 1/2 evidence pages | 2/2 |
| 2,200 | 1/2 | 2/2 |
| 3,200 | 2/2 | 2/2 |

With the updated ranking, Hybrid retrieved both expected evidence pages at the 1,600-token cap, using 1,534 actual retrieval tokens.

Before the change, it needed a much larger context budget to retain the same evidence.

I also reran the ten-question retrieval experiment after changing the ranking. The updated Hybrid method still retrieved all expected evidence pages for the nine answerable questions.

I did not observe a reduction in evidence recall on this evaluation set.

This experiment helped me understand that a retrieval method can discover the correct information and still fail to deliver it to the model if the ranking is poor.

The token limits were equal maximum budgets, not identical actual token usage. Also, these measurements only counted the retrieval payload, not the entire agent conversation.

### Limitations

There are several limitations to these experiments.

First, the evaluation set contained only ten questions. It was useful for comparing the implementations, but it is too small to establish that one method is generally better.

Second, most answer-generation comparisons were performed only once per configuration. Model output, latency, and cost can vary across repeated runs.

Third, the title-matching weight was chosen after inspecting Q06. The improvement is therefore demonstrated on the development questions, not on a separate unseen test set.

Graph expansion can also introduce irrelevant pages because two pages sharing a term do not necessarily contain related answers.

In addition, the estimated generation costs exclude query embeddings and index construction.

Some Full Context and Tree experiments returned HTTP 503 errors. I treated these as service errors rather than retrieval failures.

Finally, Full Context included more documents than the retrieval-based methods, so its results should not be treated as a perfectly controlled comparison.

### What I Learned

The biggest thing I learned from this homework is that retrieving more pages does not automatically improve an answer.

For simple questions, Basic Vector Search worked well and was relatively inexpensive.

Adjacent-page retrieval was easy to implement and may help when information continues across pages, but in my initial experiments it mostly increased the amount of context.

Graph retrieval was more useful for a question that required connecting information from two different lectures.

I also found that improving the ranking was important. In Q06, the Hybrid method already discovered the missing evidence, but it was ranked too low to survive a smaller context budget.

After adding title-aware ranking, the method retained that evidence with fewer retrieval tokens.

For this course-material chatbot, I would prefer Basic Vector Search for straightforward questions and consider Hybrid retrieval for questions involving multiple sections or lectures.

I would want to test the approach on more unseen questions before using it as the default for every query.

### Verification

I ran the automated tests after integrating the Implementation changes into `app/retrieval.py`.

The final test suite contained 33 passing tests:

- 24 original course tests.
- 3 adjacent-page retrieval tests.
- 6 Hybrid retrieval tests.

I also checked the retrieval results against the actual lecture pages and saved the experimental measurements in the `lectures/05` directory.

The code, evaluation scripts, tests, and recorded results are included in the `lec05` branch.

I used AI assistance during development, but ran the experiments, inspected the outputs, and verified the results in my GitHub Codespace.
