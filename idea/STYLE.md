# Writing SQL DSL code

These conventions describe the API proposed in `idea/`. Prefer readable Arturo
function calls over reproducing SQL clause syntax. The [function contracts](API.md)
define accepted arguments; the preferences here do not narrow those contracts.

## Keep every DSL call inside sql

Use `sql [...]` for queries, schema changes, and writes. Helpers belong to this
scope, including calls nested inside a table, view, or query body.

```art
sql [
    create :books [
        column.primary 'id :integer
        column 'title :string
    ]
]
```

Keep the outer `sql [...]` form consistent across examples. Use arrow shorthand
for suitable inner bodies.

## Prefer types for tables

Prefer `:books` for a table and `:recentBooks` for a view or named query. This is
a writing convention, not a requirement. Identifier arguments also accept
paths, literal paths, literals, and strings. Words are accepted in captured
identifier positions.

| Use | Preferred form | Other accepted forms |
| --- | --- | --- |
| Table | `:books` | `'books`, `"books"`, `main\books`, `'main\books`, captured `books` |
| Column | `'title` | `:title`, `"title"`, captured `title` |
| Qualified column | `'b\title` | captured `b\title` |
| Alias | `'b` | `"b"`, captured `b` |

Use explicit literals for keyword names. Prefer paths for qualification rather
than strings with embedded dots. Strings in value positions remain SQL values:
`select "title"` names a column, while `assign 'title "River Atlas"` assigns a
bound string value. The argument position determines the meaning.

## Make nullable fields explicit

Columns are required by default. Write `column 'title :string` for a NOT NULL
field. Add `.optional` only when NULL is meaningful, for example
`column.optional 'subtitle :string`. Column additions follow the same rule:
`add.optional 'subtitle :string`. Do not write a redundant `.required` flag.

## Pass single values directly

Write `select 'title`, `order 'title`, and `group 'genre`. Use a block when
passing several identifiers, such as `select [title publishedYear]`.

Do not add a list wrapper around one alias, one aggregate operand, or one
reference column. A function whose contract requires a block still needs that
block, even when it contains one item: `row ["River Atlas"]` is a row, not a
scalar argument. A grouping set such as `[genre]` also retains its boundary.

## Prefer arrows for one expression

When a body contains one complete function call or expression, prefer `->`:

```art
sql [
    alter :books -> add.optional 'subtitle :string
]

sql [
    from :books
    select 'title
    where -> publishedYear >= 2020
]
```

`->` supplies a block; it does not remove an argument from the function's
signature. It wraps one terminal expression, not every line that follows.
Use `[...]` for multiple commands, data lists, explicit grouping, and empty
blocks. Do not replace a list with an arrow just to remove brackets.

## Keep structure shallow

Use repeated commands when they express a flat sequence. Compose helpers
directly instead of wrapping their results in extra blocks.

```art
sql [
    from :books
    select 'genre
    select count "*"
    group 'genre
    order 'genre
]
```

Repeated `select` calls append projections. Repeated `order` calls append sort
keys. Repeated `where` calls combine conditions with AND. Use that last form for
independent filters, not to express an OR group.

Keep nesting that establishes ownership or meaning: table bodies, view bodies,
subqueries, rows, and grouped predicates. A CTE can make a deeply nested query
easier to read, but introduce one only when its name clarifies the query.

## Respect function arity and operator position

Each function consumes its declared arguments. Newlines and SQL clause names
do not terminate calls. Attributes refine the same function without changing
its positional argument count.

Use named boolean functions in prefix position. Comparisons may use Arturo's
infix symbols. Prefer `=<` for less-or-equal; the SQL output uses `<=`.

```art
sql [
    from :books
    select 'title
    where -> and
        publishedYear >= 2020
        available = true
]
```

`and` and `or` each take two predicate expressions; `not` takes one. Do not
apply SQL's AND/OR precedence to the DSL. Group compound predicates explicitly
and keep the tree visible when combining conjunction and disjunction.

## Compose projections naturally

Use `select avg 'pageCount` or the concise variant `select.avg 'pageCount`.
Use `select.as: 'averagePages avg 'pageCount` when an expression needs a name.
Choose one aggregate style within a related group of projections.

Use attributes for clear variations: `create.view`, `join.left`, `order.desc`,
and `group.rollup`. Give attribute labels their values directly, such as
`.as: 'b`. Avoid placeholder arguments and expression-mode flags.

## Format for reading

Use four spaces for indentation, one command per line, and spaces around infix
operators. Put a multiline block's closing bracket at its owner's indentation.
Keep a short arrow body on one line; indent the operands of a long prefix call.
Use descriptive lowerCamelCase names and short, meaningful aliases.

Read query bodies in a consistent order: source and joins, projections,
filters, grouping, sorting, then pagination. This is a writing preference; SQL
rendering follows the query structure rather than the order of text alone.

In idea files, separate alternatives with a blank line. Keep reference SQL
directly below `---`, without braces or comments. `---` starts a string through
the end of the file, so all DSL alternatives must appear above it.
