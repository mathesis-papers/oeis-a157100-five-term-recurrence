# Mathar's Catalan-transform recurrence and related identities

This note gives an alternative coefficient proof, using Richard J. Mathar's
2021 root-generating-function theorem, of his five-term conjecture in
OEIS A157100, revision 14, FORMULA line 11, signed 5 February 2015.
For `A(x)=(1+x)C(x(1-x^2))=sum a_n x^n`, it proves the recurrence for
every `n >= 4`, with initial values `1, 2, 3, 6` and uniqueness.

It also establishes the offset-aware relation `B=x(1-x)A` to A025262,
corrects the printed ratio to `A/B=1/[x(1-x)]`, derives Somos's bilinear
identity, and proves Mathar's A025268 six-term conjecture for `n >= 6`
from Kotesovec's shorter recurrence. The remaining corollaries give
binomial formulas, the shifted A056010 generating functions, A176703 row
sums, Adamson's constructions and the leading asymptotic constants.
Earlier formulas, general methods and related combinatorial or determinant
results are individually attributed in the note's coverage table and references.

## Contents

- `note.tex`: LaTeX source with its bibliography.
- `metadata.json`: title, mathematical scope, creators and license.
- `verify.py`: standard-library Python 3 exact coefficient and polynomial checks.
- `verification.json`: finite-check results, including three coefficient-table comparisons.
- `tables/b157100.txt`, `tables/b025262.txt`, `tables/b025268.txt`: public coefficient tables.
- `tables/sources.json`: URLs and SHA-256 hashes of those tables.

## Build the PDF

Use Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
```

Alternatively, use a standard LaTeX distribution:

```sh
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error note.tex
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is included in `note.tex`; no BibTeX step is required.

## Reproduce the finite checks

```sh
python3 verify.py --oeis-table tables/b157100.txt \
  --sibling-table tables/b025262.txt --neighbor-table tables/b025268.txt \
  > verification-reproduced.json
cmp verification.json verification-reproduced.json
```

All arithmetic is exact: unbounded integers, with rational arithmetic for
the general radical examples. The default limit is 1000; `--limit N`
accepts `8 <= N <= 2000`. The A157100 table ends at 1000, so table-based
comparisons beyond that index require a longer independently supplied table.
The default output covers:

- A157100: agreement of Catalan substitution, convolution with partial sums,
  and the five-term recurrence at indices 0 through 1000; the full coefficient
  differential equation, including its two inhomogeneous coefficients.
- A025262: binomial formula, positivity and linear recurrence through 1001;
  Somos's bilinear identity for 1 through 997.
- A056010: the double-binomial formula and convolution at 0 through 100;
  the shifted bilinear identity at 0 through 995.
- A176703: polynomial row sums at rows 0 through 30.
- A025268: the shorter recurrence for 5 through 1000, the six-term
  recurrence for 6 through 1000, and the zero-extended value -40 at index 5.
- Adamson's two constructions; exact bilinear elimination and recurrence
  combination identities; the asymptotic constants' polynomial reductions;
  and four general-radical coefficient examples at indices 1 through 30.

The three external tables agree on A157100 indices 0 through 1000,
A025262 indices 1 through 1001, and A025268 indices 1 through 1000.
Their exact file hashes are included in `verification.json`.
These finite comparisons accompany the written all-index proofs.

## Lean statement coverage

At revision `962b1e14510f845c23345d34b4fb8205b2ddc2bd`, the declaration
`D5.S1.Recurrence.Algebraic.MatharA157100FiveTermRecurrence.result`
in the following file proves the five-term recurrence over rational
coefficients for every `n >= 4`:

https://github.com/the-omega-institute/trureturing/blob/962b1e14510f845c23345d34b4fb8205b2ddc2bd/D5/S1/Recurrence/Algebraic/MatharA157100FiveTermRecurrence.lean

Its dependency provides `cat_ode`, the Catalan differential identity,
and `euler_coeff`, the coefficient rule `[x^n](xF')=n[x^n]F`:

https://github.com/the-omega-institute/trureturing/blob/962b1e14510f845c23345d34b4fb8205b2ddc2bd/D5/S1/Recurrence/A308815DFiniteRecurrence.lean

The initial values, uniqueness, ratio correction, general radical formula
and added corollaries have written proofs in the note; the three declarations
above have the specific statements just described.

## Authors and license

Haobo Ma — ChronoAI Pte Ltd, Singapore.

Wenlin Zhang — National University of Singapore;
ChronoAI Pte Ltd, Singapore.

Creative Commons Attribution 4.0 International (CC BY 4.0), `cc-by-4.0`.
The OEIS coefficient tables retain their original headers and attribution;
they are separately licensed CC BY-SA 4.0 by the OEIS Foundation Inc.
Their license text is in `tables/LICENSE-OEIS.txt`.
