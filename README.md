# Template for Arturo Packages

This template is intented to be used for the creation of
new Arturo Packages.

## Features

### Carefully designed fashion README

The readme was carefully designed to maintain consistency across packages:

- Custom Badges
- Quick Presentation
- Autotamized installation guide

### Common structure

This templates ships a common structure:

- `.github`: Github Integration.
- `.vscode`: VsCode Integration.
- `docs`: Documentation.
- `examples`: Usage Examples.
- `specs`: All kind of Tests.
- `src`: Source Code

### Better defaults

- Integrates with `unitt`, ou main testing library.
  - Comes with its best default.
- Integrates with Github CI
  - Uses our modern way of using Arturo on CI, via it's official action.

### Ready to Use

- No spending time trying to keep README consistency
- Ready to ship to pkgr.art
- CI integration since its first commit

## Usage

1. Create a new repository using it as template
    1. <img src="./template/docs/create-from-template.png" alt="Step 1: Create from Template" width="600" style="max-width:100%;height:auto;" />
2. On Github, create a `LICENSE` file and choose your license using their templates
    1. On Github, reate a new file: <img src="./template/docs/create-new-file.png" alt="Step 2.1: Create file on Github" width="600" style="max-width:100%;height:auto;" />
    2. Name this file and `LICENSE` and click in "Choose a License": <img src="./template/docs/name-license-file.png" alt="Step 2.2: Name it as LICENSE and choose a template" width="600" style="max-width:100%;height:auto;" />
    3. Choose your favorite License, review and submit a commit: <img src="./template/docs/review-and-submit-license.png" alt="Step 2.3: Choose your License and submit" width="600" style="max-width:100%;height:auto;" />
3. Run `arturo boot.art` and follow the instructions.
  Don't worry, this script will delete itself and the useless files for your project.
