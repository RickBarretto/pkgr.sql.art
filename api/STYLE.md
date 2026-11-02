# Writing readable SQL blocks

These suggestions help keep queries easy to scan as they grow. The
[API reference](API.md) documents accepted inputs and dialect support.

## Use consistent names and layout

Use four spaces for indentation and one command per line. 
A useful query order is: 
1. source and joins, 
2. projections, 
3. filters, 
4. grouping, 
4. sorting, 
5. then pagination. 

The compiler accepts clauses in any order:

```art
statement: sql [
    from.as: 'b :books
    join.left.as: 'p :publishers [b\publisherId = p\id]
    select [b\title p\name]
    where [b\available = true]
    order 'b\title
    limit 20
]
```

Choose descriptive lowerCamelCase names and short aliases that are easy to
recognize. Once a table has an alias, use that alias for qualified columns.

Use an explicit literal for a column whose name matches a helper, such as
`select 'count`.

Here is the preferred form of usage for each argument:

| Use | Preferred form | Other accepted forms |
| --- | --- | --- |
| Table | `:books` | `'books`, `"books"`, `main\books`, `'main\books`, captured `books` |
| Column | `'title` | `:title`, `"title"`, captured `title` |
| Qualified column | `'b\title` | captured `b\title` |
| Alias | `'b` | `"b"`, captured `b` |


## Make application values visible

Use `@name` for Arturo variables and parentheses for computations. This distinguishes
application values from SQL column names and captures the value when the
statement is built.

```art
minimumYear: 2020
statement: sql [
    from :books
    select [title publishedYear]
    where [publishedYear >= @minimumYear]
]
```

Use paths such as `b\title` for qualified columns. Strings in predicates and
rows are values; strings in identifier positions name columns or tables.

## Match brackets to their purpose

Pass individual identifiers directly: `select 'title`, `order 'title`,
`group 'genre`. Use blocks for lists, such as `select [title publishedYear]`,
and for rows, such as `row ["River Atlas"]`.

A body containing one complete call or predicate can use `->`. Keep explicit
blocks for several commands or nested grouping.

```art
statement: sql [alter :books -> add.optional 'subtitle :string]

statement: sql [
    from :books
    select 'title
    where -> publishedYear >= 2020
]
```

An arrow wraps one expression. Line breaks do not supply missing arguments or
extend a call's body.

## Keep filters easy to follow

Use repeated `where` calls for independent conditions that must all hold. Use
prefix `or` or `and` when the grouping matters, with blocks around nested
conditions. Comparisons use infix operators; `=<` and `<=` are both supported.

```art
statement: sql [
    from :books
    select 'title
    where [available = true]
    where [or
        genre = "Poetry"
        genre = "History"
    ]
    where [publishedYear >= 2020]
]
```

Each prefix `and` or `or` takes two predicates; `not` takes one. Keep each
operand visible when nesting them. Use `is null` and `is not null` for null
tests.

## Compose calculated columns directly

Give calculated projections useful aliases. Both `select.avg 'pageCount` and
`select avg 'pageCount` work; use a consistent form within a query.

```art
statement: sql [
    from :books
    select 'genre
    select.as: 'total count "*"
    select.as: 'averagePages avg 'pageCount
    group 'genre
    order 'genre
]
```

Use repeated `select` calls to mix identifier lists and calculated projections.
Repeated `order` calls also make mixed sort directions easy to read.

## Make nullability and write scope explicit

Columns are NOT NULL by default. Use `.optional` when a missing value is
meaningful. Choose insert columns explicitly so each row's value order is clear.

```art
statement: sql [create :books [
    column.primary 'id :integer
    column 'title :string
    column.optional 'subtitle :string
]]

statement: sql [insert.columns: [id title subtitle] :books [
    row [1 "River Atlas" null]
]]
```

Keep update and delete filters next to their assignments or target table.
Omitting `where` affects every row.

## Order pages consistently

Specify an order when paginating. Include a unique key to make the order
stable when other sort values tie.

```art
statement: sql [
    from :books
    select [id title]
    order 'title
    order 'id
    limit.skip: 20 10
]
```

## Keep execution and presentation clear

Name a statement when you want to inspect it, compile it for another dialect,
or pass it to an execution helper. Use `sql.query:` with an open SQLite
connection to get rows, and format those rows separately when needed. Close
connections after use, including when execution fails; the
[execution example](API.md#execution-and-formatting) shows the cleanup pattern.

For PostgreSQL, compile with `to :postgresQuery` and pass its SQL and parameters
to your driver. The [compiled-output reference](API.md#compiled-output) explains
multi-statement trigger output and dialect differences.
