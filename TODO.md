# SQL API evolution

Reference: [API contracts](api/API.md), [writing guide](api/STYLE.md), and the linked feature examples below.

A checked feature has implementation and regression coverage. An unchecked feature
still needs the work described. Features marked **dialect pending** can be built
as query data, but conversion to SQLite rejects them explicitly; they are not
implemented for execution. This checklist does not promise another SQL dialect.

## Construction and scope

- [x] `sql body`: capture a block and return one query or statement without executing it.
- [x] Keep DSL commands local; preserve native Arturo functions.
- [x] Accept type, literal, string, word, path and literal-path identifiers.
- [x] Quote identifiers and bind ordinary scalar values, including booleans and null.
- [x] Capture parenthesized host computations once during construction.
- [x] Use fixed positional arity and validate flag/value attributes.
- [x] Support block bodies and single-command `->` bodies.
- [x] Keep nested builders independent and avoid incidental stack results.
- [x] Validate qualified column references against local relations and declared outer aliases, including trigger scopes.

## Selection and ordering

- [x] [`select projection`](api/select/select.art): scalar identifiers, identifier lists and appended projections; `.as:` aliases.
- [x] [`select.distinct`](api/limit/distinct.art): DISTINCT across the result.
- [x] [`order keys`](api/sort/order-by.art): scalar/list keys, `.asc`, `.desc`, and appended sort keys.
- [x] [`limit count`](api/limit/limit.art): nonnegative counts and `.skip:` pagination.
- [x] `offset count`: separate pagination offset; reject conflicts with `.skip:`.
- [ ] [`fetch count`](api/limit/fetch.art): `.skip:` is parsed and validated; **dialect pending** because SQLite lacks FETCH syntax.

## Filtering

- [x] [`where predicate`](api/filter/where.art): repeated filters combine with AND.
- [x] Comparisons: `=`, `<>`, `!=`, `<`, `<=`, `=<`, `>`, `>=`.
- [x] [`and left right`](api/filter/and.art): prefix conjunction with explicit grouping.
- [x] [`or left right`](api/filter/or.art): prefix disjunction with explicit grouping.
- [x] [`not predicate`](api/filter/not.art): predicate negation.
- [x] [`between`](api/filter/between.art): two bound endpoints.
- [x] [`in`](api/filter/in.art): nonempty bound value lists.
- [x] [`like`](api/filter/like.art): bound patterns.
- [x] [`is null` / `is not null`](api/filter/is-null.art): explicit null tests; reject direct null comparisons.
- [x] Compose scalar helpers and arithmetic on both sides of predicates; preserve grouping and parameter order.

## Joins and sources

- [x] `from source`: exactly one source with optional `.as:` alias.
- [x] [`join` / `join.inner`](api/join/inner-join.art): table and predicate with optional `.as:`.
- [x] [`join.left`](api/join/left-join.art): LEFT JOIN.
- [x] [`join.right`](api/join/right-join.art): RIGHT JOIN; execution requires a supporting SQLite version.
- [x] [`join.full`](api/join/full-outer-join.art): FULL JOIN; execution requires a supporting SQLite version.
- [x] [`cross table`](api/join/cross-join.art): CROSS JOIN without a predicate, with optional `.as:`.
- [x] [Self joins](api/join/self-join.art): qualified references and separate aliases.

## Grouping

- [x] [`group keys`](api/group/group-by.art): scalar or list grouping keys.
- [x] [`having predicate`](api/group/having.art): aggregate conditions; repeated calls combine with AND.
- [ ] [`group.sets`](api/group/grouping-sets.art): validate grouping blocks, including an empty grouping set; **dialect pending** for SQL rendering and execution.
- [ ] [`group.rollup`](api/group/rollup.art): parsed; **dialect pending** for SQL rendering and execution.
- [ ] [`group.cube`](api/group/cube.art): parsed; **dialect pending** for SQL rendering and execution.

## Aggregates and conditional expressions

- [x] [Aggregate function composition](api/aggregate/aggregate-functions.art): helper calls and projection attributes.
- [x] [`count operand` / `select.count`](api/aggregate/count.art): column or wildcard operand.
- [x] [`sum operand` / `select.sum`](api/aggregate/sum.art): column operand; reject wildcards.
- [x] [`avg operand` / `select.avg`](api/aggregate/avg.art): column operand; reject wildcards.
- [x] [`min operand` / `select.min`](api/aggregate/min.art): column operand; reject wildcards.
- [x] [`max operand` / `select.max`](api/aggregate/max.art): column operand; reject wildcards.
- [x] [`coalesce operands` / `select.coalesce`](api/conditions/coalesce.art): at least two operands, including null.
- [x] [`nullif left right` / `select.nullif`](api/conditions/nullif.art): exactly two operands, including null.
- [x] [`choose branches`](api/conditions/case.art): `when predicate value`, `otherwise value`, and `.default:`; validate branch order and compatible result types.
- [x] Support nested helper expressions and Arturo arithmetic consistently across scalar expression contexts.

## Subqueries, CTEs and sets

- [x] [`query body`](api/subquery/subquery.art): scalar subqueries require one projection.
- [x] [Correlated subqueries](api/subquery/correlated-subquery.art): compile and execute references to outer aliases.
- [x] Reject undeclared or out-of-scope correlated references during construction.
- [x] [`exists query`](api/subquery/exists.art): existence predicates allow multiple output columns.
- [ ] [`all query`](api/subquery/all.art): validate a single-column query operand; **dialect pending** for SQL rendering and execution.
- [ ] [`any query`](api/subquery/any.art): validate a single-column query operand; **dialect pending** for SQL rendering and execution.
- [x] [`with name body`](api/subquery/with.art): CTEs, duplicate-name rejection, nested query validation, and parameter ordering.
- [x] [`combine.union queries`](api/set/union.art): at least two queries with matching projection counts.
- [x] [`combine.intersect queries`](api/set/intersect.art): INTERSECT.
- [x] [`combine.except queries`](api/set/minus.art): EXCEPT.
- [x] Preserve each set operand's ordering, pagination and CTE scope during compilation.

## Tables and constraints

- [x] [`create table body`](api/tables/create-table.art): column definitions and SQLite storage mappings.
- [x] `column name storageType`: INTEGER, TEXT, REAL, BLOB and boolean storage mapping.
- [x] [`column.primary`](api/tables/primary-key.art): primary-key columns.
- [x] [Required/optional columns](api/tables/not-null.art): NOT NULL by default; `.optional` permits null; reject optional primary keys.
- [x] [`column.unique`](api/tables/unique.art): unique columns.
- [x] [`reference columns target targetColumns`](api/tables/foreign-key.art): explicit foreign keys with matching column counts.
- [x] [`check predicate`](api/tables/check.art): table checks with escaped schema literals.
- [ ] [`column.identity`](api/tables/identity-column.art): parsed; **dialect pending** because SQLite lacks GENERATED AS IDENTITY syntax.
- [x] [`alter table body` / `rename newName`](api/tables/alter-table.art): rename tables; one SQLite alteration per statement.
- [x] [`add name storageType`](api/tables/add-column.art): `.optional`, `.primary`, `.unique` and `.identity` use column contracts; SQLite restrictions still apply.
- [x] [`remove name`](api/tables/drop-column.art): DROP COLUMN; requires a supporting SQLite version.
- [x] [`drop table`](api/tables/drop-table.art): DROP TABLE.

## Writes, views and triggers

- [x] [`insert table body`](api/change/insert.art): explicit `columns` or `.columns:`, appended `row` blocks, and row-width validation.
- [x] [`update table body`](api/change/update.art): `assign column value`, bulk `.values:` labels, optional filters, and scalar/null values.
- [x] [`delete table body`](api/change/delete.art): optional filters.
- [ ] [`truncate table`](api/change/truncate-table.art): parsed; **dialect pending** because SQLite lacks TRUNCATE syntax.
- [x] [`create.view name body` / `drop.view name`](api/views/views.art): query-only bodies and escaped stored literals, including pagination counts.
- [x] [`create.trigger name body`](api/trigger/triggers.art): `.on:`, `.before`/`.after`, `.insert`/`.update`/`.delete`; independent nested writes and escaped stored literals.
- [x] Validate trigger `new`/`old` references against the selected event.

## Execution and delivery

- [x] `to :sqliteQuery statement`: deterministic compilation to `text` and `params` without mutating input.
- [ ] Preserve SQLite numeric and null parameter semantics using package-owned scoped functions; keep native functions unchanged.
- [x] `sqliteExecute db statement`: native query rows; empty result for commands without rows; caller-owned connection.
- [x] `sqliteTable db statement`: terminal tables with optional `.header:` and empty-result handling.
- [x] Existing Unitt specifications and runnable examples cover the completed implementation (180 assertions at the start of this round).
- [x] Add regression tests for the remaining expression, scope and set-operation work.
- [x] Automate construction checks for every example in the `api/` catalog.
- [ ] Update API documentation and runnable examples for this round's completed behavior.
- [ ] Run Unitt and all examples sequentially, inspect results, and commit this round's changes.

## Current round

The active implementation scope is expression composition, reference-scope validation,
set-operand isolation, catalog checks, documentation and verification. Dialect-pending
items remain unchecked until a supported compilation/execution strategy is implemented.
