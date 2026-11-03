# Command-Line Interface

The `sql` command-line interface lets you work with SQLite databases using Arturo's SQL DSL. Execute statements against a database, or compile them into SQL without opening a connection.

## Installation

Install the package using Arturo's package manager:

```sh
arturo -p install sql
```

The `sql` executable is installed in `~/.arturo/packages/bin`. Make sure this directory is included in your `PATH` (see [Troubleshooting](#troubleshooting)).

## Commands

```text
sql — Query SQLite databases with the Arturo SQL DSL

USAGE
    sql [OPTIONS] <command> [ARGS]

COMMANDS
    query       Execute a DSL statement against SQLite
    compile     Compile a DSL statement without connecting
```

Run `sql <command> --help` for command-specific help.

### `query`

Execute a DSL statement against a SQLite database.

```text
USAGE
    sql query [OPTIONS] <database> [<expression>]

OPTIONS
    -f, --file=VALUE      Read the DSL body from a file instead of an expression
    -o, --format=VALUE    Output format: table or json (default: table)
```

`<database>` is the SQLite database path. Provide the DSL statement directly as `<expression>`, or load it from a file using `--file`.

### `compile`

Convert an Arturo SQL DSL statement into SQL without connecting to a database.

```text
USAGE
    sql compile [OPTIONS] [<expression>]

OPTIONS
    -f, --file=VALUE      Read the DSL body from a file instead of an expression
    -d, --dialect=VALUE   SQL dialect: sqlite or postgres (default: sqlite)
```

Use `--dialect` to choose the target SQL dialect. Compilation does not execute the generated SQL.

## Quick start

The following examples create a SQLite database, insert two books, and query the results.

### 1. Create a table

```sh
sql query books.db \
  'create :books [column title :string column publishedYear :integer]'
```

### 2. Insert two books

```sh
sql query books.db \
  'insert :books [columns [title publishedYear] row ["River Atlas" 2024] row ["Quiet Maps" 2021]]'
```

### 3. Query books published since 2023

```sh
sql query books.db \
  'from :books select [title publishedYear] where [publishedYear >= 2023]'
```

To get JSON output instead of the default table format, add `--format json`:

```sh
sql query books.db \
  'from :books select [title publishedYear]' \
  --format json
```

### 4. Compile a statement for PostgreSQL

```sh
sql compile 'from :books select title' --dialect postgres
```

This generates SQL without requiring a database connection.

## Reading statements from files

For longer DSL statements, use `--file` instead of passing an inline expression:

```sh
sql query books.db --file statement.art
sql compile --file statement.art --dialect postgres
```

The file should contain the DSL statement you want to execute or compile.

## Development

When working on the CLI itself, run the source entry point:

```sh
arturo src/main.art
```

Use this in place of the installed `sql` command so you test your local changes rather than the latest package installed from [pkgr.art](https://sql.pkgr.art/).

## Troubleshooting

### `sql: command not found`

First, make sure the package is installed:

```sh
arturo -p install sql
```

Arturo installs package executables in `~/.arturo/packages/bin`. On Unix-like shells, add that directory to your `PATH`:

```sh
export PATH="$HOME/.arturo/packages/bin:$PATH"
```

Add the same line to your shell's startup configuration to make the change persistent. Then check whether the executable is available:

```sh
command -v sql
```

#### Configure your PATH

The `PATH` environment variable tells your shell where to find executable commands. Choose the instructions for your operating system and shell.

**Bash (Linux, macOS, Git Bash)**

Add the package directory to the current terminal session:

```sh
export PATH="$HOME/.arturo/packages/bin:$PATH"
```

To make the change permanent, add the same line to `~/.bashrc` for interactive Bash sessions on most Linux systems. On macOS, Bash login shells commonly use `~/.bash_profile` instead.

**Zsh (macOS, Linux)**

```sh
export PATH="$HOME/.arturo/packages/bin:$PATH"
```

Add that line to `~/.zshrc` to make it available in future interactive Zsh sessions.

**POSIX's `sh` (including `dash` and `ash`)**

```sh
PATH="$HOME/.arturo/packages/bin:$PATH"
export PATH
```

Add these lines to `~/.profile` for future login sessions. Plain `sh` sessions do not necessarily read `~/.profile` automatically.

**Fish**

Run this once in Fish:

```fish
fish_add_path --prepend ~/.arturo/packages/bin
```

Fish saves this change for future sessions and avoids adding the same directory repeatedly. You do not need to edit `config.fish`.

**Csh and Tcsh (FreeBSD)**

```sh
set path = ( "$HOME/.arturo/packages/bin" $path )
```

Add the same line to `~/.cshrc` or `~/.tcshrc` (whichever your shell reads) to make it permanent.

**Windows PowerShell**

Add the package directory for the current PowerShell session:

```ps1
$arturoBin = Join-Path $HOME '.arturo\packages\bin'
$env:Path = "$arturoBin;$env:Path"
```

For a permanent setting:

Open **Edit environment variables** for your account from the *Start menu*.

Select `Path` under **User variables**, then select Edit.

Select **New** and add `%USERPROFILE%\.arturo\packages\bin`.

Save the changes and reopen PowerShell.

This user-level setting also applies to new Command Prompt sessions.

**Windows Command Prompt (CMD)**

For the current Command Prompt session:

```bat
set "PATH=%USERPROFILE%\.arturo\packages\bin;%PATH%"
```

To make it permanent, use the Windows user Path editor described above. 

> [!WARNING]
> **Avoid replacing the entire Path** value with `setx PATH`, which can discard existing entries.

### Verify the installation

Open a new terminal and check whether `sql` can be found:

| Shell | Command |
| --- | --- |
| Bash, Zsh, sh, Fish | `command -v sql` |
| Csh, Tcsh | `which sql` |
| PowerShell | `Get-Command sql` |
| Windows CMD | `where sql` |

If the command is found, run `sql --help` to confirm the CLI starts.
