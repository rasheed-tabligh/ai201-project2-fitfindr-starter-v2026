"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # Criterion 1 — the full three-tool run.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # Criterion 2 — the branch. Costs no model calls; the gate stops it.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3 — state. Any normal query works; what matters is whether
        # the id in session["selected_item"] matches the item suggest_outfit got.
        "name": "state: selected item reaches suggest_outfit",
        "query": "oversized flannel shirt",
        "wardrobe": "example",
        "criterion": 3,
    },
    # Criterion 4 — five DIFFERENT listings, because the criterion is about
    # five listings rather than five tries of one. Scenarios 1 and 3 above give
    # two of them (Y2K Baby Tee, Oversized Flannel); these give the other three.
    {
        "name": "fit card: track jacket",
        "query": "90s track jacket",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card: corduroy pants",
        "query": "corduroy wide leg pants under $40",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card: knit cardigan",
        "query": "chunky knit cardigan",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5 — every returned listing should be category 'tops'.
        "name": "category: graphic tee returns tops only",
        "query": "graphic tee",
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
