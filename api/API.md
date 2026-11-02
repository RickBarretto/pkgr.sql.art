# SQL API reference

Build SQL statements with Arturo blocks, compile them for SQLite or PostgreSQL,
and execute SQLite statements with an open Arturo database connection.

Requires Arturo 0.10.0 or newer.

```art
import {sql}!

minimumYear: 2020
statement: sql [
    from :books
    select [title publishedYear]
    where [publishedYear >= (minimumYear)]
    order.desc 'publishedYear
    limit 10
]
compiled: to :sqliteQuery statement
print compiled\text
inspect compiled\params
```

`sql [...]` returns a statement dictionary. Conversion returns SQL text and
parameters without executing SQL or changing that dictionary. Use
`to :postgresQuery statement` to compile the same statement for PostgreSQL.

See the [writing guide](STYLE.md) for layout and naming suggestions and the
[feature catalog](README.md) for more examples.

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

An identifier list accepts either one identifier or a block of identifiers.
Strings name identifiers in identifier positions, but represent values in
predicates, expressions, assignments and rows. For example, `select "title"`
selects a column, while `where [title = "River Atlas"]` compares it with a value.

Scalar values are strings, integers, floating-point numbers, booleans or null.
Ordinary values become bind parameters. Parentheses evaluate Arturo code once
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
Arturo code. DSL commands such as `select`, `query` and `when` are available
inside SQL bodies; importing the package leaves Arturo's built-ins intact.

## Query commands

Each query requires one `from` and at least one projection. Clauses may appear
in any order; compilation puts them in SQL order. Each command consumes its
arguments regardless of line breaks.

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

Use a single alias for one projection and a block of aliases for several.
Alias counts must match projection counts; wildcards cannot be aliased.
Conflicting modes, such as `order.asc.desc`, produce an error. A query accepts
one grouping clause and one pagination count. `group.sets` takes a nonempty
block of grouping blocks; an individual grouping block may be empty.

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
Both `<=` and `=<` compile to SQL `<=`. Compare null with `is null` or
`is not null`; direct comparisons with null are rejected. IN needs a nonempty
value list; BETWEEN needs exactly two endpoints.

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

## Subqueries, CTEs and set operations

`query [body]` builds a nested SELECT. Scalar subqueries and comparisons using
`all query [...]` or `any query [...]` require one projection. `exists query
[...]` tests whether a nested query returns rows. Correlations use explicit
outer aliases; inner aliases stay inside their query. CTE definitions have
independent relation scopes.

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

`.optional` permits null and omits NOT NULL. It cannot combine with `.primary`.
There is no `.required` flag. Identity requires an integer, non-optional column
and does not add a primary key automatically.

| Arturo storage type | SQLite | PostgreSQL |
| --- | --- | --- |
| `:integer` | INTEGER | INTEGER |
| `:string` | TEXT | TEXT |
| `:logical` | INTEGER | BOOLEAN |
| `:floating` | REAL | DOUBLE PRECISION |
| `:binary` | BLOB | BYTEA |

Other storage types produce a compilation error. SQLite accepts one alteration
per statement; its restrictions on adding primary or unique columns still apply.
DROP COLUMN and RIGHT/FULL JOIN require a supporting SQLite runtime version.

## Inserts, updates and deletes

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

Assignments and rows accept scalar values, including null. `.values:` labels
name SQL columns. Updates and deletes without `where` affect every row.

## Views and triggers

`create.view name [query body]` creates a view; `drop.view name` drops it.
The query body uses the same commands as a SELECT.

`create.trigger` takes a trigger name and a block of `insert`, `update` or
`delete` calls. It requires `.on:` with the table, exactly one timing flag
(`.before` or `.after`), and exactly one event flag (`.insert`, `.update` or
`.delete`). Use `new` references for INSERT, `old` for DELETE, and either for
UPDATE.

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

CHECK constraints, views and triggers contain escaped SQL literals rather than
bind parameters. Pagination counts in stored queries are also rendered inline.

## Compiled output

| Conversion | Fields | Parameters |
| --- | --- | --- |
| `to :sqliteQuery statement` | `text`, `params` | Positional `?`; booleans become integers |
| `to :postgresQuery statement` | `text`, `params`, `statements` | Numbered `$1`, `$2`, …; native scalar values |

`text` is the SQL string and `params` contains values in SQL order, including
values from CTEs, projections, joins and nested queries. SQLite adds scalar
casts and null adapters where needed for Arturo's native parameter binding.
Both conversions preserve the input statement.

PostgreSQL `statements` contains one SQL string for an ordinary statement. A
trigger produces two entries: CREATE FUNCTION followed by CREATE TRIGGER.
Execute those entries in order through your PostgreSQL driver. The generated
function has a deterministic name beginning with `sql_trigger_`; creation never
replaces an existing function. You manage transactions and function cleanup;
dropping a trigger or its table does not remove the helper function.

| Feature | SQLite | PostgreSQL |
| --- | --- | --- |
| `fetch` | LIMIT/OFFSET | OFFSET/FETCH |
| `group.rollup`, `.cube`, `.sets` | Compilation error | Supported |
| `all`, `any` comparisons | Compilation error | Supported |
| `.identity` | Compilation error | GENERATED ALWAYS AS IDENTITY |
| `truncate` | Compilation error | TRUNCATE TABLE |

PostgreSQL support generates SQL for an external driver. It has compiler tests,
but no server execution tests or built-in execution adapter. MySQL compilation
is not implemented.

## Execution and formatting

| Call | Accepted statement | Result |
| --- | --- | --- |
| `sql.query: db statement` | DSL block, statement dictionary or `:sqliteQuery` | Native SQLite rows |
| `sqliteExecute db statement` | Statement dictionary or `:sqliteQuery` | Native SQLite rows; compatibility wrapper |
| `sqliteTable db statement` | Statement dictionary or `:sqliteQuery` | Formatted string; optional `.header:` block |

`db` is an open native `:database` connection. You own and close it. Commands
without rows return `[]`; database errors propagate. These helpers reject raw
SQL strings and `:postgresQuery` objects. Plain `sql` without `.query:` accepts
only a DSL block.

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

`sqliteTable` returns `"No rows."` for an empty result. For nonempty results,
header counts must match the result width. The imported `tabular` function also
formats rows returned by `sql.query:`; guard empty results before calling it:

```art
rows: []
text: (empty? rows) ? ["No rows."] [tabular.header: ["Title"] rows]
```

## Compatibility syntax

`orderBy [name asc id desc]`, infix `and`/`or` predicates and
`select.expressions` remain available for existing callers. Infix predicates
bind AND before OR. New code can use `order`, prefix boolean calls and composed
projection helpers as shown above.
