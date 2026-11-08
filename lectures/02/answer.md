# Lecture 02 Answers

## Exercises

### Model and Settings Used

- **Base model:** `Qwen/Qwen3.5-0.8B`
- **Model revision:** `2fc06364715b967f1860aea9cf38778875588b17`
- **Training method:** LoRA (without quantization)
- **Environment:** Google Colab with NVIDIA Tesla T4 GPU
- **LoRA rank (`lora_r`):** 16
- **LoRA alpha (`lora_alpha`):** 32
- **Learning rate (`lr`):** `2e-4`
- **Training epochs (`num_train_epochs`):** 20
- **Random seed:** 42
- **Warmup steps:** 6
- **Maximum sequence length:** 512
- **Maximum new tokens:** 96
- **Generation:** Greedy decoding (`do_sample=False`)
- **Training examples:** 14
- **Evaluation questions:** 21
- **Trainable parameters:** 6,389,760 out of 758,782,784 (0.8421%)
- **Training steps:** 40
- **Training time:** 229 seconds
- **Final logged training loss:** 0.013986

### Did You Run Training Yourself?

**Yes (`executed_training_myself=True`).**

I personally executed the Google Colab notebook using a T4 GPU, completed the LoRA training, and evaluated the model before and after fine-tuning.

I also completed the knowledge-question evaluation and the optional 4-bit quantization experiment.

### Before and After Training

The original model was evaluated on 21 held-out questions before and after 20 epochs of LoRA fine-tuning.

| Metric | Before Training | After Training |
|---|---:|---:|
| Evaluation questions | 21 | 21 |
| Format compliance (`format_rate`) | 9.52% (2/21) | 100% (21/21) |
| Content accuracy (`content_rate`) | 0% (0/21) | 90.48% (19/21) |
| Both format and content correct | 0% (0/21) | 90.48% (19/21) |
| Evaluation duration | 44.0 s | 48.1 s |

**Observations:**

Fine-tuning substantially improved the model's ability to produce valid JSON responses containing exactly the required `answer` and `needs_review` fields.

Format compliance increased from 9.52% to 100%, while content accuracy improved from 0% to 90.48%.

However, two evaluation questions remained incorrect despite the model producing correctly formatted JSON.

### Questions That Regressed

**None.**

The notebook reported `regressed=[]`, meaning no questions previously correct in the untrained evaluation became incorrect after training.

### Remaining Failures After Training

The 20-epoch model achieved perfect format compliance but made two content errors.

1. **Grade publication date:** When asked when grades would be released, the model incorrectly returned the assignment submission deadline. The FAQ did not specify a grade publication date, so the correct behavior was to request confirmation by setting `needs_review=true`.

2. **Office-hours reservation requirement:** When asked whether office hours required advance reservations, the model referred to the office-hours schedule and set `needs_review=false`. However, the FAQ only specified the schedule and did not state whether reservations were required.

Both failures demonstrate **unsupported assertions**, where the model used related but insufficient information from the FAQ.

There were no remaining JSON-format failures in the 20-epoch evaluation.

### Results of Knowledge Questions (Section 6)

The knowledge-question evaluation tested whether the model could recognize information absent from the FAQ.

| Question | Before Training | After 20 Epochs |
|---|---|---|
| Final assignment deadline (not in FAQ) | Format error | Unsupported assertion |
| Instructor's name (not in FAQ) | Format error | Requested review |
| Next lecture topic (not in FAQ) | Format error | Requested review |
| Assignment submission deadline (control) | Format error | Direct answer |

**Observations:**

The fine-tuned model learned to generate the required JSON structure and correctly requested confirmation for some questions whose answers were missing from the FAQ.

However, it continued to incorrectly assert that the final assignment deadline was the same as the ordinary assignment submission deadline.

This showed that learning the output format did not guarantee that the model could reliably distinguish supported facts from unsupported assumptions.

The FAQ dates and administrative information used in this experiment were fictional and should not be interpreted as actual course information.

### What Changed and What Stayed the Same?

**What improved:**

- JSON-format compliance increased from 9.52% to 100%.
- Content accuracy increased from 0% to 90.48%.
- The model generated the expected `answer` and `needs_review` fields more consistently.
- Answers became more closely aligned with the training examples and fictional FAQ.

**What did not fully improve:**

- The model occasionally answered questions without sufficient supporting evidence.
- It sometimes confused related FAQ facts with answers to different questions.
- The ability to recognize unsupported questions remained imperfect.

**Conclusion:**

LoRA fine-tuning was highly effective at teaching the desired response format, but it did not guarantee factual reliability or correct uncertainty handling.

This highlights the importance of evaluating format compliance and content accuracy separately.

---

## Homework

### Level Attempted

**Basic**

### Settings or Data Changed

I investigated the effect of reducing the number of training epochs while keeping the remaining training and evaluation conditions unchanged.

I modified exactly one parameter in `CONFIG`:

- **Original:** `num_train_epochs=20`
- **Modified:** `num_train_epochs=10`

All other important settings were preserved.

| Parameter | Original | Modified |
|---|---|---|
| Base model | Qwen3.5-0.8B | Qwen3.5-0.8B |
| `num_train_epochs` | 20 | 10 |
| `lora_r` | 16 | 16 |
| `lora_alpha` | 32 | 32 |
| `lr` | `2e-4` | `2e-4` |
| `seed` | 42 | 42 |
| `warmup_steps` | 6 | 6 |
| `max_seq_len` | 512 | 512 |
| Evaluation questions | 21 | 21 |
| Generation sampling | Disabled | Disabled |

Before conducting the second experiment, I restarted the Google Colab session and reran the notebook from the beginning.

This ensured that the modified experiment did not inherit the LoRA adapter trained in the original experiment.

### Results: Comparison of 20 and 10 Training Epochs

Both experiments used the same evaluation questions and generation settings.

| Metric | Baseline: 20 Epochs | Modified: 10 Epochs |
|---|---:|---:|
| Training steps | 40 | 20 |
| Training time | 229 s | 116 s |
| Final logged training loss | 0.013986 | 0.097288 |
| Before-training format rate | 9.52% | 9.52% |
| Before-training content rate | 0% | 0% |
| After-training format rate | 100% (21/21) | 100% (21/21) |
| After-training content rate | 90.48% (19/21) | 80.95% (17/21) |
| Questions correct in both format and content | 19/21 | 17/21 |
| Regressions vs. respective untrained model | 0 | 0 |

### Analysis of Results

**1. Effect on format compliance**

Both configurations achieved 100% JSON-format compliance.

This indicates that, for this small training dataset and the evaluated questions, 10 epochs were sufficient for the model to learn the required two-field JSON response structure.

Increasing training to 20 epochs did not produce any additional improvement in this particular metric.

**2. Effect on content accuracy**

The original 20-epoch model achieved 90.48% content accuracy, correctly answering 19 out of 21 questions.

The modified 10-epoch model achieved 80.95%, correctly answering 17 out of 21 questions.

Reducing training from 20 to 10 epochs therefore decreased content accuracy by approximately **9.52 percentage points**, equivalent to two additional incorrect answers.

This suggests that additional training helped the model learn more of the desired answer behavior, even after JSON-format compliance had reached 100%.

**3. Effect on training loss**

The final logged training loss increased from:

- **20 epochs:** 0.013986
- **10 epochs:** 0.097288

The lower loss in the 20-epoch experiment is consistent with the model receiving more optimization steps and fitting the small training dataset more closely.

However, lower training loss alone does not prove better generalization. Held-out evaluation results are necessary to assess whether the additional training improved actual performance.

**4. Effect on training time**

Training time decreased from 229 seconds to 116 seconds.

This represents a reduction of 113 seconds, or approximately **49%**, when using 10 instead of 20 epochs.

The modified experiment therefore required substantially less computation while preserving perfect JSON-format compliance.

**5. Remaining content failures**

The 20-epoch model made two content errors involving:

- Grade publication date
- Advance reservations for office hours

The 10-epoch model made four content errors involving:

- Whether non-PDF submissions were allowed
- Grade publication date
- Assignment word-count limits
- Reference-format requirements

Several incorrect responses used related but insufficient FAQ information instead of recognizing that confirmation was necessary.

Both models also made an unsupported assertion about the final assignment deadline in the additional knowledge-question test.

**6. Interpretation and limitations**

The results show a practical trade-off between training duration, content accuracy, and computational cost.

In this experiment, reducing training epochs approximately halved the training time without reducing format compliance, but content accuracy decreased.

These conclusions are based on one training run per configuration and a small evaluation set of 21 questions.

Even with a fixed random seed, GPU training is not always perfectly reproducible. Additional runs and a larger evaluation set would be necessary to determine whether the observed differences generalize consistently.

### Additional Experiment: 4-Bit Quantization

I also completed the optional Section 8 experiment to observe how quantization affects model memory usage and output behavior.

The base model was loaded with 4-bit quantization without fine-tuning.

| Metric | Original Untrained Model | Untrained 4-Bit Model |
|---|---:|---:|
| Reported model weight memory | 3.01 GB | 0.76 GB |
| Format compliance | 9.52% | 66.67% |
| Content accuracy | 0% | 33.33% |

**Observations:**

Quantization reduced the reported model weight memory by approximately 75%, demonstrating a substantial memory-saving benefit.

The 4-bit model also produced different outputs, resulting in different evaluation scores.

However, the observed accuracy differences should not be interpreted as proof that quantization generally improves model performance.

Quantization introduces numerical approximation, which can alter the model's predictions. These differences should be measured separately from changes caused by fine-tuning.

This experiment compared untrained models with different numerical precision; it was **not** a LoRA-versus-QLoRA training comparison.

### Discussion: When Fine-Tuning Is Suitable

Fine-tuning is useful when an application needs to learn consistent response behavior that prompting alone cannot reliably achieve.

Examples include:

- Producing responses in a specified JSON schema
- Maintaining consistent tone or formatting
- Following repeated task-specific procedures
- Adapting response behavior to a specialized workflow
- Reducing reliance on long instructions for frequently repeated tasks

LoRA is particularly useful because it freezes the original model weights and trains only a small set of additional parameters.

In my experiment, only approximately 0.84% of the model's parameters were trainable.

Despite this small number of trainable parameters, both configurations achieved 100% JSON-format compliance.

This demonstrated the effectiveness of parameter-efficient fine-tuning for learning relatively simple output behaviors.

### Discussion: When Fine-Tuning Is Not Suitable

Fine-tuning alone is not the best solution for questions requiring factual information that is missing from the training data or changes frequently.

For example, a course chatbot should not guess an assignment deadline when the provided FAQ does not contain the relevant information.

In such situations, retrieval-augmented generation (RAG) can be more appropriate because the model can retrieve and use relevant source material while generating an answer.

When evidence is unavailable, the system should explicitly request confirmation rather than making unsupported assertions.

Fine-tuning also introduces additional costs, including:

- Preparing and validating training examples
- GPU training and experimentation
- Maintaining separate evaluation data
- Checking for regressions and overfitting
- Retraining when requirements change

For simpler formatting requirements, prompt engineering or structured-output features should generally be attempted before deciding to fine-tune the model.

### Final Reflection

This homework helped me understand the difference between teaching a model how to respond and teaching it when an answer is supported by evidence.

The most interesting result was that reducing the training duration from 20 to 10 epochs did not affect JSON-format compliance, which remained at 100%, but reduced content accuracy from 90.48% to 80.95%.

At the same time, training time decreased from 229 seconds to 116 seconds.

This demonstrated that increasing training duration can improve performance on some metrics while increasing computational cost.

The remaining mistakes on ungrounded questions showed that a model may produce a perfectly formatted response while still providing an incorrect or unsupported answer.

**My main takeaway is that fine-tuning should be evaluated using multiple independent metrics, including format compliance, factual accuracy, uncertainty handling, and computational cost.**

Fine-tuning is a useful tool for improving model behavior, but it should be combined with appropriate grounding, evaluation, and safeguards when factual reliability matters.

### Implementation — Custom FAQ

For this part, I created a fictional virtual-networking lab FAQ with five facts about the VPC, subnet, gateway, DNS resolver, and SSH access.

I replaced the original FAQ and questions in the notebook while keeping the same JSON output format with `answer` and `needs_review`.

For the ungrounded questions, I chose things related to the lab that were not mentioned in the FAQ, such as firewall rules, password rotation, and account approval. I checked that these questions could not be answered using the five facts.

I used Qwen3.5-0.8B with LoRA rank 16, learning rate `2e-4`, and 20 epochs. The dataset contained 14 training examples, 7 validation examples, and 21 test questions.

| Metric | Before | After |
|---|---:|---:|
| Format compliance | 100% | 100% |
| Content accuracy (notebook rubric) | 71.43% (15/21) | 100% (21/21) |
| Both correct | 15/21 | 21/21 |

Training took around 208 seconds, and the final logged loss was 0.013249. There were no regressions.

One thing I noticed was that the model already followed the JSON format correctly before training. Five of the six failed content checks happened because the evaluation expected the exact word `confirm`, even when the model had correctly set `needs_review` to `true`. If I only checked the `needs_review` decision, the score was 20/21 before training and 21/21 after training.

I also tried separate questions about information missing from the FAQ. Before training, the model made unsupported claims about IPv6 support and network ownership. After training, it asked for confirmation instead.

So, fine-tuning helped the model give more consistent answers in this experiment. However, the test set was small, and the scoring was quite strict about wording. I would not assume the model will always behave correctly on other questions.

The notebook and evaluation files are saved in the repository.

### Advanced — Fine-tuning on the Course Glossary

For Advanced, I used the provided `make_sft_dataset.py` script to generate training data from the course glossary. It produced 130 question-answer examples covering 65 terms.

I trained a fresh Qwen3.5-0.8B model using LoRA for three epochs, with rank 16 and learning rate `2e-4`. I used fewer epochs than the earlier FAQ experiment because this dataset was much larger.

I prepared 15 evaluation questions: five asking for glossary definitions, five asking for beginner-friendly explanations, and five about terms not included in the glossary.

The evaluation questions used different wording from the training prompts. However, the known terms themselves appeared during training, so this was mainly a test of rephrased questions, not completely unseen concepts.

Training finished in 111.6 seconds with 51 steps and a reported training loss of approximately 1.6601.

| Metric | Before | After |
|---|---:|---:|
| Known-term questions answered | 10/10 | 10/10 |
| Unknown terms correctly flagged | 0/5 | 0/5 |

These results were not as good as I had hoped. The model answered every known-term question before and after training, but answering a question does not mean the answer is correct.

When I read the actual outputs, I found that some explanations were reasonable, while others included mistakes or unsupported details.

For example, the fine-tuned model incorrectly connected LoRA configuration with Pydantic AI. It also invented a course-specific context-window limit of 4096 tokens.

The unknown-term questions were another problem. I tested KV cache, speculative decoding, FlashAttention, DPO, and MoE. These terms were not in the course glossary, but the model still answered all five instead of saying they were not covered.

One possible reason is that the training dataset only contained examples of answering known glossary questions. It did not include examples showing what to do when a term was missing. The evaluation prompt did include the known glossary term names and an instruction to refuse unknown terms, but the model did not follow that instruction reliably.

This showed me that fine-tuning on definitions does not automatically teach a model when it should say it does not know something.

#### Fine-tuning vs. Searching the Glossary

I also considered whether searching the glossary would work better than training the model on its definitions.

Fine-tuning lets the model learn terminology and response patterns without receiving every definition in the prompt. However, it takes training time, and the model can still remember details incorrectly.

A glossary-search system could retrieve the original definition whenever a question is asked. That would make it easier to check the source and update information without retraining the model.

Search is not perfect either. It might retrieve the wrong entry or fail to match a question that uses different wording.

For a learning assistant based on a course glossary, I would prefer searching the glossary for factual answers and using fine-tuning mainly to improve the response style.

I did not run a separate retrieval experiment for this part, so this comparison is based on how the two approaches work rather than measured retrieval results.

#### What I Learned

The Implementation experiment worked quite well on a small FAQ, but the Advanced experiment showed that having more training examples does not automatically make the answers more reliable.

The biggest takeaway for me was that training loss alone is not enough to judge a model. I also need to read its answers, especially when it is asked about something outside the training data.

I used AI assistance while preparing parts of the code and write-up. I ran the experiments in Colab and checked the reported numbers against the saved results.
