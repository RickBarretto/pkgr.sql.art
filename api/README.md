# SQL feature catalog

Find examples by SQL feature below. The catalog follows the
[SQLTutorial learning sequence](https://www.sqltutorial.org/) and uses a book
database throughout.

For command arguments, see the [API reference](API.md). For layout and naming,
see the [style guide](STYLE.md).

## How to read an example

Each `.art` file contains:

1. **Arturo examples** above `---`, showing alternative ways to build a statement.
2. **Reference SQL** below `---`, showing the intended SQL operation.

`---` begins an Arturo end-of-file string. The alternatives show different
argument forms or helper compositions for the same operation.

> [!NOTE]
> Reference SQL shows values inline for readability. Compiled queries normally
> use bind parameters and quoted identifiers. See
> [compiled output](API.md#compiled-output) for dialect support and exceptions.

Start with [select](select/select.art) and [ordering](sort/order-by.art), or
choose a feature:

## Features

| Topic | Examples |
| --- | --- |
| Querying data | [select](select/select.art) |
| Sorting rows | [order-by](sort/order-by.art) |
| Limiting rows | [distinct](limit/distinct.art), [limit](limit/limit.art), [fetch](limit/fetch.art) |
| Filtering rows | [where](filter/where.art), [and](filter/and.art), [or](filter/or.art), [between](filter/between.art), [in](filter/in.art), [like](filter/like.art), [is-null](filter/is-null.art), [not](filter/not.art) |
| Joining tables | [inner-join](join/inner-join.art), [left-join](join/left-join.art), [right-join](join/right-join.art), [full-outer-join](join/full-outer-join.art), [cross-join](join/cross-join.art), [self-join](join/self-join.art) |
| Grouping rows | [group-by](group/group-by.art), [having](group/having.art), [grouping-sets](group/grouping-sets.art), [rollup](group/rollup.art), [cube](group/cube.art) |
| Set operators | [union](set/union.art), [intersect](set/intersect.art), [minus](set/minus.art) |
| Working with tables | [create-table](tables/create-table.art), [primary-key](tables/primary-key.art), [not-null](tables/not-null.art), [drop-table](tables/drop-table.art), [add-column](tables/add-column.art), [drop-column](tables/drop-column.art), [foreign-key](tables/foreign-key.art), [unique](tables/unique.art), [check](tables/check.art), [alter-table](tables/alter-table.art), [identity-column](tables/identity-column.art) |
| Modifying data | [insert](change/insert.art), [update](change/update.art), [delete](change/delete.art), [truncate-table](change/truncate-table.art) |
| Views | [views](views/views.art) |
| Triggers | [triggers](trigger/triggers.art) |
| Conditional expressions | [case](conditions/case.art), [coalesce](conditions/coalesce.art), [nullif](conditions/nullif.art) |
| Aggregate functions | [aggregate-functions](aggregate/aggregate-functions.art), [avg](aggregate/avg.art), [count](aggregate/count.art), [sum](aggregate/sum.art), [max](aggregate/max.art), [min](aggregate/min.art) |
| Subqueries | [subquery](subquery/subquery.art), [correlated-subquery](subquery/correlated-subquery.art), [exists](subquery/exists.art), [all](subquery/all.art), [any](subquery/any.art) |
| Common table expressions | [with](subquery/with.art) |
