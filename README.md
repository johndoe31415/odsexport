# odsexport
odsexport is a Python-native library to create ODS (Open Document Spreadsheet)
documents. In other words, it lets you script creating "Excel" sheets from
within Python. The focus is on providing a feature-rich document creation
abstraction: all kinds of cell formatting options (data and style formatting,
including datetimes) are supported, column and row formatting is supported
(width/height/visibility), conditional formatting, and auto filtering is
implemented as well. odsexport is intended to make it easy to use ODS documents
as a data sink while creating documents that are mutable (i.e., recalculate
their cells according to formulas). An example of what documents it can produce
is given in the `example` directory along with the source code that produced
it.

## Cell formatting
When handing cells or cell ranges from odsexport, there are three format
characters that are understood:

  - `a`: Create an absolute reference, i.e., include the sheet name. Needs to
    be used when referencing cells between different sheets.
  - `c`: Pin the column. I.e., instead of `G4`, it will produce `$G4`.
  - `r`: Pin the row. I.e., instead of `G4`, it will produce `G$4`.

All of these can be combined, here is an example of a sheet "Sheet" with cell
`G4`:

  - `a`: `Sheet.G4`
  - `c`: `$G4`
  - `r`: `G$4`
  - `cr`: `$G$4`
  - `acr`: `Sheet.$G$4`


## Rant
Personally, I hate Excel or LibreOffice with a burning passion. That such an
ugly, stinking turd of software is used by millions of people around the globe
already seems odd. It is pretty much guaranteed that somewhere the salaries of
people depend on this utterly shitty, piss-poor quality application. Worse yet,
possibly some engineer is making structural computations using Excel, where
lives may depend on the accuracy of the results. The thought alone makes me
want to cry out in pain. Software so stupid, broken and obnoxious that
computations may not only not work on the exact same software with a different
locale setting, nooooo, even worse: it may silently ignore the locale errors
and produce wrong results. Don't believe me? Try counting values using
`COUNTIF()` with a condition that counts values greater than/less than a
fractional value and observe what happens when the locale setting (e.g., `4.1`
vs. `4,1`) is different than the number you enter. It really is *that* dumb.
Oh, or have you looked at the `SUBTOTAL` function? You know, that function that
computes different things depending on a given function *index* as a parameter?
Like, if you want a `SUM`, that's function 9 but if you want the maximum value
that's obviously 4. Who ever thought this train wreck of spreadsheeting was
even remotely acceptable?

Excel/LibreOffice Calc is an utter disgrace. And yet, just like thousands of
people before me, I need to cope with it. To me, that compromise is having
actual good data quality in a safe haven and only exporting to Excel when
needed.

## License
GNU GPL-3.
