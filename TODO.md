# TODO

From a structural code review on 2026-11-14 (commit `c2ba26f`). Unlike a
read-only review, the behaviors below were confirmed by running the code and
the test suite (Python 3.13, 9 tests passed, 3 failed), except where an item
says "not run". See `OVERVIEW.md` for how the package works.

Items are ordered by priority within each section. Line numbers refer to
`src/ipa_features/ipa_map.py` unless another file is named.

## 1. Behaviors that affect downstream data

These matter most because `phon_query_to_csv` builds its segment and feature
columns from this package.

- [ ] Tie-bar compounds are split into two segments. `ipa_parser("t͡ʃ")`
      returns `[t, ͡]` and `[ʃ]`, so an affricate or diphthong written with a
      tie bar is counted as two segments, with the tie bar left hanging on the
      first. The cause is that `compound_right` is not handled in the parser
      loop (lines 531-546): the tie bar is appended like a diacritic and the
      next base then ends the segment. `PhoSegment` already has partial
      multi-base support (`get_base`, line 433), but the parser never produces
      a multi-base segment, and constructing one by hand raises `ValueError`
      at line 437.
- [ ] That `ValueError` is swallowed. `segment_generator`, `get_segment`,
      `get_bases` and `get_bases_string` all catch `ValueError` to skip
      boundaries (lines 584, 600, 630, 662). Once compounds are parsed
      correctly, the "compound base not implemented" error would be caught by
      the same handler and the segment silently dropped. Use a specific
      exception class for "no base" so real errors surface.
- [ ] Role-switcher transcriptions yield nothing. Any input containing `̵`
      makes `ipa_parser` return `[""]` (line 474), which every caller treats
      as zero segments, with no warning. The return type is also wrong (a list
      holding a string rather than a list of lists). At minimum log a warning
      naming the transcription; ideally implement the role switcher.
- [ ] `∅` and `*` are returned as segments. Both are `Role = base`,
      `Type = Null` in the table, so `segment_generator("∅")` yields a segment
      with an empty feature dictionary and a "base role but unknown type"
      warning on every occurrence (line 224). In `phon_query_to_csv` this
      makes a deleted target count as one segment. Decide whether null and
      cover symbols should be segments, and give them their own role or class
      either way.
- [ ] Diacritics never modify features. `PhoSegment.features` is copied from
      the base only (line 367), so devoicing, nasalization, length and similar
      marks have no effect on `Voice` or any other feature. The combining
      logic is stubbed at lines 369-372 and `PhoDiacritic.features` is empty
      (line 312).
- [ ] Blank feature cells. Of the 126 consonant, implosive and click base
      rows, the table is missing `Voice` for 20, `Place` and `Manner` for 36,
      `Sonority` for 48 and `EML` for 101. Blanks are returned as `NaN`. Fill
      in what should be filled, and document which blanks are intentional
      (`EML` presumably only applies to the English and Spanish inventories).
- [ ] Numeric features come back as floats. Because of the blanks, `Voice`
      and `Sonority` are float columns, so `get_feature("voice")` returns
      `0.0` or `1.0` and they are written to CSV that way. Read those columns
      with a nullable integer dtype in `ipa_reference` (line 49).
- [ ] Stray left diacritics are dropped silently. `ipa_parser("pⁿ")` returns
      `[p]` and `[ⁿ]`, and the second group is discarded because it has no
      base. A right diacritic before any base (`ʰp`) is accepted and attached
      to the following base as if it were a left diacritic. Either raise or
      log for both cases (see the failing test in section 3).
- [ ] 35 table rows have a multi-character `Symbol` (for example `p̪`, `t̪͆`,
      `ʰ̵`). The parser reads one character at a time and `PhoElement` asserts
      a single character (line 122), so these rows can never be matched.
      Either match the longest symbol first or remove the rows.
- [ ] `get_bases_string` drops word boundaries: `"pʰæt kːaʧ"` becomes
      `"pætkaʧ"`. Confirm that is intended and say so in the docstring.

## 2. Bugs and rough edges

- [ ] Empty groups in parser output. `ipa_parser("a. b")` returns
      `[a], [.], [], [ ], [b]` and `ipa_parser("")` returns `[[]]`. The parser
      appends `seg_memory` at whitespace and at end of input without checking
      that it is non-empty (lines 494, 560). Harmless to `segment_generator`,
      but wrong for anyone using `ipa_parser` directly.
- [ ] `PhoElement` defines `__eq__` without `__hash__` (line 158), so
      instances cannot be used in sets or as dictionary keys
      (`TypeError: unhashable type`). `PhoSegment` does define `__hash__`.
- [ ] `PhoElement.__eq__` ignores the class, so `PhoElement("p") ==
      PhoConsonant("p")` is true. The tests depend on this. Keep it or change
      it, but document it.
- [ ] `PhoConsonant` and `PhoVowel` call `self.series.get(...)` without
      checking for `None` (lines 276, 291), so constructing one directly with
      a symbol missing from the table raises `AttributeError` instead of a
      clear message.
- [ ] `PhoElement("")` fails on the single-character `assert` (line 122) with
      a confusing message. Replace the assert with a `ValueError`; asserts are
      also stripped under `python -O`.
- [ ] `get_bases` returns `[""]` for non-string input and for role-switcher
      input (lines 653, 658) while its docstring says an empty list.
      `get_bases_string` returns `""`. Make the two consistent.
- [ ] `PhoElement.__getitem__` (line 179) is annotated `-> str` but returns a
      `PhoElement`, and is marked "to be tested". Since an element is always
      one character it has little use; consider removing it.
- [ ] `get_segment(output=...)` accepts only `'string'` yet returns a
      `PhoSegment`, not a string (line 566). Drop the parameter or implement
      it.
- [ ] The docstring header says "version: 0.2" (line 3) while the real
      version comes from git tags. Remove the hardcoded number.
- [ ] The `__main__` block at the bottom of `ipa_map.py` (lines 667-684) is
      leftover manual testing. Move anything useful into the tests.

## 3. Tests

- [ ] Three tests fail because they describe features that do not exist yet:
      `test_ipa_parser_invalid_sequences`,
      `test_ipa_parser_diacritic_role_switchers` and
      `test_ipa_parser_compound_phones`. Mark them
      `@pytest.mark.xfail(reason=...)` so the suite is green and a real
      regression is visible, then remove the marks as each feature lands.
- [ ] `test_ipa_parser_invalid_sequences` only exercises its first line. The
      four calls sit inside one `pytest.raises` block, so the block exits at
      the first exception. Use one block per input or
      `pytest.mark.parametrize`.
- [ ] Add tests for the public helpers that have none: `get_bases`,
      `get_bases_string`, `get_segment`, and the non-string (NaN) input path
      that `phon_query_to_csv` relies on.
- [ ] Add a table integrity test: unique `Symbol` values (currently true),
      every `Role` and `Type` in the expected set, and no base consonant
      missing a required feature once section 1 is settled.
- [ ] Delete `tests/test_skeleton.py` together with `skeleton.py`
      (section 5).
- [ ] No CI is configured. A single GitHub Actions job running `pytest` would
      catch table edits that break parsing.

## 4. Packaging

- [ ] Declare `pandas` in `install_requires` in `setup.cfg`. A fresh install
      cannot import the package without it.
- [ ] Replace the leftover console script `fibonacci =
      ipa_features.skeleton:run` with a real one, for example `ipa-parse =
      ipa_features.__main__:run`.
- [ ] Fix `url` and the `Documentation` link in `setup.cfg` (both still point
      at pyscaffold.org).
- [ ] Licensing is inconsistent: `LICENSE.txt` and `setup.cfg` say MIT,
      `src/ipa_features/LICENSE` is Apache 2.0, and `logging_config.py`
      carries an Apache header. Pick one.
- [ ] `python_requires` is already `>=3.8`, so the conditional import in
      `__init__.py` can be simplified as its own TODO comment notes, and the
      `importlib-metadata` requirement removed.
- [ ] `phon_query_to_csv` needs this package but cannot declare it until it
      is installable by URL or published. Tag a release so it can be pinned.

## 5. Repository cleanup

- [ ] `reDiac.py` and `regex_find_generator.py` do not work as package
      modules (not run; from reading):
      - `regex_find_generator.py` calls itself at import time (line 70),
        which reads and overwrites the clipboard.
      - Its `input` parameter shadows the builtin, so the `input('Paste
        input: ')` fallback would call `None`.
      - `reDiac.py` imports it by bare name, opens `phon_diacritics.csv`,
        which is not in the repository, has an unused `tokenize` import, and
        is missing a comma between the last two entries of
        `unicodeBlockList`.
      - Both need the `regex` package, which is not declared.
      Move them to a scripts folder outside the package, or delete them.
- [ ] Remove `skeleton.py` and the PyScaffold template docstring at the top
      of `__main__.py`, along with the empty `ipa_features()` stub there.
- [ ] `src/ipa_features/` still contains the `README.md`, `LICENSE`,
      `.gitignore` and `.gitattributes` of the old `IPA_symbol_table`
      repository. Remove them.
- [ ] One source of truth for the table. The CSV and the XLSX are both
      tracked here, and the `IPA_symbol_table` repository holds another copy
      of each. Decide which file is edited by hand, generate the other from
      it, and either archive `IPA_symbol_table` or state in its README that
      this repository is canonical.
- [ ] Delete the merged remote branches `implement_segments` and
      `ipa_features_2` (both have no commits that are not on `main`).
- [ ] Fill in `CHANGELOG.rst`, which still has the PyScaffold sample entries.

## 6. Existing notes carried over from the code

Already written as `TODO` comments and not covered above.

- [ ] Implement or remove the `tier`, `parent` and `position` attributes
      (lines 83-87, 182). The module docstring already asks whether they are
      still relevant.
- [ ] `PhoCompound` subclass of `PhoBase` (line 267), and whether
      `PhoLigature` should be a diacritic subclass (line 320).
- [ ] Stress on `PhoSegment`, and a future `PhoSyllable` (line 341).
- [ ] A `get_diacritics()` method on `PhoSegment` (line 418).
- [ ] Handle multiple bases in `get_bases` and `get_bases_string`
      (lines 628, 660).
- [ ] Test for a compound-base segment (`tests/test_ipa_map.py:180`).

## Suggested README changes

`README.rst` was left untouched. It is still the PyScaffold placeholder
("Add a short description here!"), and `docs/readme.rst` includes it, so the
Sphinx docs are empty too. Suggest replacing its body with the content of
`OVERVIEW.md` and then deleting `OVERVIEW.md`.
