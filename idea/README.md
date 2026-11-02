# SQL feature ideas

Scope: every statement, clause, operator, and function explicitly listed in the
SQLTutorial.org main learning sequence, from SELECT through WITH. This is a
design catalog, not a claim to cover every SQL standard or vendor extension.

Reference: https://www.sqltutorial.org/

Examples use an original book catalog. `.art` files pair the DSL with conceptual
SQL directly below `---`, Arturo’s end-of-file string syntax.
DSL code is uncommented, including proposed syntax. These files are design
references; proposed grammar is not implemented. The reference SQL uses inline values;
the current compiler quotes identifiers and binds scalar values.

Start with `select.art`, then `order-by.art`; continue in the order below.
Supported labels identify existing feature capabilities. Drafts now prefer scalar
arguments without list blocks; these forms still require parser changes.
RIGHT JOIN additionally requires a compatible SQLite runtime.

Proposed grammar is tentative. FETCH, schema changes, triggers, grouping extensions,
and quantified comparisons require explicit dialect decisions before implementation.


## Syntax decisions

These drafts follow [Arturo’s language syntax](https://arturo-lang.io/documentation/language/).
Only `idea/` is being designed; the library grammar remains unchanged.

- `sql [...]` receives unevaluated data. SQL words such as `and`, `or`, and
  `not` are DSL tokens; they do not call Arturo’s logical functions.
- Omit blocks for a single value: `select title`, `select *`, `orderBy title`,
  `groupBy genre`, and `[count *]`. Keep blocks for multiple values, grouped
  predicates, SQL expressions, nested queries, and individual grouping sets.
- Blocks hold lists, predicates, SQL expressions, and nested queries. Parentheses
  capture a host Arturo value; they do not group SQL expressions.
- Table and view names prefer type tokens, such as `:books` and `:recentBooks`.
  Column names remain words or literals. Literals such as `'where` escape DSL
  keywords, and paths such as `b\title` qualify columns.
- Strings and numbers in expressions are SQL values. The compiler binds them.
- Flags select variants (`join.left`, `column.notNull`). Attribute labels carry
  named options (`.as:`, `.into:`, `.on:`).
- Proposed schema operations use `create.table`, `alter.table`, `drop.table`,
  and `column` with constraint flags. Column types use native type tokens:
  `:integer` maps to SQL INTEGER and `:string` to SQL TEXT. SQL-specific types
  still need a mapping design. `add-column.art` retains the original alternative
  exploration, including custom `:books` and `:text` type names.
- Proposed UPDATE assignments use labels: `set [available: false]`. These are
  parsed as data, not evaluated into an Arturo dictionary.
- Proposed CASE expressions use one expression block with explicit `when` branches
  and an `else` value.
- Use `where -> predicate` and `having -> predicate` to omit outer predicate blocks.
  The next clause or enclosing block ends the predicate; inner grouping is retained.
- Top-level schema bodies share the enclosing `sql` block. INSERT uses repeated
  `values [row ...]` clauses, keeping row boundaries without an outer rows block.
  These flatter forms are design proposals only.
- Use `=<` for Arturo’s less-or-equal symbol. SQL reference text uses `<=`.
  This spelling is a parser enhancement proposal, not current library behavior.
- `---` begins one string containing everything through the end of the file.
  Reference SQL goes directly below it, without braces.

## Querying data

- [select](select.art) — supported.

## Sorting rows

- [order-by](order-by.art) — supported.

## Limiting rows

- [distinct](distinct.art) — supported.
- [limit](limit.art) — supported.
- [fetch](fetch.art) — proposed.

## Filtering rows

- [where](where.art) — supported.
- [and](and.art) — supported.
- [or](or.art) — supported.
- [between](between.art) — proposed, including the `=<` spelling.
- [in](in.art) — proposed.
- [like](like.art) — proposed.
- [is-null](is-null.art) — supported.
- [not](not.art) — proposed.

## Joining tables

- [inner-join](inner-join.art) — supported.
- [left-join](left-join.art) — supported.
- [right-join](right-join.art) — supported.
- [full-outer-join](full-outer-join.art) — proposed.
- [cross-join](cross-join.art) — proposed.
- [self-join](self-join.art) — supported.

## Grouping rows

- [group-by](group-by.art) — proposed.
- [having](having.art) — proposed.
- [grouping-sets](grouping-sets.art) — proposed.
- [rollup](rollup.art) — proposed.
- [cube](cube.art) — proposed.

## Set operators

- [union](union.art) — proposed.
- [intersect](intersect.art) — proposed.
- [minus](minus.art) — proposed.

## Working with tables

- [create-table](create-table.art) — proposed.
- [primary-key](primary-key.art) — proposed.
- [not-null](not-null.art) — proposed.
- [drop-table](drop-table.art) — proposed.
- [add-column](add-column.art) — proposed.
- [drop-column](drop-column.art) — proposed.
- [foreign-key](foreign-key.art) — proposed.
- [unique](unique.art) — proposed.
- [check](check.art) — proposed.
- [alter-table](alter-table.art) — proposed.
- [identity-column](identity-column.art) — proposed.

## Modifying data

- [insert](insert.art) — proposed.
- [update](update.art) — proposed.
- [delete](delete.art) — proposed.
- [truncate-table](truncate-table.art) — proposed.

## Views and triggers

- [views](views.art) — proposed.
- [triggers](triggers.art) — proposed.

## Conditional expressions

- [case](case.art) — proposed.
- [coalesce](coalesce.art) — proposed.
- [nullif](nullif.art) — proposed.

## Aggregate functions

- [aggregate-functions](aggregate-functions.art) — supported.
- [avg](avg.art) — supported.
- [count](count.art) — supported.
- [sum](sum.art) — supported.
- [max](max.art) — supported.
- [min](min.art) — supported.

## Subqueries

- [subquery](subquery.art) — proposed.
- [correlated-subquery](correlated-subquery.art) — proposed.
- [exists](exists.art) — proposed.
- [all](all.art) — proposed.
- [any](any.art) — proposed.

## Common table expressions

- [with](with.art) — proposed.

## Alternatives

Each file keeps its existing examples first and adds an alternative as its last
`sql` block above `---`. Both spellings are design candidates for the same SQL
behavior, not promises of implementation support. The reference string is shared.
The aggregate-functions draft retains its existing authored reference unchanged;
its expression-list alternative uses the pageCount names from that reference.

| Feature | Alternative explored |
| --- | --- |
| [add-column](add-column.art) | Action and object naming |
| [aggregate-functions](aggregate-functions.art) | Explicit expression list |
| [all](all.art) | Literal target instead of a type target |
| [alter-table](alter-table.art) | Action and object naming |
| [and](and.art) | Predicate block instead of an arrow |
| [any](any.art) | Predicate block instead of an arrow |
| [avg](avg.art) | Projection attribute instead of an expression block |
| [between](between.art) | Predicate block instead of an arrow |
| [case](case.art) | Separate branch-list block |
| [check](check.art) | Action and object naming |
| [coalesce](coalesce.art) | Projection attribute instead of an expression block |
| [correlated-subquery](correlated-subquery.art) | Predicate block instead of an arrow |
| [count](count.art) | Projection attribute instead of an expression block |
| [create-table](create-table.art) | Action and object naming |
| [cross-join](cross-join.art) | Literal target instead of a type target |
| [cube](cube.art) | Action and object naming |
| [delete](delete.art) | Action and object naming |
| [distinct](distinct.art) | Explicit projection list |
| [drop-column](drop-column.art) | Action and object naming |
| [drop-table](drop-table.art) | Action and object naming |
| [exists](exists.art) | Predicate block instead of an arrow |
| [fetch](fetch.art) | Attribute-based ordering |
| [foreign-key](foreign-key.art) | Action and object naming |
| [full-outer-join](full-outer-join.art) | Literal target instead of a type target |
| [group-by](group-by.art) | Attribute-based grouping |
| [grouping-sets](grouping-sets.art) | Action and object naming |
| [having](having.art) | Predicate block instead of an arrow |
| [identity-column](identity-column.art) | Action and object naming |
| [in](in.art) | Predicate block instead of an arrow |
| [inner-join](inner-join.art) | Literal target instead of a type target |
| [insert](insert.art) | Positional target instead of an attribute |
| [intersect](intersect.art) | Explicit set-operation family |
| [is-null](is-null.art) | Predicate block instead of an arrow |
| [left-join](left-join.art) | Literal target instead of a type target |
| [like](like.art) | Predicate block instead of an arrow |
| [limit](limit.art) | Attribute-based ordering |
| [max](max.art) | Projection attribute instead of an expression block |
| [min](min.art) | Projection attribute instead of an expression block |
| [minus](minus.art) | Explicit set-operation family |
| [not-null](not-null.art) | Action and object naming |
| [not](not.art) | Predicate block instead of an arrow |
| [nullif](nullif.art) | Projection attribute instead of an expression block |
| [or](or.art) | Predicate block instead of an arrow |
| [order-by](order-by.art) | Attribute-based ordering |
| [primary-key](primary-key.art) | Action and object naming |
| [right-join](right-join.art) | Literal target instead of a type target |
| [rollup](rollup.art) | Action and object naming |
| [select](select.art) | Explicit projection list |
| [self-join](self-join.art) | Literal target instead of a type target |
| [subquery](subquery.art) | Predicate block instead of an arrow |
| [sum](sum.art) | Projection attribute instead of an expression block |
| [triggers](triggers.art) | Action and object naming |
| [truncate-table](truncate-table.art) | Action and object naming |
| [union](union.art) | Explicit set-operation family |
| [unique](unique.art) | Action and object naming |
| [update](update.art) | Predicate block instead of an arrow |
| [views](views.art) | Action and object naming |
| [where](where.art) | Predicate block instead of an arrow |
| [with](with.art) | Named common-table expression option |
