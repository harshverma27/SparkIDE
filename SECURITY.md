# Security Policy

## Supported versions

SparkIDE is pre-2.0; security fixes are applied to the latest release and the
`main` branch.

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue.

- Preferred: open a [private security advisory](https://github.com/harshverma27/SparkIDE/security/advisories/new)
  on GitHub.
- Alternatively, email **harshkardam246@gmail.com** with details and, if
  possible, steps to reproduce.

You can expect an acknowledgement within a few days. Once a fix is available
we'll coordinate disclosure and credit you in the release notes (unless you
prefer to remain anonymous).

SparkIDE runs `arduino-cli` and embeds a local Blockly page in a
`QWebEngineView`. Reports about command injection, unsafe file handling, or the
web bridge are especially appreciated.
