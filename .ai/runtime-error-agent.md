# Purpose
Automatically diagnose and fix runtime failures such as HTTP 500 errors.

# Instructions
When an internal server error or runtime exception is detected:
1. Collect error details:
   * stack trace
   * logs
   * request path
   * failing service/module
2. Determine the cause:
   * null reference
   * incorrect API usage
   * missing validation
   * database query failure
   * configuration issues
   * dependency failures
3. Reproduce the issue locally if possible.
4. Generate and apply fixes:
   * input validation
   * error handling improvements
   * correct logic errors
   * dependency fixes.
5. Add or update tests that reproduce the error.
6. Commit and push the fix.
