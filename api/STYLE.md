# Writing readable SQL blocks

Write queries so readers can find the source, selected columns, and filters at
a glance. This guide recommends a consistent style. For accepted inputs and
validation rules, see the [API reference](API.md).

## Put one command on each line

Use four spaces for indentation. Keep related clauses together in this order:

1. Source and joins
2. Selected columns
3. Filters
4. Grouping and group filters
5. Sorting
6. Pagination

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

The compiler accepts clauses in any order; a consistent layout helps readers.

## Choose names readers can follow

Use descriptive lowerCamelCase names. Keep aliases short and recognizable,
such as `b` for books and `p` for publishers. Once a table has an alias, use it
for qualified columns.

| Use | Preferred form |
| --- | --- |
| Table | `:books` |
| Column | `'title` |
| Qualified column | `'b\title` |
| Alias | `'b` |
| Column list | `[title publishedYear]` |

Use an explicit literal for names that match a helper: `select 'count`.
The [identifier reference](API.md#identifiers-and-values) lists other accepted forms.

## Make application values visible

Use `@name` for an Arturo variable. Use parentheses when you need an Arturo
computation. Both capture the result when the statement is built.

```art
minimumYear: 2020
statement: sql [
    from :books
    select [title publishedYear]
    where [publishedYear >= @minimumYear]
]
```

## Match brackets to their purpose

| Purpose | Example |
| --- | --- |
| One identifier | `select 'title` |
| A list | `select [title publishedYear]` |
| Row data | `row ["River Atlas"]` |
| One-expression body | `alter :books -> add.optional 'subtitle :string` |
| Several commands or nested grouping | `[...]` |

Use `->` only when the body is one complete expression:

```art
statement: sql [
    from :books
    select 'title
    where -> publishedYear >= 2020
]
```

> [!IMPORTANT]
> Line breaks do not end calls or extend an arrow's body. Each command still
> needs all its arguments.

## Keep filters easy to follow

Use separate `where` calls for conditions that must all hold. For alternatives,
use prefix `or`. Add blocks around nested conditions so the grouping is visible.

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

Keep both operands visible when nesting `and` or `or`. Use `is null` and
`is not null` for null tests. See [predicates](API.md#predicates) for the full syntax.

## Give calculated columns useful aliases

Use separate `select` calls to mix ordinary columns with calculations:

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

Both `select.avg 'pageCount` and `select avg 'pageCount` work. Choose a consistent
form within a query.

## Show the shape of your data

Mark nullable columns with `.optional`. Name insert columns explicitly so readers
can match each row's values to its columns.

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

For updates and deletes, keep filters close to the target table and assignments.
Use an unfiltered write only when you intend to change the whole table; see
[write scope](API.md#inserts-updates-and-deletes).

## Order pages consistently

When paginating, include a unique key in the sort order to break ties:

```art
statement: sql [
    from :books
    select [id title]
    order 'title
    order 'id
    limit.skip: 20 10
]
```

Here, `id` gives books with the same title a consistent order.

## Name statements you will reuse

Give a statement a name when you want to inspect it, compile it for another
dialect, or pass it to an execution helper. Keep result formatting separate
when it makes the data flow easier to follow.

For connection cleanup and table formatting, use the patterns in
[execution and formatting](API.md#execution-and-formatting).
