---
name: naming
description: "Name variables, functions, types, and files so the name states intent and role, not implementation or type. Use whenever writing new code, reviewing names, or renaming during a refactor. Covers vague fillers (data, temp, handle, obj), names that lie about what the thing does, Hungarian and encoded prefixes, abbreviations that cost the reader, scaling length to scope, dropping noise words (Manager, Helper, Util, Info), booleans that read as predicates, and staying consistent with the surrounding codebase. Pairs with why-comments: a good name deletes the comment that was there to explain a bad one."
---

# Naming

A name is the interface to a thing. Read ten times for every time it is
written, it is where most of a reader's understanding comes from, and it is
the one piece of documentation that can't be skipped. Agents reach for the
first name that compiles: `data`, `temp`, `result`, `handle`, `processData`.
Each is a placeholder that survived to production. The failure is not ugliness,
it is that a vague or misleading name forces the reader back into the body to
learn what the code already knew and refused to say. Spend the name; it is
cheaper than the comment, and far cheaper than the misread.

## Name the intent, not the mechanism

The name should say what the thing is for, so a reader never has to open the
body to find out. A name built from the implementation goes stale the moment
the implementation changes, and tells the reader nothing they couldn't get by
reading the code anyway.

```python
# bad: named after the data structure and the steps
arr = get_users()
d = {}
for x in arr:
    d[x.id] = x
```
```python
# good: named after the role each thing plays
users = get_users()
users_by_id = {u.id: u for u in users}
```

`users_by_id` survives switching the dict to an LRU cache; `d` told you nothing
to begin with. Same for functions: `parse_and_validate_and_store` describes the
body, `register_user` describes the purpose. When the steps change, the second
name still holds.

## Vague fillers say nothing

`data`, `info`, `temp`, `val`, `obj`, `item`, `thing`, `handle`, `stuff`,
`result`, `payload` are placeholders. Every value is data; the name has to say
*which* data. The fix is almost never to add a word (`userData`, `tempResult`)
but to replace the filler with the actual role.

```
data          -> raw_response, parsed_invoice, pixel_buffer
temp          -> previous_total, swap_slot, unsaved_draft
handle        -> open_socket, db_connection, file_reader
result        -> matching_rows, discounted_price, is_authorized
process(x)    -> resize_image(x), settle_payment(x), reindex(x)
```

## A name that lies is worse than a vague one

A vague name makes the reader look; a misleading name makes them trust the
wrong thing and stop looking. `getUser` that also writes a login timestamp,
`isValid` that throws instead of returning a bool, a `list` that is actually a
set, `count` that holds the sum. Whenever a name and the behavior disagree, fix
the name (or split the function so it does only what its name claims).

```js
// lies: "get" implies a pure read, but this mutates
function getConfig() {
  if (!cache) cache = loadFromDisk();  // side effect hidden behind "get"
  return cache;
}
// honest: the name admits the lazy load
function loadConfigOnce() { ... }
```

## Drop the noise words

`Manager`, `Helper`, `Util`, `Handler`, `Processor`, `Info`, `Data`, `Object`,
`Wrapper` attach to a name without narrowing it. `UserManager` could hold any
code that touches a user. Ask what it actually does and name that: authenticates
(`Authenticator`), stores (`UserRepository`), or maps to JSON
(`UserSerializer`). If the responsibility is too diffuse to name, that is a
design smell the name is exposing, not a naming problem to paper over.

```
UserManager      -> UserRepository, SessionStore, ProfileValidator
DataHelper       -> CsvParser, PriceFormatter
handleData()     -> ingestUpload(), applyDiscounts()
ThingProcessor   -> InvoiceRenderer
```

`Util`/`Helpers` catch-all modules grow into junk drawers because nothing that
lands there had to justify its home. Name the module for what it holds
(`geometry`, `retry`, `currency`) and the pull toward a dumping ground goes away.

## Don't restate the type

The type is already on the field or in the signature. `userList`, `nameString`,
`configMap`, `IUser`, `AbstractBaseFactory` repeat what the reader can already
see, and lie the day `userList` becomes a set. Name for role; let the type carry
the shape.

```
userList: User[]        -> users: User[]
nameStr: string         -> name: string
amountInt: number       -> amount: number   (or amountCents, if unit matters)
configMap: Map<...>     -> config: Map<...>
```

Encoding the type into the name (Hungarian notation: `strName`, `bReady`,
`arrItems`, `m_count`, `lpszFile`) is the same mistake with a worse history. It
predates editors that show types on hover and dies loudly on every refactor.
Skip it. The one exception: a unit or interpretation the type genuinely can't
express earns its way into the name, `timeoutMs`, `priceCents`, `angleRadians`,
because there the suffix carries meaning, not redundancy.

## Booleans read as predicates

A boolean should read as a yes/no question, so a condition reads like a
sentence. Prefix with `is`, `has`, `can`, `should`, `did`. A bare noun leaves
the reader guessing which value is true.

```
status        -> is_active
admin         -> is_admin
retry         -> should_retry
children      -> has_children
if flag:      -> if is_expired:
```

Avoid negatives in the name; `is_disabled` forces a double negative at every
`if not is_disabled`. Prefer `is_enabled` and let the caller negate.

## Length scales with scope

How descriptive a name needs to be depends on how far it travels. A loop index
alive for three lines can be `i`; a value that crosses module boundaries and
lives in the reader's head for a whole function needs to carry its meaning
unaided. Long names in a tight scope are noise; short names in a wide scope are
riddles.

```python
# fine: tiny scope, the reader sees the whole life of the name at once
for i in range(len(rows)):
    total += rows[i].amount

# needs the full name: this crosses functions and outlives the reader's glance
def settle(pending_reimbursements): ...
```

Single letters are fine for conventional short-lived roles (`i`/`j` indices,
`k`/`v` in a dict comprehension, `e` for a caught exception, `x` in a one-line
lambda). Everywhere else, the keystrokes an abbreviation saves the writer are
paid back with interest by every reader who has to decode it. `cnt`, `usr`,
`calc`, `mgr`, `svc`, `idx`, `tmpl`, `req`/`res` (as domain terms, not
request/response) cost more than they save. Write the word.

## Match the codebase

Naming conventions are house style. If the codebase says `fetchUser`, a new
`get_user_data` reads as foreign even where it is individually defensible.
Match what surrounds your change: the casing (`camelCase` vs `snake_case`), the
verb vocabulary (is it `fetch`, `get`, `load`, or `retrieve` here?), the
collection idioms (`users` vs `userList`), the file naming (`user_repository.py`
vs `UserRepository.ts`). One consistent convention beats a locally better name
that breaks the pattern. When you genuinely think the house convention is wrong,
raise it, don't fork it one file at a time.

## A good name deletes a comment

When you feel the urge to add a comment explaining what a name means, that is
the name asking to be better. `d` with a comment `# users keyed by id` should
just be `users_by_id`. `t` with `# timeout in seconds` should be
`timeout_seconds`. The comment goes stale independently of the code; the name
can't. See [[why-comments]]: the comments worth keeping explain *why*, and a
name that has to be explained by a *what* comment is a name not yet finished.

```python
n = get()          # number of active sessions   -> active_session_count = get()
flag = True        # whether the cache is warm    -> cache_is_warm = True
```

## Renaming existing code

- Rename freely within code you are already changing; a scoped rename that makes
  the diff clearer is part of the work.
- A repo-wide rename of an established name is its own change, not a rider on a
  feature. It touches every call site and buries the real diff. Do it alone.
- Keep a name consistent with its callers. Renaming a function without updating
  the vocabulary its neighbors use trades one inconsistency for another.
- Don't "fix" a name whose meaning you're unsure of. An odd name (`fudge_factor`,
  `magic_offset`) may encode a hard-won reason. Ask before overwriting it.
