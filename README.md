# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr takes a plain-language request like "vintage graphic tee under $30"
and turns it into a styled outfit and a caption. It pulls a description, a size
and a price ceiling out of what you typed, searches 40 thrift listings for
keyword matches inside that budget and size, and picks the best one. It then
asks a model to build one or two outfits pairing that item with pieces already
in your wardrobe, and writes a short caption naming the item's price and the
platform it is listed on. If nothing in the listings matches, it stops before
spending a model call and tells you which part of your query to loosen.



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the 40 thrift listings by keywords, size and price,
  and returns the best keyword matches first.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None)
- **Returns:** A list of listing dicts, best match first, at most
  `config.SEARCH_RESULT_LIMIT` of them. Each dict has `id`, `title`,
  `description`, `category`, `style_tags` (list), `size`, `condition`,
  `price` (float), `colors` (list), `brand` (str or None), `platform`.
- **When it has nothing:** An empty list `[]`. Not None, not an exception.

### `suggest_outfit`

- **What it does:** Asks the model to suggest one or two outfits that pair a
  thrifted listing with pieces from the user's wardrobe.
- **Inputs:** `new_item` (dict, a listing), `wardrobe` (dict with an `items`
  key holding a list of wardrobe item dicts)
- **Returns:** A non-empty string naming one or two outfits, each referring to
  specific pieces from `wardrobe['items']` by name.
- **When it has nothing:** When `wardrobe['items']` is empty, returns a string
  with advice about the item itself (fit, how to style its colours) plus
  generic pairing ideas such as plain jeans or white sneakers. It never claims
  the user already owns a piece. It never returns "" and never raises.

### `create_fit_card`

- **What it does:** Asks the model to write a short caption someone would post
  about the find.
- **Inputs:** `outfit` (str, the output of `suggest_outfit`), `new_item`
  (dict, a listing)
- **Returns:** A two to four sentence caption that mentions the item, its price
  and its platform once each. The wording varies between runs by design.
- **When it has nothing:** When `outfit` is empty or whitespace only, returns
  the fixed string "No outfit suggestion was available, so there's no caption
  to write." No model call is made.

---

## Planning Loop

If `search_listings` returns an empty list, put a message in
`session["error"]` naming what the user could change, and return the session
without calling `suggest_outfit`. Otherwise take the first result, put it in
`session["selected_item"]`, and continue to `suggest_outfit` and then
`create_fit_card`.

— `agent.py::run_agent`

**How the query is parsed:** With regex, in `agent.py::parse_query`. `_PRICE_RE`,
`_SIZE_RE` and `_BARE_SIZE_RE` pull a price ceiling and a size out of the text,
and whatever is left becomes the description. No model call, so the same query
parses the same way every time.

**What moves through the session:** `query` to `parsed` to `search_results` to
`selected_item` to `outfit_suggestion` to `fit_card`, in that order. Each tool
reads its input back out of the session rather than taking it straight from the
previous call. When the run ends early, `error` is set instead and everything
after it stays `None`.

---

## Sample Run

### Full query through the loop

`python agent.py`, matching path:

```
[1] parse_query
      in:  looking for a vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, …
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      →    10 wardrobe item(s)
[5] create_fit_card

  found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
  fit card: Scored this butterfly baby tee for just $18.0 on depop and I am
            officially obsessed. I'm leaning into total 2000s off-duty energy
            today by pairing it with my baggiest dark-wash jeans and a beat-up
            denim jacket. Such a cute little throwback piece!
```

Impossible query, same command:

```
[7] search_listings (via MCP)
      out: [] (empty)
      →    0 match(es)
[8] branch
      →    search returned []: stopping before suggest_outfit

  stopped: Nothing in the listings matched description 'designer ballgown',
  size XXS, under $5.
  Things to change: try broader words — 'jacket' finds more than 'cropped
  corduroy jacket'; drop the size, or try a neighbouring one; raise the price
  ceiling above $5.
  fit_card is None — it should still be None here
```

### Per-tool tests

```
$ python -c "from tools import search_listings; print([l['title'] for l in search_listings('graphic tee', max_price=30)])"
['Y2K Baby Tee — Butterfly Print', 'Graphic Tee — 2003 Tour Bootleg Style', 'Mesh Long-Sleeve Top — Black', 'Vintage Band Tee — Faded Grey', 'Low-Rise Cargo Pants — Khaki', 'Vintage Graphic Hoodie — Faded Black']
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[1], get_example_wardrobe()))"
Here are two thrift-fashion styling options built around your new Y2K baby tee, using only the pieces currently in your wardrobe:

### Outfit 1: 2000s Streetwear Contrast
Pair the ultra-feminine, fitted energy of the butterfly tee with something structured and baggy for that classic Y2K off-duty look. 
* **Top:** The new Y2K Baby Tee — Butterfly Print
* **Bottoms:** Baggy straight-leg jeans, dark wash
* **Outerwear:** Vintage black denim jacket (worn open to show off the graphic)
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag

### Outfit 2: Grunge-Meets-Y2K Edge
Play up the vintage, nostalgic vibe of the tee by contrasting it with tougher, utilitarian pieces from your closet.
* **Top:** The new Y2K Baby Tee — Butterfly Print
* **Bottoms:** Wide-leg khaki trousers
* **Shoes:** Black combat boots
* **Accessories:** Brown leather belt (to define the waist against the trousers) and Black crossbody bag
```

```
$ python -c "from tools import create_fit_card; print(create_fit_card('', {}))"
No outfit suggestion was available, so there's no caption to write.
```

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
$ python -c "from tools import suggest_outfit; ..."

```

```
$ python -c "from tools import create_fit_card; ..."

```

---

## How I Used AI

**1. Deciding what `suggest_outfit` does with an empty wardrobe.** The docstring
in the starter said to "return general styling advice" and left the decision to
me. I asked Claude whether that was enough to write a spec from, and it pointed
out that nobody could check it, because there is no way to tell whether a given
answer counts as general styling advice. I replaced it with something specific:
when the wardrobe is empty the tool returns advice about the item itself, how it
should fit and how to style its colours, plus one or two generic pairing ideas
such as plain jeans or white sneakers, and it never claims the user already owns
a piece. That sentence went into my Tool Inventory and then into the prompt the
tool sends.

**2. Checking the search results instead of trusting them.** I ran
`search_listings('graphic tee', max_price=30)` and the six titles that came back
all looked like tops, so the search looked correct. I asked Claude to check the
`category` field on each one rather than reading the titles, and Low-Rise Cargo
Pants came back as `bottoms`. It had scored well because the words in its
listing overlapped with my query, and my search never looks at `category` at
all. I left it in place on purpose. Criterion 5 is the one that tests for this,
and unit 4 is where I am supposed to find out whether it holds, so fixing it now
would have removed the thing I wrote the criterion to catch.

**3. Reading my own file before pasting into it.** I had code from class for
wiring `search_listings` through MCP, and I pasted it into `run_agent`. It broke
the file: an unclosed parenthesis on a `trace.step` call, a duplicated import,
and three competing search calls where `session["search_results"]` was set from
one of them and `results` from another. I asked Claude to read `agent.py` and
tell me what was actually there, and the answer was that the starter already
shipped a `_search()` function with `call_tool("search_listings", ...)` inside
it and a direct-call fallback. The MCP wiring Milestone 1 asked for was already
written. I had been pasting a third copy of a call that existed twice. I reverted
`run_agent` to just `results = _search(parsed)` and the file compiled again.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

Produced by `run_eval.py::main`, seven scenarios from `scenarios.py`, five tries
each, caching off. Full output in `results/run_2026-10-07_2143_before.md`.
60 model calls.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item` id reaches `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card names the price and the platform | 5 listings | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. `graphic tee` returns only `tops` | 4 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |

Criterion 4 is measured across five different listings rather than five tries of
one, because the criterion is about five listings. Those five come from the
scenarios in `scenarios.py` tagged `"criterion": 4`, plus the listings selected
by criteria 1 and 3.

### Real output

**Criterion 1** — `run_eval.py::run_once`, five tries of "vintage graphic tee
under $30". Every try reached step 5 and produced a different card, so these are
five real answers and not one cached one:

```
try 1: completed — fit card 304 chars
try 2: completed — fit card 287 chars
try 3: completed — fit card 280 chars
try 4: completed — fit card 261 chars
try 5: completed — fit card 264 chars
```

**Criterion 2** — same file, "designer ballgown size XXS under $5". The loop
never reached step 4 on any try:

```
[2] search_listings (via MCP)
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit
  try 1: stopped early — Nothing in the listings matched description 'designer ballgo
```

**Criterion 3** — `trace.py::step`, called from `agent.py::run_agent`. I compared
all 30 `select_item` outputs against the `suggest_outfit` input that followed
them. Zero mismatches. One pair:

```
[3] select_item
      out: Oversized Flannel Shirt — Plaid Red/Black ($22.0, thredUp)
[4] suggest_outfit
      in:  Oversized Flannel Shirt — Plaid Red/Black ($22.0, thredUp)
```

**Criterion 4** — `tools.py::create_fit_card`, five different listings. One card
each:

```
Scored this little butterfly tee on depop for just $18.0 and I'm obsessed.
Scored this oversized red and black flannel on thredUp for just $22.0 and I'm obsessed.
Scored this vintage navy and white track jacket on Poshmark for $45.
Scored these rust corduroy wide-leg pants on depop for $32.0 and I am officially obsessed.
Scored this chunky brown knit on depop for just $35.0 and I am never taking it off.
```

**Criterion 5** — `tools.py::search_listings`, query "graphic tee". Six listings
returned, identical on all five tries:

```
tops       Y2K Baby Tee — Butterfly Print
tops       Graphic Tee — 2003 Tour Bootleg Style
tops       Mesh Long-Sleeve Top — Black
tops       Vintage Band Tee — Faded Grey
bottoms    Low-Rise Cargo Pants — Khaki      <-- not tops
tops       Vintage Graphic Hoodie — Faded Black
```

---

## Verdicts and Diagnoses

**1. MET (5/5).** Target was 4 of 5. All five tries ran parse, search, select,
outfit and fit card, and returned a card. The five cards differ in length from
261 to 304 characters, which is how I know caching was off and these were five
real model answers.

**2. MET (5/5).** Target was 5 of 5. Every try stopped at the branch in
`agent.py::run_agent` and the trace shows no step 4 on any of them. This is the
one path with no model in it, which is why I set 5 of 5 in unit 3.

**3. MET (5/5).** Target was 5 of 5. Thirty select-and-style pairs across the
whole run, zero mismatches. As with criterion 2, this path is plain Python, so
a mismatch would have been a bug rather than variation.

**4. MET (5/5).** Target was all five listings. Every card names the price and
the platform. One card wrote "$45" instead of "$45.0", which still states the
price, so I counted it as a pass.

**5. MISSED (0/5).** Target was 4 of 5. The query "graphic tee" returns
`Low-Rise Cargo Pants — Khaki`, which is `category: bottoms`.

**Diagnosis for criterion 5.** The step is the tool, `tools.py::search_listings`.
The mechanism is that it pools title, description, category, style_tags, colors
and brand into one bag of words and weights every word the same. My query
keywords are `{graphic, tee}`. The cargo pants description reads "Great for
layering with a long tee", so the word "tee" is in the listing as something the
item pairs *with* rather than something it *is*. That earns it a score of 1,
enough to clear my "drop anything scoring zero" rule, and nothing downstream
ever looks at `category`.

Worth saying plainly: this is one failure counted five times, not five separate
failures. Retrieval has no model in it, so the same query returns the same six
listings on every run. 0 of 5 is as bad as this criterion can score and it tells
me the same thing 1 of 5 would.

No pattern across misses, because there is only one miss. The four METs all came
out at target or above, which I would be more worried about if criterion 5 had
not failed.



---

## Loop Trace

One full run, `python app.py ask 'vintage graphic tee under $30' --trace`.
Produced by `trace.py::step`, called from `agent.py::run_agent`. Step 2 is the
MCP call, served by `mcp_server.py::search_listings`.

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are two thrift-fashion styling options built around your new Y2K baby tee, using only the pieces currentl…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Scored this butterfly baby tee for just $18.0 on depop and I am officially obsessed. I'm leaning into total 20…
```

### Failure modes triggered on purpose

**1. Empty search.** `python app.py ask 'designer ballgown size XXS under $5'`.
The loop stopped at step 3 and never called `suggest_outfit`:

```
[3] branch
      →    search returned []: stopping before suggest_outfit

  Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
```

The message names all three things the user controls and only mentions the size
and the price ceiling because this query actually set them.

**2. Empty wardrobe.** `python app.py ask 'oversized flannel shirt' --empty-wardrobe`.
`suggest_outfit` ran with 0 wardrobe items and returned advice rather than
crashing or returning an empty string:

```
[4] suggest_outfit
      →    0 wardrobe item(s)

  **Fit & Color Advice**
  Since this is an oversized flannel, let it lean into that relaxed, effortless
  shape. [...] let it be the statement piece of your outfit by keeping the rest
  of your colors neutral (think black, white, grey, or denim).

  **Thrift-Store Pairing Ideas**
  * **Bottoms:** A pair of classic straight-leg blue jeans or vintage black denim
  * **Footwear:** Crisp white sneakers or chunky black combat boots
```

This matches what my Tool Inventory promised: advice about the item plus generic
pairing ideas, never claiming the user already owns a piece.

**3. Model unavailable.** I changed one character of `GEMINI_API_KEY` in `.env`
and ran a query I had not run before, so the cache could not answer it:

```
[4] model unavailable
      →    stopping, search results kept

  The model couldn't be reached, so the outfit and caption steps didn't run.
  The search worked — 5 listing(s) were found. Check GEMINI_API_KEY in your .env,
  then run the same query again.
What the service said: The model rejected your API key. Check GEMINI_API_KEY in
your .env file, or create a fresh key at aistudio.google.com.
```

**A fourth failure mode I got for free.** While testing the above, Google
returned a 503. The same handler fired but with a different message:

```
What the service said: Couldn't reach the model: 503 UNAVAILABLE. {'error':
{'code': 503, 'message': 'This model is currently experiencing high demand.
Spikes in demand are usually temporary. Please try again later.'}}
```

Two causes, two different instructions. One tells the user to fix their key, the
other tells them to wait. All four stop cleanly, keep the search results, and
print a sentence rather than a stack trace, so none of them needed a new handler.





---

## The Improvement

**What I changed.** `tools.py::search_listings` now splits the listing's fields
into two groups before scoring. Strong fields are title, category and
style_tags. Weak fields are description, colors and brand. A listing qualifies
only if the query shares at least one keyword with its strong fields; a listing
whose only matches are in weak fields is dropped. The score is still the size of
the union of strong and weak matches, so weak fields keep helping the ranking,
they just cannot get a listing into the results on their own.

**Why I picked it.** My only miss was criterion 5, and the diagnosis named this
exact mechanism: the old scorer pooled every field into one bag of words, so
"Great for layering with a long tee" in the cargo pants description counted the
same as "tee" in a real tee's title. Splitting strong from weak is the smallest
change that addresses that sentence.

### Run Log — After

Produced by `run_eval.py::main`, same seven scenarios, five tries each, caching
off. Full output in `results/run_2026-10-07_2206_after.md`. 60 model calls.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item` id reaches `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card names the price and the platform | 5 listings | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. `graphic tee` returns only `tops` | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

### Did it help?

Yes. Criterion 5 went from 0 of 5 to 5 of 5. The other four criteria did not
move, which is what I wanted: the change was supposed to fix one thing without
disturbing anything else.

The query "graphic tee" before and after:

```
BEFORE — 6 results                      AFTER — 4 results
tops     Y2K Baby Tee                   tops  Y2K Baby Tee
tops     Graphic Tee — 2003 Tour        tops  Graphic Tee — 2003 Tour
tops     Mesh Long-Sleeve Top           tops  Vintage Band Tee
tops     Vintage Band Tee               tops  Vintage Graphic Hoodie
bottoms  Low-Rise Cargo Pants  <-- miss
tops     Vintage Graphic Hoodie
```

Criteria 1 to 4 were unaffected because every one of their scenarios still
selects the same top-1 listing as before. I checked all 30 select-and-style
pairs in the after run: zero mismatches, same as before.

**The trade-off, stated plainly.** This buys precision with recall. Result
counts dropped across the board: "graphic tee" 6 to 4, "oversized flannel shirt"
7 to 5, "90s track jacket" 10 to 9. `Mesh Long-Sleeve Top` is a legitimate top
that no longer appears for "graphic tee", because its only match was in its
description. I accepted that because my criterion is about what comes back being
correct, not about how much comes back.

---

## What's Still Broken

**1. The fix is narrower than it looks.** It removes description-only matches.
It does not fix wrong-category matches in general. The query "vintage graphic
tee under $30" still returns a 90s silk slip dress and a braided leather belt,
because both have "vintage" in their `style_tags`, which is a strong field. My
criterion 5 only names the bare "graphic tee" query, so it passes while the
underlying problem is only partly solved. What I would do: infer a category from
the query and filter on it, rather than relying on which field a word appeared
in. I stopped here because this unit allows one change and I had already spent
it, and because changing the criterion after seeing the result would not be
honest.

**2. Nothing in my criteria measures recall.** All five criteria ask whether
what comes back is correct. None asks whether anything useful was left out. That
is how a precision fix could pass every criterion while quietly making the
search worse, and I would not have noticed from the run log alone. I caught the
dropped result counts by comparing the two runs by hand. Next time I would write
one criterion about a minimum number of results for a query I know the data can
answer.

**3. The MCP fallback hides its own failures.** `agent.py::_search` wraps the
MCP call in `except Exception` and silently falls back to calling
`search_listings` directly. The trace still prints "search_listings (via MCP)"
either way, so if MCP broke mid-run my trace would say it ran when it did not. I
confirmed MCP really is being used by calling `mcp_client.call_tool` on its own
and getting results back, but the trace itself cannot tell the two paths apart.
The fix is to have `_search` report which path it took. I ran out of time.

---

## The MCP move

I moved `search_listings` onto MCP. `mcp_server.py` registers it with FastMCP,
typed as `description: str`, `size: str | None`, `max_price: float | None`, and
a description written for an agent that will never see my implementation.
`agent.py::_search` calls it through `mcp_client.call_tool` and falls back to a
direct call if the server cannot be reached. The other two tools are unchanged.

Nothing behaved differently after the move. The same query returned the same
listings in the same order, which is the result I wanted, because
`search_listings` is pure Python with no model in it.

One thing the move changed that is not code: writing the tool description forced
me to be accurate about behaviour I had never written down. My first draft said
results come back "cheaper first among equal matches". They do not. The sort is
stable with `reverse=True`, so listings with equal scores keep their original
catalog order. I only caught it because a published description is read by
someone who cannot check the source.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
