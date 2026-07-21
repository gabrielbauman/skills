---
name: simplified-technical-english
description: "Write procedures, runbooks, and instructional text in Simplified Technical English, a controlled language adapted from the ASD-STE100 aerospace standard for software: short, unambiguous sentences a stressed or non-native reader can follow without misreading. Use when writing or editing runbooks, operational or troubleshooting procedures, migration or installation steps, README instructions, warnings and cautions, or when asked to simplify, standardize, or tighten technical writing. Pairs with writing-docs (that skill decides what a document contains; this one governs the sentences)."
---

# Simplified Technical English

Technical instructions get read at the worst possible moment: mid-incident,
at 3am, by a reader whose first language is not English, or by an agent that
executes them literally. Prose that would be fine in an essay fails here in
specific ways: the action hides inside a noun stack ("perform connection
resistance calibration"), the condition arrives after the command it
qualifies so the reader acts before reading it, passive voice conceals who
or what acts, and synonym variation makes one component look like three.

Simplified Technical English fixes these with a small set of sentence-level
rules, adapted here from ASD-STE100, the controlled language the aerospace
industry developed because misread maintenance manuals caused accidents.
Apply the rules to procedures, runbooks, warnings, and the descriptive text
around them.

One rule outranks the others: simplify the sentence, never the meaning.

## Protect the meaning first

Before touching style, fix what the text must not lose:

- Preserve identifiers exactly: commands, paths, flags, API names, code
  symbols, UI labels, log messages, units, limits, and quoted text. A
  "simplified" runbook with a mistyped flag is worse than the original.
- Preserve the sequence of operations. Reordering steps for readability
  changes the procedure.
- Preserve normative force. "Must", "should", "may", and "can" state four
  different contracts (requirement, recommendation, permission,
  possibility). Do not promote or demote one while rewording.
- When a fact is missing (a precondition, a hazard, an expected result),
  say so or ask. Do not invent it to complete the sentence.

## One term for one thing

Readers treat different words as different things. If a document says "the
scheduler", "the cron service", and "the job runner" for the same component,
the reader must guess whether that is one system or three, and guessing is
exactly what procedures exist to prevent.

- Pick one noun per component, state, and result, and repeat it. Repetition
  that prevents ambiguity is correct; varying terms for style is not.
- Write an official long term in full at first use, then use its defined
  short form: "the Certificate Signing Request (CSR)... submit the CSR".
- Prefer the common word over the impressive one: "use" not "utilize",
  "start" not "initiate", "enough" not "sufficient".
- Keep multi-word nouns to three words. Longer stacks force the reader to
  parse grammar instead of following instructions.

**Before:** Perform runway light connection resistance calibration.
**After:** Calibrate the resistance of the runway light connection.

## Sentences

- Give each sentence one topic and one primary action, with the subject,
  verb, and object explicit. A sentence that does two things lets the
  reader complete one and skip the other.
- Use articles ("the", "a") where grammar wants them. Telegraphic style
  ("restart pod, check log") reads fast and misleads faster.
- Use "this" or a pronoun only when its referent is unmistakable. In
  "restart the proxy and the agent, then check that it is healthy", the
  reader cannot know what "it" is.
- Write contractions in full: "do not", "cannot", "it is". "Do not" survives
  a bad photocopy, a truncated terminal, and a skimming reader; "don't"
  loses its negation more easily than any other word in the sentence.
- Where you want a semicolon, start a new sentence instead.

## Verbs and voice

Active voice with a named agent tells the reader who acts, which in a
procedure is the difference between "the system does this" and "you must do
this".

- Use active voice when the agent is known. Use passive only in descriptive
  text where the agent is unknown or genuinely irrelevant.
- Prefer simple forms: simple present, simple past, imperative. Replace
  perfect and progressive constructions when a simple form keeps the
  meaning ("the scheduler starts the service", not "the service is being
  started by the scheduler").
- Use a direct verb for the action instead of a noun phrase plus a filler
  verb: "back up the database", not "perform a backup of the database".
- Do not verb a noun unless the domain already does ("deploy" yes;
  "grease the fasteners" no, write "apply grease to the fasteners").

**Before:** The configuration is validated by the operator before deployment
is performed.
**After:** Validate the configuration. Then deploy.

## Conditions before commands

Put the condition first, then a comma, then the command. A reader executing
step by step performs the action they read first; if the condition trails
the command, they may act before learning it did not apply.

**Before:** Restart the service when the health check fails.
**After:** When the health check fails, restart the service.

The same goes for prerequisites: "Before you run the migration, back up the
database", never the reverse order.

## Procedures

- Write each instruction in the imperative: "Stop the service", not "The
  service should be stopped" (by whom?) or "You will want to stop the
  service".
- One instruction per sentence, one sentence per step. Combine actions only
  when they genuinely happen at the same time.
- Keep each procedural sentence to 20 words or fewer. Past that length a
  step is usually hiding a second instruction or a condition.
- Number the steps when order matters; use bullets only when it does not.
- Put the expected result or acceptance check right after the action it
  verifies, as its own sentence: "Restart the service. The status endpoint
  returns 200 within 30 seconds."

**Before:** Stop the service, save the configuration file, and restart the
service, making sure it comes back healthy.
**After:**
1. Stop the service.
2. Save the configuration file.
3. Restart the service. The health check passes within one minute.

## Descriptions and summaries

Descriptive text (overviews, explanations, incident summaries) follows the
same discipline with more room:

- Lead with the primary result or fact, then add supporting detail. The
  first sentence answers the question the reader arrived with.
- Keep descriptive sentences to 25 words or fewer, one topic per paragraph,
  and at most six sentences per paragraph.
- Use plain connectors ("and", "but", "then", "as a result") to make the
  relationship between sentences explicit instead of implied.
- State uncertainty directly. Separate what is verified from what is
  assumed or unfinished; "the fix is deployed and the test passes" and "the
  fix should work" are different claims.

**Before:** Fixed: timeout -> retry path -> green.
**After:** The request timeout is fixed. The client now retries once after a
transient gateway error, and the integration test passes.

## Lists

- Put a colon before a vertical list, keep every item at the same logical
  level, and start each item with an uppercase letter.
- End full-sentence items with a period; never end an item with a comma or
  semicolon as if the list were one long sentence.
- Do not mix instructions and descriptions in the same list. A reader
  scanning a checklist executes every line; a buried statement of fact
  either gets "executed" or teaches them to skip lines.

## Notes, warnings, and cautions

These three labels carry different obligations, and mixing them teaches
readers to ignore all of them:

- A note holds supporting information only. If a note contains an
  instruction, requirement, limit, or safety precaution, the reader who
  skips it (notes are skippable by definition) misses something mandatory.
  Promote it into the procedure.
- WARNING marks a risk of injury or death. CAUTION marks a risk of damage
  to equipment, software, or data. Do not use WARNING for data loss or
  CAUTION for electrical hazards; readers calibrate their attention to the
  label.
- Start a safety instruction with the command or condition, then state the
  hazard and its result. The action must come first because it is the part
  the reader needs before they act.

**Example:** CAUTION: Back up the database before you run the migration.
The migration can remove data that does not match the new schema.

## Final check

Before finishing, verify:

- The first sentence gives the outcome or primary fact.
- Technical meaning, normative force, sequence, and every identifier are
  unchanged.
- Each sentence has one topic; procedural sentences stay within 20 words,
  descriptive within 25.
- Conditions and prerequisites come before their commands.
- Active voice wherever the agent is known; imperatives for every
  instruction.
- Every pronoun and "this" has exactly one possible referent.
- One term per thing, used consistently throughout.
- Notes contain no requirements; warnings and cautions state both the
  action and the consequence.
