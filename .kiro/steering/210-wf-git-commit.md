---
inclusion: manual
---
# Rule: Git Commit Message Specification

The commit message must follow this strict format: `<type>(<scope>): <subject>`

### **Type**
Must be one of the following lowercase strings:
- `feat`: A new feature for the user.
- `fix`: A bug fix for the user.
- `chore`: Changes to the build process, auxiliary tools, or other chores that don't affect user-facing code.
- `docs`: Documentation only changes.
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `ci`: Changes to our CI configuration files and scripts.

### **Scope (Optional)**
A noun describing the section of the codebase affected.
Examples: `web`, `coprocessor`, `db`, `auth`, `ui`, `api`.

### **Subject**
- **Must** start with a lowercase letter.
- **Must not** end with a period.
- **Must** be a short, imperative description of the change (e.g., "add login button" not "added login button").
- **Must** be 50 characters or less.