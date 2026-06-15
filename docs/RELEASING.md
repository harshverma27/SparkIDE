# Releasing SparkIDE

Releases are automated by `.github/workflows/release.yml`: pushing a `v*` tag
runs the test suites and publishes a GitHub Release whose notes are pulled from
the matching `CHANGELOG.md` section.

## Steps

1. **Pick the version.** Follow [SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`.
   Each roadmap phase ships at least a `MINOR` bump.

2. **Update the version string.** It lives in a single place — `APP_VERSION` in
   `app_config.py` — and flows to the QApplication version, the About dialog, and
   the log welcome line. Bump it with:
   ```bash
   make bump-version VERSION=X.Y.Z
   ```

3. **Update `CHANGELOG.md`.** Rename the `## [Unreleased]` section to
   `## [X.Y.Z] — YYYY-MM-DD` and start a fresh empty `## [Unreleased]` above it.
   The release workflow extracts the section header matching the tag's version
   (without the `v`), so the heading **must** read `## [X.Y.Z]`.

4. **Commit** the version bump and changelog on `main` (via PR):
   ```bash
   git commit -am "chore: release vX.Y.Z"
   ```

5. **Tag and push:**
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

6. **Watch the Release workflow.** It runs Python + JS tests, then creates the
   GitHub Release with the extracted notes. If tests fail, no release is
   published — fix forward and re-tag.

## Notes

- Binary/installer artifacts (AppImage, MSI, dmg) are **not** built yet; that
  arrives in Phase 4 (Cross-Platform Packaging). This workflow currently
  publishes source + notes only.
- To test the extraction locally before tagging:
  ```bash
  awk -v ver="X.Y.Z" '/^## \['"X.Y.Z"'\]/{c=1;next} c&&/^## \[/{exit} c' CHANGELOG.md
  ```
