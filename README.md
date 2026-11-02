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

A data-first SQLite SELECT builder for Arturo 0.10.0+.

```art
import {sql}!

minimumAge: 18
statement: sql [
    select [id name email]
    from users
    where [
        age >= (minimumAge)
        and [active = true or role = "admin"]
    ]
    orderBy [name asc]
    limit 20
]
compiled: to :sqliteQuery statement
inspect compiled\text
inspect compiled\params
```

`sql` parses the block into an inspectable dictionary. `to :sqliteQuery` converts
it into a `:sqliteQuery` object with `text` and `params` fields without executing
SQL. SQL text uses one clause per line with four-space indentation. Identifiers
are quoted and values use positional `?` parameters. Execute on an Arturo SQLite
connection with the built-in `query`:

```art
db: open.sqlite ":memory:"
query db "CREATE TABLE users (id INTEGER, name TEXT, email TEXT, age INTEGER, active INTEGER, role TEXT)"
query db {INSERT INTO users VALUES (1, 'Ada', 'ada@example.com', 30, 1, 'member')}
failure: try [
    rows: query.with: compiled\params db compiled\text
    inspect rows
]
close db
unless null? failure [throw to :string failure]
```

The compiled `text` and `params` fields pass directly to `query.with:`. Boolean
values compile to SQLite integers (`true` → `1`, `false` → `0`), so parameters
are ready to bind without further conversion. The query dictionary retains the
original values. Arturo returns its native block of rows (cells are strings on
Arturo 0.10.0), and database errors propagate to the caller.

`sqliteExecute db statement` remains a convenience wrapper accepting either a
query dictionary or a compiled `:sqliteQuery` and calling the same built-in API.
The caller opens and closes the connection. No external SQLite package is
required. See `examples/sqlite.art` for a runnable example.

### Terminal tables

Use `sqliteTable` to execute a query and format its results with the `tabular`
package (installed as a dependency). Print the returned string in the terminal:

```art
print sqliteTable.header: ["ID" "Name" "Email"] db statement
```

Both query dictionaries and compiled `:sqliteQuery` objects are accepted.
The optional `.header:` labels must match the number of result columns; omit
them for a table without a header, including with `select [*]`. Empty results
return `"No rows."`. The caller still owns and closes the database connection.
Run `arturo examples/sqlite.art` for a complete terminal example.

Use `statement` rather than `query` as a variable when using the database API:
Arturo already defines a function named `query`.

### Grammar

Clauses occur in order: `select`, `from`, repeated `where`, optional `orderBy`,
optional `limit`, optional `offset`. The last requires a limit. Pagination accepts
nonnegative integers, including zero. Ordering accepts `[name asc id desc]`;
omitted directions default to ascending.

Columns and tables are bare words; `select [*]` selects all columns. Predicates
support `=`, `<>`, `!=`, `<`, `<=`, `>`, `>=`, `is null`, and `is not null`.
Use explicit null tests rather than `= null`. Bare words represent identifiers;
strings, numbers, and booleans represent values. Keywords are case-sensitive.

`and` binds more tightly than `or`. Nested blocks group conditions. Repeated
`where` clauses combine with AND, preserving each predicate's grouping.

Parentheses evaluate trusted Arturo code once during construction, including
function-local variables. Each expression must return exactly one string,
number, or boolean. Later compilations reuse the stored value. Internal helper
bindings use `_sql` prefixes; avoid those names in dynamic expressions.

Query dictionaries contain `kind`, `columns`, `table`, `predicates`, `ordering`,
`limit`, and `offset`. Predicates use tagged dictionaries for comparisons,
boolean operations, null tests, identifiers, and bound values. Compilation does
not mutate these dictionaries.

Joins, aliases, qualified identifiers, aggregates, subqueries, writes, raw SQL,
IN, LIKE, BETWEEN, and NOT groups are outside this initial release.

## Development

Run `unitt`, `arturo src/main.art`, or `arturo examples/select.art`, or
`arturo examples/sqlite.art`.

### SELECT attributes

Use `select.distinct [name]` to remove duplicate rows, or
`select.as: [userId userName] [id name]` for positional aliases.
Alias counts must match; wildcards cannot have aliases.

`select.expressions` enables structured projections:

```art
sql [
    select.expressions.as: [total adjusted] [
        [count [*]]
        [+ amount 2]
    ]
    from orders
]
```

Attributes can combine, including `select.distinct.expressions.as:`.
Aggregates support `count`, `sum`, `avg`, `min`, and `max` with a
single argument block; only count accepts a wildcard. Arithmetic uses binary
prefix blocks with `+`, `-`, `*`, or `/` and supports nesting.
Scalar values are parameterized; parentheses still evaluate Arturo code once.

### Runnable, self-testing examples

Each example includes assertions and exits with an error if a check fails.
SQLite examples use an in-memory database and close it after execution.

| Command | Demonstrates |
| --- | --- |
| `arturo examples/select.art` | Compilation, captured values, and parameter checks |
| `arturo examples/sqlite.art` | Execution and terminal tables |
| `arturo examples/aliases.art` | Positional column aliases |
| `arturo examples/distinct.art` | Duplicate removal |
| `arturo examples/aggregates.art` | COUNT, SUM, AVG, MIN, MAX with aliases |
| `arturo examples/arithmetic.art` | Nested addition, subtraction, multiplication, division |
| `arturo examples/combined.art` | Combined attributes and captured expression values |

CI runs all these examples alongside the unit specifications.
