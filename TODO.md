# SQL API evolution

Reference: [API contracts](api/API.md), [writing guide](api/STYLE.md), and the linked feature examples below.

A checked feature has implementation and regression coverage for the target
explicitly described. An unchecked feature still needs the work described.
SQLite and PostgreSQL compilers are implemented; PostgreSQL server execution is
not claimed. MySQL plans below remain proposals awaiting syntax decisions.

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
- [x] [`fetch count`](api/limit/fetch.art): SQLite translates to LIMIT/OFFSET; PostgreSQL emits native FETCH/OFFSET.

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
- [x] [`group.sets`](api/group/grouping-sets.art): validate grouping blocks, including an empty grouping set; PostgreSQL emits GROUPING SETS; SQLite rejects it.
- [x] [`group.rollup`](api/group/rollup.art): PostgreSQL emits ROLLUP; SQLite rejects it.
- [x] [`group.cube`](api/group/cube.art): PostgreSQL emits CUBE; SQLite rejects it.

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
- [x] [`all query`](api/subquery/all.art): validate a single-column query operand; PostgreSQL emits ALL; SQLite rejects it.
- [x] [`any query`](api/subquery/any.art): validate a single-column query operand; PostgreSQL emits ANY; SQLite rejects it.
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
- [x] [`column.identity`](api/tables/identity-column.art): PostgreSQL emits GENERATED ALWAYS AS IDENTITY; SQLite rejects it.
- [x] [`alter table body` / `rename newName`](api/tables/alter-table.art): rename tables; one SQLite alteration per statement.
- [x] [`add name storageType`](api/tables/add-column.art): `.optional`, `.primary`, `.unique` and `.identity` use column contracts; SQLite restrictions still apply.
- [x] [`remove name`](api/tables/drop-column.art): DROP COLUMN; requires a supporting SQLite version.
- [x] [`drop table`](api/tables/drop-table.art): DROP TABLE.

## Writes, views and triggers

- [x] [`insert table body`](api/change/insert.art): explicit `columns` or `.columns:`, appended `row` blocks, and row-width validation.
- [x] [`update table body`](api/change/update.art): `assign column value`, bulk `.values:` labels, optional filters, and scalar/null values.
- [x] [`delete table body`](api/change/delete.art): optional filters.
- [x] [`truncate table`](api/change/truncate-table.art): PostgreSQL emits TRUNCATE TABLE; SQLite rejects it.
- [x] [`create.view name body` / `drop.view name`](api/views/views.art): query-only bodies and escaped stored literals, including pagination counts.
- [x] [`create.trigger name body`](api/trigger/triggers.art): `.on:`, `.before`/`.after`, `.insert`/`.update`/`.delete`; independent nested writes and escaped stored literals.
- [x] Validate trigger `new`/`old` references against the selected event.

## Execution and delivery

- [x] `sql.query: db statement`: execute captured blocks, dictionaries or compiled SQLite queries; return native rows.
- [x] `to :sqliteQuery statement`: deterministic compilation to `text` and `params` without mutating input.
- [x] Preserve SQLite numeric and null parameter semantics using package-owned scoped functions; keep native functions unchanged.
- [x] `sqliteExecute db statement`: native query rows; empty result for commands without rows; caller-owned connection.
- [x] `sqliteTable db statement`: terminal tables with optional `.header:` and empty-result handling.
- [x] Existing Unitt specifications and runnable examples cover the completed implementation (180 assertions at the start of this round).
- [x] Add regression tests for the remaining expression, scope and set-operation work.
- [x] Automate construction checks for every example in the `api/` catalog.
- [x] Update API documentation and runnable examples for this round's completed behavior.
- [x] Run Unitt and all examples sequentially, inspect results, and commit this round's changes.

## Completed implementation round

Expression composition, reference-scope validation, set-operand isolation, catalog
checks, documentation and verification are complete. Dialect-pending items remain
unchecked until a supported compilation/execution strategy is implemented.


### Verification and commits

- `84f45db`: expression composition, relation scopes, set-operand isolation and catalog checks.
- `ab3a51b`: scoped SQLite scalar adapters; preserve native functions after success and errors.
- Final verification: 404 Unitt assertions pass; every runnable example and `src/main.art` pass, executed sequentially. The API example is included in CI.

## PostgreSQL and MySQL compilation proposal

Status: PostgreSQL compilation is now implemented through `to :postgresQuery`.
SQLite remains available through `to :sqliteQuery`. PostgreSQL execution adapters
and MySQL compilation remain future work. MySQL syntax and translation policies
below are still proposals. No tracking issues have been opened.


- [x] Add compilation-only `:postgresQuery` with `text`, `params`, and an explicit `statements` list.
- [ ] Add compilation-only `:mysqlQuery` with `text` and `params`.
- [x] Scope PostgreSQL helpers locally and preserve SQLite/native functions across success and errors.
- [x] Emit PostgreSQL quoted identifiers, numbered placeholders, native scalar parameters, FETCH, grouping extensions, ALL/ANY, identity and TRUNCATE.
- [ ] Emit MySQL quoted identifiers, positional placeholders, LIMIT pagination, rollups, ALL/ANY, AUTO_INCREMENT and TRUNCATE; reject unsupported combinations.
- [x] Generate PostgreSQL schema, views and triggers, including separate function/trigger DDL.
- [ ] Generate MySQL schema, views and trigger syntax.
- [x] Test PostgreSQL nested parameter ordering, catalog compilation, dialect boundaries and immutable input without requiring database drivers.
- [x] Document implemented PostgreSQL/SQLite support, run checks sequentially, and commit each verified step.
- [ ] Document and verify MySQL once its compiler is implemented.

### Full feature matrix

SQLite describes the current implementation. PostgreSQL describes implemented compilation capabilities; MySQL 8.4 describes
proposed compilation capabilities. PostgreSQL output
is compiler-tested; no PostgreSQL server execution is claimed. “Translate” is a proposal that still needs a syntax/policy decision.

| API feature | SQLite: current | PostgreSQL: compiler implemented | MySQL 8.4: proposed |
| --- | --- | --- | --- |
| `select`, appended projections, `.as:` | Supported | Supported | Supported |
| `select.distinct` | Supported | Supported | Supported |
| `from`, table aliases | Supported | Supported | Supported |
| `where`, repeated filters | Supported | Supported | Supported |
| Comparisons, `and`, `or`, `not` | Supported | Supported | Supported |
| `between`, `in`, `like` | Supported | Supported | Supported |
| `is null`, `is not null` | Supported | Supported | Supported |
| Arithmetic and nested scalar expressions | Supported | Supported | Supported |
| INNER JOIN | Supported | Supported | Supported |
| LEFT JOIN | Supported | Supported | Supported |
| RIGHT JOIN | SQLite version dependent | Supported | Supported |
| FULL JOIN | SQLite version dependent | Supported | Unsupported natively |
| CROSS JOIN and self joins | Supported | Supported | Supported |
| `order.asc`, `order.desc` | Supported | Supported | Supported |
| `limit`, `.skip:`, `offset` | Supported | Supported | Supported |
| `fetch` | Translated to LIMIT/OFFSET | Native FETCH | Proposed translation to LIMIT/OFFSET |
| `group` | Supported | Supported | Supported |
| `having` | Supported | Supported | Supported |
| `group.rollup` | Rejected | Native ROLLUP | WITH ROLLUP |
| `group.cube` | Rejected | Native CUBE | Unsupported natively |
| `group.sets` | Rejected | Native GROUPING SETS | Unsupported natively |
| `count`, `sum`, `avg`, `min`, `max` | Supported | Supported | Supported |
| `choose`, `when`, `otherwise`, `.default:` | Supported | Supported | Supported |
| `coalesce`, `nullif` | Supported | Supported | Supported |
| Scalar and correlated subqueries | Supported | Supported | Supported |
| `exists` | Supported | Supported | Supported |
| `all`, `any` | Rejected | Supported | Supported, with subquery restrictions |
| `with` CTEs | Supported | Supported | Supported |
| UNION, INTERSECT, EXCEPT | Supported | Supported | Supported |
| `create`, `column` | Supported | Supported | Supported |
| Required and optional columns | Supported | Supported | Supported |
| `.primary`, `.unique` | Supported | Supported | Subject to index/type restrictions |
| `reference` foreign keys | Supported | Supported | Subject to engine/index restrictions |
| `check` | Supported | Supported | Supported |
| `.identity` | Rejected | GENERATED ALWAYS AS IDENTITY | AUTO_INCREMENT; requires an indexed key |
| `alter`, `add`, `remove`, `rename` | Supported, SQLite restrictions | Supported | Supported |
| `drop` | Supported | Supported | Supported |
| `insert`, `columns`, `row` | Supported | Supported | Supported |
| `update`, `assign`, `.values:` | Supported | Supported | Supported |
| `delete` | Supported | Supported | Supported |
| `truncate` | Rejected | Native TRUNCATE | Native TRUNCATE |
| `create.view`, `drop.view` | Supported | Supported | Supported |
| `create.trigger` | Supported | Requires a trigger function | Requires FOR EACH ROW trigger syntax |

### Candidate compiler interfaces

SQLite and PostgreSQL spellings are implemented. MySQL spelling remains a proposal.

| Detail | SQLite: implemented | PostgreSQL: implemented | MySQL: candidate |
| --- | --- | --- | --- |
| Query type | `:sqliteQuery` | `:postgresQuery` | `:mysqlQuery` |
| Output fields | `text`, `params` | `text`, `params`, `statements` | `text`, `params` |
| Identifier quoting | `"name"` | `"name"` | `` `name` `` |
| Parameter placeholders | `?` | `$1`, `$2`, ... | `?` |
| Arturo execution adapter | `sql.query:`, `sqliteExecute`, `sqliteTable` | Separate future work | Separate future work |

SQL generation can be implemented without a native Arturo database driver.
Execution, connections and driver integration are separate work items. Server
execution tests are distinct from compiler tests and must not be claimed until run.

### Decisions to make before implementation or issue creation

- [x] Select SQLite or PostgreSQL with `to :sqliteQuery` / `to :postgresQuery`; MySQL naming remains proposed.
- [ ] Decide whether unsupported features produce errors or use documented translations/emulation.
- [ ] Decide whether MySQL `fetch` translates to LIMIT/OFFSET or is rejected.
- [ ] Define identity behavior: PostgreSQL ALWAYS versus BY DEFAULT, MySQL AUTO_INCREMENT indexing requirements, and any SQLite mapping.
- [ ] Define per-dialect storage types, string lengths and indexable string constraints.
- [x] Define PostgreSQL native boolean/null parameters and numbered placeholders for external drivers.
- [ ] Define MySQL parameter handling and placeholder conventions.
- [x] Define PostgreSQL trigger helper naming and emit separate function/trigger statements; callers manage cleanup.
- [x] Expose PostgreSQL multi-statement DDL through an ordered `statements` block alongside `text` and `params`.
- [ ] Define MySQL version requirements and diagnostics for unsupported joins, grouping extensions and restricted quantified subqueries.
- [x] Validate PostgreSQL through compiler regression tests and the complete API catalog.
- [ ] Add optional PostgreSQL server execution checks and driver integration.
- [ ] After syntax decisions, create tracking issues from the agreed scope. No issues have been opened yet.

### Candidate issue breakdown for later

1. Dialect selection and compiled-query interface.
2. Scoped compiler infrastructure, identifier quoting and parameter numbering.
3. PostgreSQL query features: pagination, grouping extensions and quantified comparisons.
4. PostgreSQL schema, identity columns, views and triggers.
5. MySQL query features, syntax translations and unsupported-feature diagnostics.
6. MySQL schema, AUTO_INCREMENT, views and triggers.
7. Cross-dialect catalog tests, parameter-order tests and native-function preservation.
8. Documentation, support matrix and runnable compilation examples.
9. Optional PostgreSQL/MySQL driver integration and server execution tests.

### Reference documentation

- [PostgreSQL SELECT, pagination and grouping](https://www.postgresql.org/docs/current/sql-select.html).
- [PostgreSQL quantified subqueries](https://www.postgresql.org/docs/current/functions-subquery.html).
- [PostgreSQL identity columns](https://www.postgresql.org/docs/current/ddl-identity-columns.html).
- [PostgreSQL TRUNCATE](https://www.postgresql.org/docs/current/sql-truncate.html).
- [PostgreSQL triggers](https://www.postgresql.org/docs/current/sql-createtrigger.html).
- [MySQL 8.4 SELECT](https://dev.mysql.com/doc/refman/8.4/en/select.html).
- [MySQL 8.4 rollups](https://dev.mysql.com/doc/refman/8.4/en/group-by-modifiers.html).
- [MySQL 8.4 subqueries](https://dev.mysql.com/doc/refman/8.4/en/subqueries.html).
- [MySQL 8.4 AUTO_INCREMENT](https://dev.mysql.com/doc/refman/8.4/en/example-auto-increment.html).
- [MySQL 8.4 TRUNCATE](https://dev.mysql.com/doc/refman/8.4/en/truncate-table.html).

### PostgreSQL implementation notes

- `to :postgresQuery statement` returns `text`, native scalar `params`, and `statements`.
- Parameters are numbered in SQL order across CTEs, projections, joins and nested queries.
- Trigger compilation emits a function definition and a CREATE TRIGGER command as two statements.
- Trigger helper names use `sql_trigger_` plus a deterministic SHA1 digest of table and trigger names; no existing function is replaced.
- Stored definitions inline escaped literals. PostgreSQL trigger dollar-quote delimiters avoid collisions with body content.
- SQLite continues to reject non-equivalent identity, grouping, quantified comparison and truncate operations.

### SQLite dialect boundary

- [x] Translate `fetch`/`.skip:` to LIMIT/OFFSET without mutating the input or changing bound parameter order.
- [x] Keep non-equivalent SQLite operations explicit: grouping extensions, ALL/ANY, GENERATED ALWAYS identity and TRUNCATE diagnostics point to `to :postgresQuery`.
- [ ] Choose any future SQLite emulation or identity/truncate mapping separately; no implicit semantic substitution is implemented.

### Current PostgreSQL delivery

- [x] Implement `to :postgresQuery` without introducing dialect keywords into captured SQL bodies.
- [x] Compile all eight formerly unavailable API constructs through PostgreSQL; translate SQLite FETCH safely.
- [x] Verify 722 assertions, including scoped-helper cleanup, native-function preservation and every catalog example.
- [x] Document compilation-only support and provide a runnable PostgreSQL example in CI.
- [x] Run all examples sequentially and commit the final documentation/example step.

Commits: `8d48697` adds PostgreSQL compilation; `a98c1ee` adds SQLite FETCH translation and dialect diagnostics.
