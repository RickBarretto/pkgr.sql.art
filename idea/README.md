# SQL function API ideas

This catalog explores an Arturo API for the features in the
[SQLTutorial learning sequence](https://www.sqltutorial.org/). Examples use an
original book catalog. Only `idea/` is changed; these are proposals for a future
API, not examples supported by the current library.

Start with [the writing guide](STYLE.md) and [the function contracts](API.md),
then `select/select.art`, `sort/order-by.art`,
and the feature list below. Every feature has alternatives above `---`; the SQL
below it is the reference output. `---` is Arturo’s end-of-file string syntax.
SQL reference values are shown inline for readability; actual values should be
bound parameters. Identifiers should be quoted by the compiler.

## Reading the API

```art
sql [
    create :books [
        column.primary 'id :integer
        column 'title :string
    ]
]

sql [
    create.view :recentBooks [
        from :books
        select [id title]
        where [publishedYear >= 2020]
    ]
]
```

`sql [...]` provides the scope for every DSL function, including creation and
write commands. Only `sql` is a public entry point; helpers remain scoped.
Functions have fixed positional arguments. `create` and `create.view` both take
an identifier and a body block. A body is needed even for one command; use `->` when it contains one complete
expression and `[...]` when it contains several commands. Single identifiers need no block: `select 'title`,
`order 'title`, and `group 'genre`. Lists and grouped expressions keep theirs.

Columns default to NOT NULL. Use `column.optional` or `add.optional` for nullable
fields; `.required` is unnecessary.

Attributes refine a function, rather than defining a second spelling for it:
`create.view`, `join.left`, `select.count`, `order.desc`, and `group.rollup`.
There are no dummy positional arguments or implicit “until the next clause”
bodies. Repeated `select` calls append projections; repeated `where` calls
combine conditions with AND. Named boolean functions use prefix calls:
`and predicate1 predicate2`, `or predicate1 predicate2`, and `not predicate`.
Query clauses can be expressed in a readable order;
the compiler arranges the resulting SQL.

Calculated projections compose functions naturally: `select avg 'pageCount` or
`select coalesce [subtitle title]`. `select` consumes their result as its one
argument, without an expression-mode attribute.

The preferred table identifier is `:books`. Identifiers also accept `:path`,
`:pathliteral` (Arturo’s spelling of literalPath), `:literal`, and `:string`.
Words are accepted inside captured DSL bodies and identifier lists. They are
not assumed to be literal identifiers during ordinary Arturo evaluation.
See [identifier handling](API.md#identifiers-and-values) for examples and the
difference between an identifier string and a bound string value.

Alternatives explore the same contracts: a scalar versus a one-item list,
a projection attribute versus a composed helper call, bulk assignments, or a different
identifier form. They do not add interchangeable names for every function.

## Validation and scope

The drafts can be read as Arturo values. This alone does not verify their future
behavior. The proposed API still needs implementation and semantic tests.
Dialect support must be decided for FETCH, RIGHT/FULL joins, identity columns,
triggers, TRUNCATE, grouping extensions, and quantified comparisons.

## Querying data

- [select](select/select.art).

## Sorting rows

- [order-by](sort/order-by.art).

## Limiting rows

- [distinct](limit/distinct.art).
- [limit](limit/limit.art).
- [fetch](limit/fetch.art).

## Filtering rows

- [where](filter/where.art).
- [and](filter/and.art).
- [or](filter/or.art).
- [between](filter/between.art).
- [in](filter/in.art).
- [like](filter/like.art).
- [is-null](filter/is-null.art).
- [not](filter/not.art).

## Joining tables

- [inner-join](join/inner-join.art).
- [left-join](join/left-join.art).
- [right-join](join/right-join.art).
- [full-outer-join](join/full-outer-join.art).
- [cross-join](join/cross-join.art).
- [self-join](join/self-join.art).

## Grouping rows

- [group-by](group/group-by.art).
- [having](group/having.art).
- [grouping-sets](group/grouping-sets.art).
- [rollup](group/rollup.art).
- [cube](group/cube.art).

## Set operators

- [union](set/union.art).
- [intersect](set/intersect.art).
- [minus](set/minus.art).

## Working with tables

- [create-table](tables/create-table.art).
- [primary-key](tables/primary-key.art).
- [not-null](tables/not-null.art).
- [drop-table](tables/drop-table.art).
- [add-column](tables/add-column.art).
- [drop-column](tables/drop-column.art).
- [foreign-key](tables/foreign-key.art).
- [unique](tables/unique.art).
- [check](tables/check.art).
- [alter-table](tables/alter-table.art).
- [identity-column](tables/identity-column.art).

## Modifying data

- [insert](change/insert.art).
- [update](change/update.art).
- [delete](change/delete.art).
- [truncate-table](change/truncate-table.art).

## Views

- [views](views/views.art).

## Triggers

- [triggers](trigger/triggers.art).

## Conditional expressions

- [case](conditions/case.art).
- [coalesce](conditions/coalesce.art).
- [nullif](conditions/nullif.art).

## Aggregate functions

- [aggregate-functions](aggregate/aggregate-functions.art).
- [avg](aggregate/avg.art).
- [count](aggregate/count.art).
- [sum](aggregate/sum.art).
- [max](aggregate/max.art).
- [min](aggregate/min.art).

## Subqueries

- [subquery](subquery/subquery.art).
- [correlated-subquery](subquery/correlated-subquery.art).
- [exists](subquery/exists.art).
- [all](subquery/all.art).
- [any](subquery/any.art).

## Common table expressions

CTEs are grouped under `subquery/`.

- [with](subquery/with.art).
