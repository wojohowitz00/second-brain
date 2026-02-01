# Naming (SOP)

Rules for note filenames and identifiers used by the agent when creating or referencing files.

## Filenames

- **Format**: kebab-case (lowercase, words separated by hyphens).
- **Characters**: Use only letters, numbers, and hyphens. No spaces, underscores, or special characters.
- **Length**: Maximum 30 characters (truncate and strip trailing hyphen if longer).
- **Empty**: If the content yields no valid name, use `untitled`.

## Examples

- "Hello World!" → `hello-world`
- "Test: Something" → `test-something`
- "Meeting notes from Q2 planning" → `meeting-notes-from-q2-plann` (truncated)

## Note

The file writer applies these rules automatically via `sanitize_filename`. Classifications should suggest short, clear subject names that survive sanitization well.
