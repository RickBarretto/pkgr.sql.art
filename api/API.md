# Function contracts

See [writing practices](STYLE.md) for preferred spellings and layout.

Based on [Arturo’s syntax and evaluation rules](https://arturo-lang.io/documentation/language/):
functions consume a fixed number of positional arguments; attributes add flags
or named values. Whitespace and line breaks do not determine call boundaries.
These contracts describe the captured-body interpreter. SQLite conversion rejects unsupported dialect features.

`sql [...]` is the public entry point and the scope for every DSL function.
`create`, `select`, expression helpers, and all other DSL functions exist only
inside that scope or its nested bodies. They do not become global Arturo
functions. Fragments in contract tables are calls within this scope.

## Identifiers and values

`Identifier` below means the union `:type :path :pathliteral :literal :string`.
An interpreter for a DSL body may additionally pass `:word` tokens to an
identifier argument. This is one contract shared by table, view, trigger, column,
alias, constraint-column, and reference identifiers. It is not restricted to
`:type` even though types are preferred for table names.

| Form | Table example | Column example |
| --- | --- | --- |
| Type | `from :books` | `select :title` |
| Literal | `from 'books` | `select 'title` |
| String | `from "books"` | `select "title"` |
| Path | `from main\books` | `select b\title` |
| Literal path | `from 'main\books` | `select 'b\title` |
| Captured word | `sql [from books select title]` | `select [title publishedYear]` |

Types contribute their names; they are not instantiated. `sql` captures its
body, so identifier tokens such as `:books`, `main\books`, or a bare `books`
are interpreted as SQL identifiers in identifier positions. They are not looked
up or executed in the caller’s scope. This does not change how native Arturo
would evaluate the same tokens outside `sql [...]`.

`Identifiers` means one Identifier or a block of identifiers. A single wildcard
is `"*"` in an identifier argument; inside an expression block it is `*`.
A string in an identifier argument names an identifier; a string inside a
predicate, scalar expression, assignment value, or row is a bound value.

`Scalar` means a string, integer, floating-point number, boolean, or null.
Null binding is distinct from null comparison: use `is null`/`is not null`.
The SQLite compiler preserves numeric and null semantics even when the host
runtime binds values as text. Its conversion helpers are scoped to rendering;
they do not replace native Arturo functions.
`Expression` means a SQL expression value returned by a scoped helper function. `Predicate` means a
block representing one SQL condition. These blocks are interpreted as SQL data,
not passed to Arturo `do`. Paths inside them identify SQL columns.
Parenthesized Arturo computations must be captured once when constructing the
query, in the caller’s scope; compiling it later must not evaluate them again.

## Construction and body evaluation

| Function | Positional arguments | Result / purpose |
| --- | --- | --- |
| `sql` | `body :block` | Establish DSL scope and return the constructed query or statement |
| `create` | `tableName Identifier`, `body :block` | Build a table definition |
| `create.view` | `viewName Identifier`, `body :block` | Build a view from a query body |
| `create.trigger` | `triggerName Identifier`, `body :block` | Build a trigger from statement calls |
| `alter` | `tableName Identifier`, `body :block` | Build a schema change |
| `drop` | `tableName Identifier` | Drop a table; `.view` selects a view |
| `truncate` | `tableName Identifier` | Remove all rows using dialect TRUNCATE |
| `insert` | `tableName Identifier`, `body :block` | Build an insert |
| `update` | `tableName Identifier`, `body :block` | Build an update |
| `delete` | `tableName Identifier`, `body :block` | Build a delete |
| `combine` | `queries :block` | Combine query calls; `.union`, `.intersect`, or `.except` required |

For example, the `create` signature in Arturo parameter notation is:

```art
[tableName :type :path :pathliteral :literal :string :word body :block]
```

The `:word` case applies to tokens passed by the captured-body interpreter;
it does not suppress native Arturo argument evaluation by itself.

A single function call body can use Arturo’s terminal-expression shorthand:
`sql [alter :books -> add.optional 'subtitle :string]`. Here `add` has exactly two arguments,
so `->` wraps that one call. Keep explicit blocks for several commands; do not
use an arrow to mean “read until the next SQL clause.”

Bodies establish a local builder context. Each command resolves to a function
with these contracts and mutates only its owning builder. The body interpreter
captures identifier arguments and passes their tokens without resolving host
variables. It uses the function’s arity, not the next SQL keyword, to find call
boundaries. Nested bodies have separate contexts and are validated for their
owner: a table body accepts columns and constraints, not query commands.

Body commands leave no incidental stack values; the enclosing constructor
returns one statement/query. `combine` evaluates its block of query calls and
consumes those results. It requires at least two compatible projections. Each operand keeps its ordering,
pagination and CTE definitions in its own SQL scope. Builders
create data only: execution and connection management are separate operations.
Overlapping built-in names are resolved locally, without rebinding global Arturo
functions such as `select`, `query`, `remove`, or `when`.

Attributes do not change positional arity. For example, `insert.columns:` still
takes the table name and body; `create.view` still takes the name and body.
Only one create variant is allowed per call. Trigger `.on:` names the table;
`.before`/`.after` and `.insert`/`.update`/`.delete` select timing and event.
Trigger writes may refer to `new` for INSERT, `old` for DELETE, and both for
UPDATE; these names are rejected outside their owning trigger scope.

## Query commands

| Function | Positional arguments | Options and behavior |
| --- | --- | --- |
| `from` | `source Identifier` | `.as: Identifier` sets an alias; exactly one source |
| `select` | `projection Identifier / Expression / :block` | Append a projection or identifier list; `.as:` takes matching aliases; `.distinct` applies to the whole result |
| `select.count`, `.sum`, `.avg`, `.min`, `.max` | `operand Identifier` | Append one aggregate; only count accepts `*` |
| `select.coalesce`, `.nullif` | `operands :block` | Coalesce accepts at least two operands; nullif exactly two |
| `where` | `predicate :block` | Repeated calls combine with AND |
| `join` | `table Identifier`, `predicate :block` | Default inner; `.left`, `.right`, `.full`; `.as:` alias |
| `cross` | `table Identifier` | Cross join; `.as:` alias; no artificial empty predicate |
| `order` | `keys Identifiers` | Default ascending; `.asc` or `.desc`; repeated calls append sort keys |
| `group` | `keys Identifiers` | `.rollup`/`.cube` take keys; `.sets` takes a block of grouping blocks |
| `having` | `predicate :block` | Filter groups; repeated calls combine with AND |
| `limit`, `fetch` | `count :integer` | Optional `.skip: :integer`; require stable ordering for pagination examples |
| `offset` | `count :integer` | Separate alternative to `.skip:`; do not combine both |
| `with` | `name Identifier`, `body :block` | Register a CTE query before the main query |

Each spelling is a variant of its base function, with one consistent argument
count. Attribute combinations with conflicting projection/grouping modes are
errors. A single alias is unwrapped; multiple aliases use a block. Pagination
counts are nonnegative; FETCH and LIMIT are alternative dialect strategies.

Expression helpers are ordinary scoped calls whose results can be passed to
`select`. No projection mode needs to be declared:

```art
sql [
    from :books
    select avg 'pageCount
    select coalesce [subtitle title]
]
```

| Helper | Positional arguments | Result |
| --- | --- | --- |
| `count`, `sum`, `avg`, `min`, `max` | `operand Identifier` | One aggregate expression; only count accepts `"*"` |
| `coalesce` | `operands :block` | One expression; at least two operands |
| `nullif` | `left Identifier / Scalar`, `right Identifier / Scalar` | One nullif expression |
| `choose` | `branches :block` | One conditional expression; optional `.default:` |

`select` always consumes one argument. In `select avg 'pageCount`, that argument
is the result of `avg`, which also consumes exactly one argument. Repeated
`select` calls append projections. A list such as `[title publishedYear]` remains
a captured identifier list; it does not execute expression helpers. Use composed
calls for calculated projections and `.as:` on `select` for their aliases.
Attributes belong to the function they decorate, including when its argument is
another call. Symbolic arithmetic follows Arturo’s evaluation rules; explicit
grouping is required where it changes the expression. Predicate blocks interpret
nested expression blocks as grouping, not as host Arturo computations.

Predicate blocks use Arturo function-call syntax. Comparisons may use their
native infix symbols; named boolean functions are prefix calls: `and` and `or`
consume two predicate expressions, and `not` consumes one. There is no SQL-style
AND/OR precedence in the DSL. Arity and explicit grouping determine the tree;
only generated SQL uses infix AND/OR. Scalar helpers work on either side of
comparisons. Nested scalar-expression blocks must contain one complete expression.
Arithmetic uses `+`, `-`, `*`, and `/` as prefix or infix calls, groups from the
right, and preserves explicit grouping blocks.

```art
sql [
    from :books
    where [and
        publishedYear >= 2020
        available = true
    ]
]

sql [
    from :books
    where [or
        genre = "Poetry"
        genre = "History"
    ]
]
```

An arrow can wrap one complete prefix call, as in `where -> and ... ...`;
it does not turn following lines into separate clauses. Repeated `where` calls
remain an alternative for conjunction. The comparison symbol `=<` renders SQL
`<=`. The predicate spellings `between`, `in`, `like`, and null tests follow the same captured-call rule. SQL rendering
must preserve the explicitly constructed predicate tree.

`query body :block`, available only within `sql` and its nested bodies, constructs one nested SQL expression query. `exists`, `all`,
and `any` each consume that query. A subquery must have a single output column
for scalar and quantified comparisons. Correlated references name a declared
outer alias. Qualified references are validated after construction against local
relations and explicit outer aliases. A local alias hides the original table name;
inner aliases do not leak to their parent query. CTE definitions have independent
relation scopes. A nested query block stays nested because its scope matters.

## Schema and write commands

| Function | Positional arguments | Options and behavior |
| --- | --- | --- |
| `column` | `name Identifier`, `storageType :type` | NOT NULL by default; `.optional` permits NULL; `.primary`, `.unique`, `.identity` flags |
| `reference` | `columns Identifiers`, `target Identifier`, `targetColumns Identifiers` | Matching column counts; explicit table reference |
| `check` | `predicate :block` | Table check constraint |
| `add` | `name Identifier`, `storageType :type` | Column addition inside alter; same constraint flags as column |
| `remove` | `name Identifier` | Column removal inside alter |
| `rename` | `newName Identifier` | Rename the owning table |
| `columns` | `names Identifiers` | Insert columns; `.columns:` on insert is the alternative |
| `row` | `values :block` | Append one row; count must match columns |
| `assign` | `column Identifier`, `value Scalar` | Set one field inside update |
| `when` | `predicate :block`, `value Scalar` | Append one choose branch |
| `otherwise` | `value Scalar` | Fallback branch; `.default:` on choose is the alternative |

Columns are required by default: `column 'title :string` emits `TEXT NOT NULL`.
Use `column.optional 'subtitle :string` for a nullable field. The same default
and `.optional` flag apply to `add`. There is no `.required` flag. A primary-key
column cannot be `.optional`; reject that combination rather than silently
ignoring it. Optional columns omit NOT NULL in the generated SQL.

`:integer` maps to SQL INTEGER; `:string` to SQL TEXT. The table name `:books`
is an identifier, while the second argument of `column 'title :string` describes
storage. Additional type mappings and identity behavior depend on the dialect.
INSERT requires column order to be explicit. `update.values:` accepts a captured
label/value block for bulk assignment, with its two positional arguments intact.
Labels in that option are SQL column names, not assignments into the caller’s
scope. `choose` requires at least one when branch and has a single result type
compatible with its branches. `coalesce [subtitle title]` preserves SQL null
semantics; it is not Arturo `??`, which also substitutes for false.
