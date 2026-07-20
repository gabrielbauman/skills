---
name: secure-coding
description: "Write code that holds at the trust boundary: treat every external input as attacker-controlled until validated server-side, build SQL, shell commands, HTML, and paths by parameterization instead of string concatenation, check authorization at every resource access, keep secrets out of code, logs, URLs, and error messages, use vetted crypto, and fail closed. Use whenever handling user input or file uploads, building queries or shell commands, adding an endpoint or permission check, storing passwords or tokens, or reaching for eval, shell=True, or dangerouslySetInnerHTML. Pairs with dependencies, the supply-chain half of the attack surface."
---

# Secure coding

Insecure code is rarely written on purpose. It is written by assuming:
that the value in the request is the shape the frontend sends, that
the id in the URL belongs to the user who sent it, that nobody will
put a quote mark in their name. Each assumption is true for every user
the developer imagined and false for the one probing the system, and
the attacker only needs the assumption you did not check.

The corrective is a small set of habits applied at the boundary where
outside data enters and where your system touches resources. None of
them require a security specialist; all of them require refusing the
convenient assumption.

## All input is attacker-controlled

Everything that crosses into your process from outside is chosen by
someone else: URL parameters, form fields, JSON bodies, headers,
cookies, file names and contents of uploads, webhook payloads, query
strings, and data read back from systems that others write to.
Validate it server-side at the boundary: type, range, length, format,
allowed values. Client-side validation is a UX courtesy; the attacker
does not use your frontend, they use curl.

Validate by allowlist (what is permitted) rather than blocklist (what
is known to be bad). A blocklist encodes the attacks you have thought
of; the allowlist survives the ones you have not.

## Never build code out of data

Injection, in every variant, is one mistake: concatenating untrusted
data into a string that something will execute. The fix is also one
idea: keep data in the data channel, using the mechanism each
executor provides for exactly this.

- **SQL**: parameterized queries or the ORM's bound parameters, never
  f-strings or `+`. `f"WHERE name = '{name}'"` is an open door no
  quoting function reliably closes.
- **Shell**: argument lists (`subprocess.run(["git", "log", ref])`),
  never `shell=True` with interpolated input. If you must go through
  a shell, the input goes through the platform's quoting function and
  you write down why.
- **HTML**: the template engine's auto-escaping, left on. Every
  bypass (`dangerouslySetInnerHTML`, `innerHTML`, `| safe`, `v-html`)
  is a claim that this exact string is trusted; be able to say who
  made it trusted.
- **Paths**: resolve user-supplied file names against a base
  directory and verify the resolved path is still inside it, or
  `uploads/../../etc/passwd` walks wherever it likes.
- **`eval` and friends** on external input: no. There is no quoting
  discipline that makes executing attacker text safe.

## Authorization at the resource, every path

Authentication says who this is; authorization says what they may
touch, and it must be checked where the touching happens. The classic
hole (insecure direct object reference) is a handler that fetches by
id and checks nothing:

```python
# Anyone logged in can read any invoice by guessing ids.
def get_invoice(request, invoice_id):
    return Invoice.objects.get(id=invoice_id)

# The fetch itself enforces ownership; there is no path around it.
def get_invoice(request, invoice_id):
    return Invoice.objects.get(id=invoice_id, owner=request.user)
```

Hiding the button is not authorization; the attacker calls the
endpoint directly. Check on reads and writes both, on every route to
the resource (API, admin, export, webhook), and put the check in the
data-access layer where a forgotten handler cannot skip it.

## Secrets stay out of everywhere

A secret that touches code, logs, URLs, or error messages should be
assumed leaked, because each of those surfaces is copied somewhere
you do not control: git history survives the deleting commit, logs
are shipped to aggregators, URLs land in access logs, proxies, and
browser history.

- Secrets come from the environment or a secret manager, never
  literals in source. `.env` files stay untracked.
- Never in log lines (logging covers this) or in exception text that
  can reach a user (error-handling covers that).
- Tokens travel in headers or request bodies, not query strings.
- A secret that does leak gets rotated, not deleted from history;
  the history has already been cloned.

## Do not roll your own crypto or auth

Password hashing, token generation, session management, and
encryption are solved by vetted libraries and unsolvable by fresh
implementations, because the failures are invisible: the homemade
scheme works perfectly in every test and falls to an attack you have
not heard of. Concretely:

- Passwords: bcrypt, scrypt, or argon2 via a maintained library.
  Never md5, sha256, or anything you composed yourself, salted or
  otherwise.
- Random tokens: the cryptographic RNG (`secrets`, `crypto`), never
  `random`.
- Comparing secrets (tokens, signatures, MACs): the constant-time
  compare (`hmac.compare_digest`), because `==` leaks how much of the
  guess was right through timing.
- Session and auth flows: the framework's, configured, not
  reimplemented.

## Fail closed

When an authorization check errors (service down, record missing,
exception thrown), the request is denied. A `try/except` that
proceeds on failure converts every outage into an open door, and
these paths are exactly the ones no test exercises. The same
fail-closed shape applies to validation: unrecognized input is
rejected, not passed through.

Least privilege is the same idea at rest: the DB user the app runs
as, the scopes on its tokens, the permissions on its service account,
each sized to the need, so the day something is compromised the blast
is sized to the need too.

## Dangerous APIs are review flags

`eval`, `exec`, `pickle.loads` on external data, `yaml.load` without
`SafeLoader`, `shell=True`, `dangerouslySetInnerHTML`, `innerHTML`,
`| safe`, disabled CSRF, `verify=False`: each is a deliberate hole in
a protection someone built. Sometimes the hole is justified; it is
never justified silently. Each use gets a comment saying why it is
safe here (per why-comments, this is a constraint worth writing
down), and absent that justification, reviewers should treat it as a
finding.

## Bad, then good

```python
# Every assumption the attacker needs, in four lines: query built
# from input, no ownership check, secret in the log line.
def download(request):
    name = request.GET["file"]
    log.info(f"download {name} token={request.headers['X-Api-Token']}")
    row = db.execute(f"SELECT path FROM files WHERE name = '{name}'")
    return send_file(row.path)
```

```python
def download(request):
    name = request.GET["file"]
    log.info("download requested", file=name, user=request.user.id)
    row = db.execute(
        "SELECT path FROM files WHERE name = %s AND owner_id = %s",
        [name, request.user.id],
    )
    if row is None:
        raise Http404
    path = (UPLOAD_ROOT / row.path).resolve()
    if not path.is_relative_to(UPLOAD_ROOT):
        raise Http404
    return send_file(path)
```

Same feature, same length within a few lines. The difference is only
which assumptions got checked: the query is parameterized, the fetch
enforces ownership, the resolved path is confined to its directory,
the token stays out of the logs, and the missing row fails closed.
