# AI writing tropes: full catalog

The complete reference behind the SKILL.md checklist. Each entry: what the
pattern is, why models produce it, and an example or two. Use this when
deep-cleaning heavily AI-flavored text or when you need to justify an edit.

Throughout: one instance of a trope may be deliberate and fine. Multiple
different tropes, or the same one repeated, marks the text as generated.

## Word choice

**Significance adverbs.** "quietly", "deeply", "remarkably", "fundamentally",
"arguably" pasted on to make an ordinary statement feel weighty. Test: delete
the adverb; if nothing changes, it was filler.
*"a quiet intelligence working behind the scenes"*

**Inflated vocabulary.** delve, tapestry, landscape, ecosystem, paradigm,
synergy, robust, seamless, harness, leverage (verb), streamline, utilize,
certainly. Each has a plain equivalent (dig into, mix, field, use...).
*"delving into the ever-evolving landscape of modern tooling"*

**The "serves as" dodge.** "serves as", "stands as", "marks", "represents"
where "is" would do. Models avoid repeating plain copulas, so they reach for
pomp.
*"The library serves as the project's central abstraction."* It is the
abstraction.

**Gravitas words.** crucial, essential, pivotal, vital, key, fundamental used
as intensity seasoning. Same deletion test as adverbs.
*"This is a crucial distinction."* If it matters, the sentence after it will
show why.

## Sentence structure

**Negative parallelism.** "It's not X, it's Y", "not because X, but because
Y", "The question isn't X. The question is Y." The single most recognized AI
tell: every point framed as a surprising reframe. One per piece, maximum, and
only when the contrast is real.
*"This isn't a bug tracker. It's a way of thinking."*

**Denial countdowns.** "Not A. Not B. Just C." Manufactured narrowing toward
a reveal.
*"Not a workaround. Not a patch. A redesign."*

**Self-posed questions.** Asking a question nobody asked and answering it in
the next clause for drama.
*"The catch? There isn't one."*

**Anaphora and stacked triples.** The same opener three-plus times running, or
rule-of-three lists back to back. One triple can be elegant; a chain of them
is a sampling artifact.
*"It could index your files. It could draft your replies. It could plan your
week."*

**False ranges.** "From X to Y" where no spectrum runs between X and Y; it's
just a fancy way to list two things.
*"from onboarding to cultural transformation"*

**Trailing participle analysis.** A "-ing" phrase tacked onto a fact to inject
unearned meaning: "highlighting...", "underscoring...", "reflecting broader
trends", "cementing its legacy".
*"The office moved downtown, underscoring the company's commitment to
community."*

**Empty transitions.** "It's worth noting that", "Importantly,",
"Interestingly,", "Notably,". They promise a connection they don't make.

## Paragraph and document structure

**Fragment percussion.** Very short sentences or fragments, one per line, as
manufactured emphasis. Nobody drafts this way; it's a readability-training
artifact.
*"He shipped it. Untested. On a Friday."*

**Listicle in prose clothing.** "The first problem is... The second problem
is... The third..." A numbered list wearing paragraphs, usually produced when
the model was told to stop making lists.

**Numbered phase labels.** "Phase 1:", "Stage 2:", "Step 3:" stamped on
narrative that isn't actually instructions. Prose flows by topic, not
countdown.

**Fractal summaries.** Previewing what you'll say, saying it, then
recapping what you said, recursively at every level of the document.

**Signposted conclusions.** "In conclusion", "To sum up", "In summary". A
reader can feel an ending; announcing it is template residue.

**One-point dilution.** A single thesis restated through ten metaphors to
feel comprehensive. If a section adds no new information, cut the section.

**The dead metaphor.** One metaphor introduced, then hammered through the
whole piece. Humans use a metaphor and move on.

**Content duplication.** The same sentence or paragraph appearing twice,
reworded or verbatim; a long-generation artifact. Always read the whole piece
once looking only for repeats.

## Tone

**False suspense.** "Here's the kicker", "Here's the thing", "Here's where it
gets interesting" before an unremarkable point.

**Teacher mode.** "Let's break this down", "Let's dive in", "Think of it as a
Swiss Army knife", "Imagine a world where...". Patronizing for experts,
and the analogies are usually murkier than the original concept.

**Stakes inflation.** Every topic becomes world-historical: "will
fundamentally reshape how we work", "defines the next era". A post about API
pricing is about API pricing.

**False vulnerability.** Polished, risk-free "honesty": "And yes, I'll admit
I'm biased here...". Real vulnerability is specific and a little
uncomfortable.

**Asserted obviousness.** "The truth is simple", "History is clear on this
point". If it were clear, you'd show it instead of saying so.

**False exclusivity.** "What nobody talks about", "the part everyone misses"
attached to widely known points. Valid only for genuinely obscure material.

**Invented concept labels.** Abstract problem-nouns welded to domain words and
treated as established terms: "the supervision paradox", "workload creep",
"the acceleration trap". Naming a thing is not arguing for it; several of
these in one piece is a strong slop signal.

**Unnamed authorities.** "Experts argue", "studies show", "observers note",
"industry reports suggest". No name, no source, no claim.

**Compliment sandwich.** Praise wrapped around every criticism. In technical
contexts especially, just say what's wrong.

**Clichéd idioms.** "smoking gun", "perfect storm", "game changer", "move the
needle", "double-edged sword", "tip of the iceberg", "at the end of the day".
Authority-flavored stock phrases nobody types by hand.

**Fake casual quotes.** Performing relatability by quoting an imagined
reaction: *"and your reviewer goes 'nope'"*. Casual writing is casual without
scare quotes.

**"Despite these challenges..."** The acknowledge-and-dismiss formula:
problems listed only to be waved off in an optimistic closer.

## Formatting

**Em-dash addiction.** A human uses a couple per piece; generated text uses
twenty. Replace with commas, parentheses, colons, or two sentences.

**Bold-first bullets.** Every bullet opening with a **Bolded label:** followed
by explanation. Signature AI markdown, especially with emoji.

**Unicode decoration.** Arrows (→), smart quotes, box-drawing flourishes.
Type what a keyboard produces: "->", straight quotes.

## Technical and professional prose

**Performative slang.** footgun, blast radius, monkeypatch, "ships day one",
"when X lands", "flip the knob", "smoke test" dropped in to sound senior.
Keep a term only when it's the precise word and the plain phrase would be
ambiguous; otherwise say "easy to misuse", "what this affects", "when X is
released", "a quick check".

**Fallback diagnoses.** "Race condition", "memory leak", "deadlock",
"debounce it" used as conclusions without an identified mechanism. Legitimate
only when you can name the two operations that interleave, the allocation
that's never freed, the event being coalesced. Otherwise describe the
observed behavior.

**Technical filler.** "under the hood", "deep dive", "in-depth", "at a
glance", "out of the box" as flavor. The sentence means the same without
them.
