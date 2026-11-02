<h1 align="center">sql</h1>

<p align="center">
    <i>An SQL Builder for Arturo</i>
    <br><br><br>
    <img
        src=./docs/icons/arturo-light-mode.png#gh-light-mode-only
        alt=Arturo logo
        width=20
    />
    <img
        src=./docs/icons/arturo-dark-mode.png#gh-dark-mode-only
        alt=Arturo logo
        width=20
    />
    <br>
    <b>~ CODE IS ART ~</b>
    <br><br>
</p>

<p align="center">
    <a href="https://www.arturo-lang.io"><img src="https://img.shields.io/badge/language-Arturo-6A156B.svg?&style=flat&colorA=000000&colorB=000000" alt="Langukvage: Arturo"/></a>
    &nbsp;
    <a href="https://github.com/RickBarretto/pkgr.sql.art/blob/main/LICENSE"><img src="https://img.shields.io/github/license/RickBarretto/pkgr.sql.art?&style=flat&colorA=000000&colorB=000000" alt="License"/></a>
    &nbsp;
    <a href="https://github.com/RickBarretto/pkgr.sql.art/actions"><img src="https://img.shields.io/github/actions/workflow/status/RickBarretto/pkgr.sql.art/test.yml?branch=main&style=flat&colorA=000000&colorB=000000" alt="CI Status"/></a>
</p>

## At a Glance

<p align="center">
    <img alt="At a Glance" width="720"
    src="./docs/images/"
    />
</p>

## Installation

```sh
arturo -p install sql
```

or

```art
import {sql}!
```

## Documentation

An SQL builder for Arturo 0.10.0+, using the function API in [api/API.md](api/API.md).
Every DSL command belongs inside `sql [...]`. Bodies are captured as SQL data;
helpers do not replace Arturo's built-in functions.

```art
import {sql}!

minimumYear: 2020
statement: sql [
    from :books
    select [title publishedYear]
    where -> and publishedYear >= (minimumYear) available = true
    order.desc 'publishedYear
    order 'title
    limit.skip: 0 20
]
compiled: to :sqliteQuery statement
inspect compiled\text
inspect compiled\params
```

`sql` returns an inspectable dictionary. `to :sqliteQuery` produces `text` and
`params` without executing SQL or mutating the statement. Values use `?` parameters;
booleans use SQLite integer values. Renderer-local adapters add numeric casts
where scalar expressions lack column affinity, and preserve SQL nulls on Arturo
runtimes that bind parameters as text. These helpers do not replace native Arturo
functions and leave scope after rendering. Parenthesized Arturo computations run once during
construction, including computations using function-local variables.

Tables, columns and aliases accept types, literals, strings, paths, literal paths,
and captured words. Prefer `:books` for tables and `'title` for single columns.
Identifiers are quoted; strings inside predicates, expressions and rows are values.
Explicit literals allow identifiers that match DSL keywords.

### Queries

Query clauses may appear in any order; the compiler arranges them. Repeated
`select` calls append projections, repeated `where` and `having` calls combine
with AND, and repeated `order` calls append sort keys. Each command consumes its
documented arguments. `->` captures one complete expression, including single
commands such as `insert.columns: [title] :books -> row ["River Atlas"]`.

```art
sql [
    from :books
    select 'genre
    select.count.as: 'total "*"
    select avg 'pageCount
    group 'genre
    having [[count "*"] > 3]
    order.desc 'genre
]
```

Projections support `.distinct`, `.as:`, `.count`, `.sum`, `.avg`, `.min`, `.max`,
`.coalesce` and `.nullif`. Composed helpers include aggregates, `coalesce`,
`nullif` and `choose` with `when`/`otherwise` branches or `.default:`.
Only COUNT accepts a wildcard. Alias counts must match projections. CASE result
branches must have compatible scalar types; integers and floating-point values
may mix, and null is accepted with any result type.

Predicates support comparisons (including `=<`), prefix `and`, `or`, `not`,
`in`, `between`, `like`, `is null`, and `is not null`. Nested blocks preserve
grouping. Use null tests rather than comparison with null. Scalar helpers can
appear on either side of a comparison. Arithmetic uses Arturo's grouping from
the right; explicit blocks change grouping:

```art
sql [
    from :books
    select coalesce [[nullif subtitle ""] title]
    select.as: 'adjusted + pageCount 2
    where [coalesce [subtitle title] like "River%"]
    where [[pageCount + 2] * 3 >= 300]
]
```

`join` defaults to INNER and accepts `.left`, `.right`, `.full` and `.as:`.
`cross` takes a table with optional `.as:` and no predicate. Nested `query`
expressions, correlated column paths, `exists`, `with` CTEs and
`combine.union`/`.intersect`/`.except` are supported. Scalar subqueries require
one projection and set operations require matching projection counts. Each set
operand retains its own ORDER BY, pagination and CTE scope.

Qualified references must name a local table or alias. A table alias hides its
original table name. Correlations refer to explicit outer aliases; inner aliases
stay inside their query. Duplicate relation aliases are rejected. Trigger `new`
and `old` references are available for INSERT and DELETE respectively, and both
are available for UPDATE.

`limit` accepts a nonnegative count and optional `.skip:`; `offset` is an
alternative to `.skip:` and requires pagination. Use explicit ordering for
stable pages. Earlier `orderBy`, infix boolean predicates and
`select.expressions` remain available for existing callers.

### Schema and writes

```art
sql [create :books [
    column.primary 'id :integer
    column 'title :string
    column.optional 'subtitle :string
]]

sql [insert.columns: [id title] :books [
    row [1 "River Atlas"]
    row [2 "Quiet Maps"]
]]

sql [update :books [assign 'title "New title" where [id = 1]]]
sql [delete :books [where [id = 2]]]
sql [alter :books -> add.optional 'pageCount :integer]
```

Columns default to NOT NULL. `.optional` permits null and cannot combine with
`.primary`. `.unique`, table `reference` and `check` constraints are supported.
SQLite storage mappings are INTEGER, TEXT, REAL and BLOB. Alter bodies support
one `add`, `remove` or `rename` per SQLite statement.

INSERT requires explicit columns and matching row widths. UPDATE supports
`assign` and `.values: [column: value]`; write values may include null.
`create.view`, `drop.view` and `create.trigger` support stored schema statements.
SQLite prohibits placeholders in stored definitions: scalar AST values in CHECK,
views and triggers are rendered as escaped SQL literals. Pagination counts in
stored queries are rendered as nonnegative integers. Ordinary queries and
writes remain parameterized.

The builder also accepts the reference's FETCH, grouping extensions, ALL/ANY,
identity and TRUNCATE forms as data. Conversion to SQLite rejects these with
explicit errors because SQLite does not support their SQL syntax. RIGHT/FULL
joins and ALTER DROP COLUMN depend on the SQLite version bundled with Arturo.

### Execution and terminal tables

```art
db: open.sqlite ":memory:"
failure: try [
    ignored: sqliteExecute db sql [create :books [column 'title :string]]
    ignored: sqliteExecute db sql [insert :books [columns 'title row ["River Atlas"]]]
    print sqliteTable.header: ["Title"] db sql [from :books select 'title]
]
close db
unless null? failure -> throw to :string failure
```

The caller owns the connection. `sqliteExecute` accepts dictionaries or compiled
queries, returning native rows for SELECT and an empty block for commands that
produce no rows. Database errors propagate. Compiled fields also work directly
with Arturo's `query.with: compiled\params db compiled\text`.

`sqliteTable` returns a formatted string using the `tabular` dependency.
Optional `.header:` labels must match the result width; empty results return
`"No rows."`.

## Development

Run `unitt`, `arturo src/main.art`, and the self-testing scripts in `examples/`.
`examples/api.art` demonstrates the function API with an in-memory database.
The contracts and feature catalog live in `api/`; dialect-specific limitations
are described above. [TODO.md](TODO.md) tracks each API feature and outstanding
dialect support. Unitt also constructs every catalog example and checks that each
`sql` call returns exactly one statement.
