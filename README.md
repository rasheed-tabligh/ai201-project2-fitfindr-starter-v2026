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

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:**

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** <!-- which fields, in what order -->

---

## Sample Run

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
<<< Here are two thrift-fashion styling options built around your new Y2K baby tee, using only the pieces currently in your wardrobe:

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
* **Accessories:** Brown leather belt (to define the waist against the trousers) and Black crossbody bag >>>
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

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
