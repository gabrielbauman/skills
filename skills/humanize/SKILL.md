---
name: humanize
description: Write prose that reads like a person wrote it, and strip AI tells from existing text. Use whenever drafting or revising anything a human will read as prose (blog posts, docs, READMEs, emails, reports, announcements, marketing copy, PR descriptions) and whenever asked to humanize text, remove AI slop, make writing sound natural, or edit AI-generated drafts. Covers the common tells: em-dash addiction, "it's not X, it's Y" reframes, delve/robust/landscape vocabulary, bold-first bullets, manufactured drama, templated structure.
---

# Humanize

AI text feels off because it performs writing instead of doing it: manufactured
drama (false pivots, self-answered questions, inflated stakes), templated
structure (announced sections, bolded bullets, signposted conclusions), and
inflated vocabulary (delve, crucial, landscape). The fix is rarely a synonym
swap. Most flagged phrases carry no information, so the fix is deletion.

## Process

1. Draft for content. Say what you mean, in the order the reader needs it.
2. Make one revision pass against the checklist below. Prefer cutting to
   rephrasing.
3. Load [references/tropes.md](references/tropes.md) only if something reads
   as AI-flavored but matches nothing on the checklist, or if you need the
   full catalog's definitions and examples to justify an edit to the user.
   Slop density is not a reason to load it: the checklist covers the common
   tells however many of them the text has, and loading the catalog to
   confirm edits you've already identified just spends tokens.

A single instance of any pattern below can be fine. Several different ones, or
the same one twice, is the failure mode.

## Checklist

**Formatting**
- Em dashes: a couple per piece at most. Use commas, parentheses, or a period.
- Type what a keyboard types: straight quotes, "->" not unicode arrows.
- Bullets that each open with a **Bolded label:** are an AI signature.
- No emoji unless the user's own style uses them.

**Sentence moves**
- "It's not X, it's Y" and its cousins ("not because X but because Y",
  "The question isn't X. It's Y."). The most recognized tell of all.
- "Not A. Not B. Just C." countdowns.
- Self-posed questions ("The result? Devastating.").
- The same sentence-opener three times in a row; stacked rules-of-three.
- "From X to Y" where no real scale runs from X to Y.
- Trailing participle analysis ("...highlighting the region's rich heritage").

**Vocabulary**
- delve, tapestry, landscape, robust, seamless, leverage, harness, streamline,
  crucial, pivotal, fundamental, game-changer: use the plain word or delete.
- "serves as" / "stands as" / "represents" where "is" works.
- Significance adverbs: quietly, deeply, remarkably, fundamentally.

**Drama and tone**
- "Here's the kicker/thing", "Let's dive in", "It's worth noting",
  "In conclusion".
- Stakes inflation ("will reshape how we think about everything").
- False exclusivity ("what nobody talks about") unless it is genuinely obscure
  and you can back that up.
- "Think of it as..." analogies for readers who don't need them; "Imagine a
  world where...".
- Invented concept labels ("the supervision paradox") presented as established
  terms.
- Unnamed authorities ("experts argue", "studies show"). Name the source or
  drop the claim.

**Structure**
- Short. Punchy. Fragments. as manufactured emphasis.
- Listicles wearing prose ("The first wall is... The second wall is...") and
  numbered phase labels ("Phase 1:", "Step 2:") outside actual instructions.
- Telling the reader what you're about to say or just said, at any level.
- One metaphor per piece, used once, then dropped.
- Compliment sandwiches around criticism; "despite these challenges" pivots.

**Technical prose** (PRs, reports, commit messages)
- Slang worn to sound senior: footgun, blast radius, "when X lands",
  smoke test, "under the hood", "deep dive". Use the plain phrase.
- Diagnosis words (race condition, memory leak, deadlock) only when you can
  name the actual mechanism, never as a label for "something is wrong".

## What human writing does

The checklist only removes; these are what to put in its place.

- Vary sentence length the way speech does. A long sentence is fine when the
  thought is long, and a short one lands harder next to it.
- Be specific. Numbers, names, file paths, direct quotes. Specificity is the
  strongest human signal there is, and it's the one thing slop never has.
- Commit to claims. Cut hedges you don't mean ("arguably", "in many ways",
  "perhaps"). If you're genuinely unsure, say exactly what you're unsure
  about; that reads as honesty, not weakness.
- Trust the reader. No warm-up paragraph, no analogy for an expert audience,
  no announcing your structure. Start where the content starts.
- Let plain sentences be plain. A sentence that states a fact beats one
  straining for effect. Not every paragraph needs a turn.

## Rewriting someone else's text

Preserve the meaning and the author's voice; remove the residue, don't layer
your own flourishes on top. When a flagged sentence turns out to carry no
content ("This represents a pivotal shift in the landscape"), delete it
instead of rewording it. Expect the text to get shorter; that is the point.
