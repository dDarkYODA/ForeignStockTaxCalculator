# Purpose
Automatically resolve CodeRabbit review comments.

# Instructions
* Detect pull requests with CodeRabbit review comments.
* Fetch all unresolved review comments.
* Group comments by file and category (bug, style, refactor, performance, tests).
* Generate fixes addressing all comments.
* Apply patches to the repository.
* Run lint and tests.
* Commit fixes to the PR branch.
* Repeat until no CodeRabbit comments remain unresolved.
