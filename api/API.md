# SQL API reference

Use this reference for command arguments, validation rules, and compiled output.
For installation and a first query, start with the [quick start](../README.md#quick-start).
The [style guide](STYLE.md) covers layout; the [feature catalog](README.md)
provides more examples.

## On this page

- [Identifiers and values](#identifiers-and-values)
- [Query commands](#query-commands)
- [Predicates](#predicates)
- [Expressions and aggregates](#expressions-and-aggregates)
- [Subqueries, CTEs, and set operations](#subqueries-ctes-and-set-operations)
- [Tables and constraints](#tables-and-constraints)
- [Inserts, updates, and deletes](#inserts-updates-and-deletes)
- [Views and triggers](#views-and-triggers)
- [Compiled output](#compiled-output)
- [Execution and formatting](#execution-and-formatting)
- [Compatibility syntax](#compatibility-syntax)

## Statement basics

`sql [...]` builds a statement dictionary. Every DSL command belongs inside
that block or one of its nested bodies. Importing the package leaves Arturo's
built-in functions intact.

- **Build:** `statement: sql [from :books select 'title]`
- **Compile:** `to :sqliteQuery statement` or `to :postgresQuery statement`
- **Execute on SQLite:** `sql.query: db statement`

Compilation returns SQL and parameters. It does not execute SQL or change the
statement.

## Identifiers and values

Commands inside `sql [...]` treat table and column names as SQL identifiers.
They do not look up those names as Arturo variables. Identifiers are quoted
when compiled.

| Form | Table example | Column example |
| --- | --- | --- |
| Type | `from :books` | `select :title` |
| Literal | `from 'books` | `select 'title` |
| String | `from "books"` | `select "title"` |
| Path | `from main\books` | `select b\title` |
| Literal path | `from 'main\books` | `select 'b\title` |
| Word | `from books` | `select [title publishedYear]` |

These forms also work for aliases, views, triggers and constraint columns.
Use a literal such as `'count` when an identifier matches a DSL command or
expression helper. Use `"*"` to select all columns or as the operand of `count`.

An identifier list accepts one name or a block of names.

> [!IMPORTANT]
> A string's role depends on its position. `select "title"` names a column;
> `where [title = "River Atlas"]` compares that column with a bound value.

Scalar values are strings, integers, floating-point numbers, booleans or null.
Ordinary values become bind parameters. Prefix a variable with `@`, such as
`@maximumYear`, to capture its scalar value. Parentheses evaluate Arturo code once
when the statement is built, including variables local to the calling function:

```art
minimumPages: 200
statement: sql [
    from :books
    select 'title
    where [pageCount >= (minimumPages + 20)]
]
```

Square brackets inside a predicate group SQL expressions. Parentheses run
Arturo code.

## Query commands

Each query requires one `from` and at least one projection. Clauses may appear
in any order; compilation puts them in SQL order. Each command consumes its
arguments regardless of line breaks. A body is required even for one command:
use `->` for one complete expression and `[...]` for several commands.

In the tables below, **identifier** means any name form shown above,
**identifiers** means one name or a block of names, and **expression** means a
column, scalar value, helper call or arithmetic expression where supported.

| Command | Arguments | Options and behavior |
| --- | --- | --- |
| `from` | identifier | Exactly one source; `.as:` sets its alias |
| `select` | identifier, identifier list or expression helper call | Appends projections; `.as:` supplies matching aliases; `.distinct` applies to the whole result |
| `select.count`, `.sum`, `.avg`, `.min`, `.max` | identifier | Appends one aggregate; only count accepts `"*"` |
| `select.coalesce`, `.nullif` | operand block | At least two operands for coalesce; exactly two for nullif |
| `where` | predicate block | Repeated calls combine with AND |
| `join` | table identifier, predicate block | INNER by default; `.inner`, `.left`, `.right`, `.full`; optional `.as:` |
| `cross` | table identifier | CROSS JOIN; optional `.as:` |
| `order` | identifiers | Ascending by default; `.asc` or `.desc`; repeated calls append keys |
| `group` | identifiers | Plain GROUP BY; `.rollup`, `.cube` and `.sets` select grouping extensions |
| `having` | predicate block | Repeated calls combine with AND |
| `limit`, `fetch` | integer count | Optional `.skip:` offset; count and offset must be nonnegative |
| `offset` | integer count | Requires limit or fetch; cannot also use `.skip:` |
| `with` | identifier, query body block | Defines a CTE |

Validation rules:

- Use one alias for one projection, or a matching block of aliases for several.
  Wildcards cannot be aliased.
- Choose one mode per command. Conflicting flags such as `order.asc.desc` fail.
- Use at most one grouping clause and one pagination count per query.
- Pass a nonempty block of grouping blocks to `group.sets`. Individual grouping
  blocks may be empty.

```art
statement: sql [
    from.as: 'b :books
    join.left.as: 'p :publishers [b\publisherId = p\id]
    select.as: [title publisher] [b\title p\name]
    where [b\available = true]
    order 'b\title
    limit.skip: 20 10
]
```

Qualified names must refer to a table or alias in scope. An alias hides the
original table name. Duplicate relation aliases are rejected.

## Predicates

| Form | Example |
| --- | --- |
| Comparison | `where [pageCount >= 200]` |
| AND | `where [and available = true pageCount >= 200]` |
| OR | `where [or genre = "Poetry" genre = "History"]` |
| NOT | `where [not available = true]` |
| IN | `where [genre in ["Poetry" "History"]]` |
| BETWEEN | `where [publishedYear between [2000 2020]]` |
| LIKE | `where [title like "River%"]` |
| Null test | `where [subtitle is null]` or `where [subtitle is not null]` |

Comparisons accept `=`, `<>`, `!=`, `<`, `<=`, `=<`, `>` and `>=`.
Both `<=` and `=<` compile to SQL `<=`.

- **Null:** use `is null` or `is not null`. Direct comparisons with null fail.
- **IN:** supply a nonempty value list.
- **BETWEEN:** supply exactly two endpoints.

Prefix `and` and `or` each take two predicates; `not` takes one. Nested blocks
make grouping explicit. Repeated `where` calls are another way to express AND.
Scalar helpers and arithmetic can appear on either side of a comparison.

```art
statement: sql [
    from :books
    select 'title
    where [and
        [or genre = "Poetry" genre = "History"]
        publishedYear >= 2020
    ]
    where [coalesce [subtitle title] like "River%"]
]
```

## Expressions and aggregates

| Helper | Arguments | Behavior |
| --- | --- | --- |
| `count`, `sum`, `avg`, `min`, `max` | column identifier | One aggregate; only count accepts `"*"` |
| `coalesce` | operand block | First non-null operand; at least two operands |
| `nullif` | two expressions | Null when the operands are equal |
| `choose` | branch block | SQL CASE; optional `.default:` scalar value |
| `when` | predicate block, scalar value | One branch inside choose |
| `otherwise` | scalar value | Fallback inside choose; alternative to `.default:` |

Compose helpers directly after `select`. A plain projection list such as
`[title publishedYear]` contains identifiers; use separate `select` calls for
calculated projections.

```art
statement: sql [
    from :books
    select 'genre
    select.as: 'total count "*"
    select.as: 'averagePages avg 'pageCount
    group 'genre
    having [[count "*"] > 3]
]

statement: sql [
    from :books
    select coalesce [[nullif subtitle ""] title]
    select.as: 'length choose [
        when [pageCount >= 300] "Long"
        otherwise "Short"
    ]
    select.as: 'adjusted + pageCount 2
]
```

CASE requires at least one `when`. Result values must have compatible types;
integers and floats may mix, and null is compatible with any result type.
COALESCE substitutes for SQL null, including when another operand is false.

Arithmetic supports `+`, `-`, `*` and `/` in prefix or infix position and groups
from the right. Use blocks to change grouping, as in
`where [[pageCount + 2] * 3 >= 300]`.

## Subqueries, CTEs, and set operations

### Nested queries

- `query [body]` builds a nested SELECT.
- Scalar subqueries, `all query [...]`, and `any query [...]` require one projection.
- `exists query [...]` tests whether a nested query returns rows.

Correlated queries refer to explicit outer aliases. Inner aliases stay inside
their query; CTE definitions have independent table and alias scopes.

```art
statement: sql [
    from.as: 'b :books
    select 'b\title
    where [exists query [
        from.as: 'l :loans
        select 'l\bookId
        where [l\bookId = b\id]
    ]]
]

statement: sql [
    with :recent [
        from :books
        select [title publishedYear]
        where [publishedYear >= 2020]
    ]
    from :recent
    select 'title
]
```

### Set operations

Use `combine.union`, `combine.intersect` or `combine.except` with a block of at
least two `sql [...]` SELECT calls. Projection counts must match. Each operand
retains its own ordering, pagination and CTE scope.

```art
statement: sql [combine.union [
    sql [from :books select 'title where [genre = "Poetry"]]
    sql [from :books select 'title where [genre = "History"]]
]]
```

## Tables and constraints

| Command | Arguments | Behavior |
| --- | --- | --- |
| `create` | table identifier, definition block | Creates a table |
| `column` | identifier, storage type | NOT NULL by default; `.optional`, `.primary`, `.unique`, `.identity` flags |
| `reference` | local identifiers, table identifier, target identifiers | Table foreign key; column counts must match |
| `check` | predicate block | Table CHECK constraint |
| `alter` | table identifier, change block | Changes a table |
| `add` | identifier, storage type | Adds a column inside alter; same flags as column |
| `remove` | column identifier | Drops a column inside alter |
| `rename` | new table identifier | Renames the table inside alter |
| `drop` | table identifier | Drops a table |

```art
statement: sql [create :books [
    column.primary 'id :integer
    column 'title :string
    column.optional 'subtitle :string
    column 'publisherId :integer
    reference 'publisherId :publishers 'id
    check [id > 0]
]]

statement: sql [alter :books -> add.optional 'pageCount :integer]
```

- `.optional` permits null and omits NOT NULL. It cannot combine with `.primary`.
- `.required` is not a supported flag; columns are already required by default.
- `.identity` requires an integer, non-optional column. It does not add a primary key.

### Storage types

| Arturo storage type | SQLite | PostgreSQL |
| --- | --- | --- |
| `:integer` | INTEGER | INTEGER |
| `:string` | TEXT | TEXT |
| `:logical` | INTEGER | BOOLEAN |
| `:floating` | REAL | DOUBLE PRECISION |
| `:binary` | BLOB | BYTEA |

Other storage types produce a compilation error.

- **SQLite:** use one alteration per statement. Its restrictions on adding
  primary or unique columns still apply.
- **PostgreSQL:** several additions or removals may share an ALTER statement,
  but a table rename must be a separate statement.

DROP COLUMN and RIGHT/FULL JOIN require a supporting SQLite runtime version.

## Inserts, updates, and deletes

| Command | Arguments | Behavior |
| --- | --- | --- |
| `insert` | table identifier, body block | Explicit `columns` or `.columns:` and at least one row |
| `columns` | identifiers | Sets insert column order |
| `row` | scalar value block | Adds a row; width must match the column count |
| `update` | table identifier, body block | At least one assignment; optional `.values:` label/value block |
| `assign` | column identifier, scalar value | Adds an update assignment |
| `delete` | table identifier, body block | Optional where clauses |
| `truncate` | table identifier | TRUNCATE TABLE; PostgreSQL only |

```art
statement: sql [insert.columns: [id title] :books [
    row [1 "River Atlas"]
    row [2 "Quiet Maps"]
]]

statement: sql [update :books [
    assign 'title "New title"
    where [id = 1]
]]

statement: sql [update.values: [title: "New title" subtitle: null] :books [
    where [id = 1]
]]

statement: sql [delete :books [where [id = 2]]]
```

Assignments and rows accept scalar values, including null. Labels in `.values:`
name SQL columns.

> [!WARNING]
> An UPDATE or DELETE without `where` affects **every row** in the table.

## Views and triggers

**Views:** `create.view name [query body]` creates a view; `drop.view name`
drops it. The body uses SELECT commands.

**Triggers:** `create.trigger` takes a name and a block of `insert`, `update`,
or `delete` calls. Supply all three options:

| Option | Choose |
| --- | --- |
| Table | `.on:` followed by the table identifier |
| Timing | Exactly one of `.before` or `.after` |
| Event | Exactly one of `.insert`, `.update`, or `.delete` |

Inside the body, use `new` references for INSERT, `old` for DELETE, and either
for UPDATE. PostgreSQL trigger names must be unqualified: use `:loanAdded`,
not a schema path.

```art
statement: sql [create.view :recentBooks [
    from :books
    select 'title
    where [publishedYear >= 2020]
]]

statement: sql [create.trigger.after.insert.on: :loans :loanAdded [
    update :books [
        assign 'available false
        where [id = new\bookId]
    ]
]]
```

> [!NOTE]
> Stored definitions cannot use bind parameters. CHECK constraints, views, and
> triggers contain escaped SQL literals; pagination counts are rendered inline
> as nonnegative integers. Ordinary queries and writes remain parameterized.

## Compiled output

| Conversion | Fields | Parameters |
| --- | --- | --- |
| `to :sqliteQuery statement` | `text`, `params` | Positional `?`; booleans become integers |
| `to :postgresQuery statement` | `text`, `params`, `statements` | Numbered `$1`, `$2`, …; native scalar values |

`text` is the SQL string and `params` contains values in SQL order, including
values from CTEs, projections, joins and nested queries. SQLite adds scalar
casts and null adapters where needed for Arturo's native parameter binding.
Both conversions preserve the input statement.

### PostgreSQL triggers

For ordinary statements, `statements` contains one SQL string. For triggers,
execute both entries in order through your driver:

1. CREATE FUNCTION
2. CREATE TRIGGER

The function has a deterministic name beginning with `sql_trigger_`. Creation
never replaces an existing function.

> [!IMPORTANT]
> You manage transactions and generated function cleanup. Dropping a trigger
> or its table does not remove the helper function.

### Dialect support

| Feature | SQLite | PostgreSQL |
| --- | --- | --- |
| `fetch` | LIMIT/OFFSET | OFFSET/FETCH |
| `group.rollup`, `.cube`, `.sets` | Compilation error | Supported |
| `all`, `any` comparisons | Compilation error | Supported |
| `.identity` | Compilation error | GENERATED ALWAYS AS IDENTITY |
| `truncate` | Compilation error | TRUNCATE TABLE |

> [!IMPORTANT]
> PostgreSQL support is compilation-only. SQL generation and parameter order
> are tested, but server execution and driver integration are not. Use an
> external driver to execute the output.

Unsupported SQLite features fail with a dialect-specific error rather than
being replaced with a different operation. MySQL compilation is not implemented.

## Execution and formatting

| Call | Accepted statement | Result |
| --- | --- | --- |
| `sql.query: db statement` | DSL block, statement dictionary or `:sqliteQuery` | Native SQLite rows |
| `sqliteExecute db statement` | Statement dictionary or `:sqliteQuery` | Native SQLite rows; compatibility wrapper |
| `sqliteTable db statement` | Statement dictionary or `:sqliteQuery` | Formatted string; optional `.header:` block |

`db` must be an open native `:database` connection.

- You own the connection and must close it, including after a failure.
- Commands that produce no rows return `[]`. Database errors propagate.
- Execution helpers reject raw SQL strings and `:postgresQuery` objects.
- Plain `sql` without `.query:` accepts only a DSL block.

This example closes the connection before rethrowing any error:

```art
db: open.sqlite ":memory:"
failure: try [
    ignored: sql.query: db [create :books [column 'title :string]]
    ignored: sql.query: db [insert.columns: 'title :books -> row ["River Atlas"]]
    rows: sql.query: db [from :books select 'title]
    print tabular.header: ["Title"] rows
]
close db
unless null? failure -> throw to :string failure
```

### Format results

`sqliteTable` returns `"No rows."` for an empty result. For nonempty results,
header counts must match the result width.

To format rows separately, use the imported `tabular` function:

```art
rows: []
text: (empty? rows) ? ["No rows."] [tabular.header: ["Title"] rows]
```

> [!TIP]
> `tabular` requires at least one row. Check for empty results before calling it,
> as shown above.

Compiled SQLite output also works with Arturo's native call:
`query.with: compiled\params db compiled\text`.

## Compatibility syntax

`orderBy [name asc id desc]`, infix `and`/`or` predicates and
`select.expressions` remain available for existing callers. Infix predicates
bind AND before OR. New code can use `order`, prefix boolean calls and composed
projection helpers as shown above.
