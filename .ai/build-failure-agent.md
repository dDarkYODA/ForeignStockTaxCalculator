# Purpose
Automatically diagnose and fix CI/CD failures.

# Instructions
When a CI pipeline or build fails:
1. Fetch CI logs from the failed job.
2. Identify the root cause category:
   * compilation errors
   * dependency issues
   * lint failures
   * type errors
   * failing tests
   * environment/configuration issues
3. Generate a fix plan.
4. Apply fixes such as:
   * correcting syntax or type errors
   * fixing imports or dependencies
   * updating configuration
   * repairing failing tests
   * adjusting build scripts
5. Run the build locally.
6. If the build succeeds:
   * commit the fix to the same branch
   * push the changes.
7. Repeat until the CI pipeline succeeds.

Never bypass failures by disabling tests or removing validations.
