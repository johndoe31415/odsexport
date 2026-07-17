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
it:

  - [Produced ODS file](https://github.com/johndoe31415/odsexport/raw/refs/heads/main/example/example_document.ods)
  - [Source code](https://github.com/johndoe31415/odsexport/blob/main/example/write_example_document.py)


## Cell formatting
When handing cells or cell ranges from odsexport, there are three format
characters that are understood:

  - `a`: Create an absolute reference, i.e., include the sheet name. Needs to
    be used when referencing cells between different sheets.
  - `c`: Pin the column. I.e., instead of `G4`, it will produce `$G4`.
  - `r`: Pin the row. I.e., instead of `G4`, it will produce `G$4`.
  - `b`: Put the cell expression in braces, e.g., produce `[.G4]` instead of
    `G4`. This is required inside all fomula expressions which are manually
    created and will lead to subtle errors if omitted.

All of these can be combined, here is an example of a sheet "Sheet" with cell
`G4`:

  - `a`: `Sheet.G4`
  - `c`: `$G4`
  - `r`: `G$4`
  - `cr`: `$G$4`
  - `acr`: `Sheet.$G$4`
  - `abcr`: `[Sheet.$G$4]`


## Formulas
odsexport offers a thin layer of expressions so that Pythonic formula references can be used
in an operator-overloaded manner. When those formulas and cell references are used, the cell notation is automatically
put in braces. For example, this is a valid construct:

```python3
cylinder_volume = (odsexport.CellRef(radius_cell) ** 2) * 3.1415 * height_cell
```

Note that you only need to wrap the cell into an expression once (here, using
`odsexport.CellRef`), then subsequent mathematical operations are automatically
wrapped. Note that you can construct formulas by using Python constructs which
will be translated into formulas. Even expressions can be written natively in
Python. Consider this example:

```python3
hour_ref = odsexport.CellRef(hour_cell)
formula = ((hour_ref >= 0) & (hour_ref <= 24)).then("Valid", else_value = "Invalid")
```

Which will render to the Excel formula `=IF(AND(B20>=0;B20<=24);"Valid";"Invalid")`.

Here, the relational operators `<`, `<=`, `>`, `>=`, `==` and `!=` may be used
as well as `&` for boolean AND, `|` for boolean OR and `~` for boolean NOT.


## Manual formulas
You can also completely manually write the formulas as strings. Inside such
formulas, brace notation must be used for all cell references. odsexport does
treat formulas which are provided as strings as-is and acts completely dumb
with them. It will happily accept anything you throw at it. However, note that
a misformatted formula (e.g., a cell that uses `Sheet.G4` instead of the
correct `[Sheet.G4]`) will lead to interoperability issues. OpenOffice will
read such a document just fine while Excel will reject it and throw an error.
**It is the responsibility of the odsexport user to use cell references
correctly when using manual formulas.**


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
even remotely acceptable? Why is this whole standard so terribly inconsistent
and requires [brackets] for cell references in certain cases, but not others?
Why does Excel hide a column just right if `table:visibility` is set to
`collapse` but doesn't do the same for rows unless there is a style name set
(even if that style is completely empty)? Who can actually, seriously, work
with this raging dumpster fire?

Excel/LibreOffice Calc is an utter disgrace. And yet, just like thousands of
people before me, I need to cope with it. To me, that compromise is having
actual good data quality in a safe haven and only exporting to Excel when
needed.


## Acknowledgements
The cute watermelon 16x16 icon is courtesy of
[Suzana Assets (Fruits Icons - 16x16)](https://suzana-assets.itch.io/). Thanks!


## License
GNU GPL-3.
