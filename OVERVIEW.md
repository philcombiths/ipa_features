# ipa_features overview

Written from a code review on 2026-11-14 (commit `c2ba26f`). The examples below
were run against that commit.

## What it does

`ipa_features` parses a string of IPA characters into segments and looks up
phonetic features for each one. A segment is a base symbol (consonant or vowel)
plus any diacritics attached to it. Symbol roles and feature values come from a
reference table, `IPA_Symbol_Table.csv`, which is derived from the symbol set
used by Phon.

Its main consumer is `phon_query_to_csv`, whose `phone_data_expander.py` calls
`ipa_map.segment_generator()` to fill the T1-T3 and A1-A3 segment columns
(base, voice, place, manner, sonority, EML).

## Setup

The package is laid out with PyScaffold under `src/ipa_features/`.

    pip install pandas
    pip install -e .

`pandas` has to be installed by hand because it is not declared in `setup.cfg`.
The version number comes from git tags via `setuptools_scm`, so install from a
git checkout.

To run the tests:

    pip install pytest pytest-cov
    pytest

## Usage

From Python:

    from ipa_features import ipa_map

    # Segments, one PhoSegment per base symbol
    seg = next(ipa_map.segment_generator("pʰæt"))
    str(seg)                    # 'pʰ'
    seg.get_base()              # 'p'
    seg.get_feature("voice")    # 0.0
    seg.get_feature("place")    # 'bilabial'
    seg.get_feature("manner")   # 'stop'
    seg.get_feature("sonority") # 1.0
    seg.get_feature("EML")      # 'E'

    # Base symbols only, diacritics and boundaries stripped
    ipa_map.get_bases_string("pʰæt kːaʧ")   # 'pætkaʧ'

    # Raw parse: a list of segments, each a list of classified elements
    ipa_map.ipa_parser("pʰæt")

From the command line (prints the raw parse):

    python -m ipa_features "pʰæt"

## The reference table

`src/ipa_features/IPA_Symbol_Table.csv` has 281 rows, indexed by `Symbol`. It
is read once, at import, into `ipa_map.ipa_df`.

- Identity columns: `Description`, `Name`, `Symbol`, `Symbol-Display`,
  `Unicode`, `Type`.
- `Role` drives the parser. Values: `base` (158), `diacritic_right` (106),
  `diacritic_left` (9), `boundary` (3), `stress` (2), `compound_right` (2, the
  tie bars), `diacritic_role-switcher` (1).
- Consonant features: `Voice`, `Place`, `Manner`, `Sonority`, `EML` (early,
  middle or late acquired), plus `Flap`, `Lateral`, `Liquid`, `Glide`.
- Vowel features: `Back`, `Central`, `Front`, `Close`, `Mid`, `Open`, `Round`,
  `Rhotic`.

`IPA_Symbol_Table.xlsx` sits beside the CSV. Only the CSV is read by the code.
A separate repository, `IPA_symbol_table`, holds another copy of both files.

## How parsing works

`ipa_parser()` walks the string one character at a time and groups characters
into segments:

- Brackets and slashes are removed; runs of whitespace become one word
  boundary.
- A `base` symbol starts a segment. `diacritic_right` symbols attach to the
  base before them, `diacritic_left` symbols (such as prenasalization `ⁿ`)
  attach to the base after them.
- Boundary and stress symbols are stored as their own one-element groups.
- A character that is not in the table raises `ValueError`.

`segment_generator()` then wraps each group in a `PhoSegment` and silently
skips any group that has no base (boundaries, stress marks, stray diacritics).

## Classes

All in `ipa_map.py`.

- `PhoElement`: one character with its table row. `classify()` returns the
  matching subclass.
  - `PhoBase` -> `PhoConsonant`, `PhoVowel` (carry the feature dictionary)
  - `PhoDiacritic`, `PhoLigature`, `PhoBoundary`, `PhoStress`
- `PhoSegment`: a base plus its diacritics. Features are taken from the base
  only.

## Current limitations

These are worth knowing before relying on the output. Each is tracked in
`TODO.md`.

- Tie-bar affricates and diphthongs are split: `t͡ʃ` parses as two segments,
  `t͡` and `ʃ`. Single-character ligatures such as `ʧ` parse as one segment.
- A transcription containing the role-switcher character (`̵`) produces no
  segments at all.
- Diacritics do not change features. A devoiced `b̥` still reports
  `Voice = 1`.
- The null symbol `∅` and the cover symbol `*` are `base` rows, so each is
  returned as a segment with an empty feature set.
- Many consonant rows have blank features (see `TODO.md` for counts), and
  blanks come back as `NaN`.
- The 35 table rows whose `Symbol` is more than one character (for example
  `p̪`) are never matched as a unit, because parsing is character by
  character.

## Files

- `src/ipa_features/ipa_map.py`: the library. Everything above lives here.
- `src/ipa_features/__main__.py`: command-line wrapper around `ipa_parser`.
- `src/ipa_features/IPA_Symbol_Table.csv` / `.xlsx`: reference table.
- `src/ipa_features/reDiac.py`, `regex_find_generator.py`: older standalone
  regex helpers. Not used by the library and not importable as part of the
  package in their current form.
- `src/ipa_features/skeleton.py`, `tests/test_skeleton.py`: PyScaffold
  example code (Fibonacci).
- `tests/test_ipa_map.py`: tests for the parser and segment classes.
- `docs/`: Sphinx scaffolding that pulls in `README.rst`, which is still the
  PyScaffold placeholder.

## Test status

Run on 2026-11-14 with Python 3.13: 9 passed, 3 failed. The three failures are
tests written ahead of features that are not implemented yet (invalid sequence
detection, role switchers, compound phones).
