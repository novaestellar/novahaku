# Binary assets in this tree

Every binary asset in the reference corpus, why it is kept, and — where the
content is reproducible as text — what reproduces it. Text reproductions live in
`visuals/`.

## Policy

A binary asset stays only when the picture is itself the content. It is removed
when its meaning survives as text without losing anything a reader needs: a table
becomes a markdown table, a flow becomes a numbered request sequence, a code
snippet becomes a fenced block.

Nothing is removed while it is still the only carrier of its content.

## Every asset is now reachable

Four assets were previously referenced by broken markup — `![alt]` with no
target, or a hard-coded external URL — so the file was present but never rendered.
That is fixed: each of the four now points at its text reproduction, and the
markdown is valid. The originals are kept because the layout or colour coding
carries information a table loses.

| Asset | Size | Rendered from | Text reproduction |
|---|---|---|---|
| `payloads-extras/Type Juggling/Images/table_representing_behavior_of_PHP_with_loose_type_comparisons.png` | 44,011 B | `Type Juggling/README.md:43` (was `![LooseTypeComparison]`, no target) | `visuals/php-loose-comparison.md` |
| `payloads-extras/Insecure Deserialization/Images/NETNativeFormatters.png` | 284,395 B | `Insecure Deserialization/DotNET.md:49` (was `![NETNativeFormatters.png]`, no target) | `visuals/net-native-formatters.md` |
| `payloads-extras/SAML Injection/Images/XSLT1.jpg` | 152,989 B | `SAML Injection/README.md:165` (was an external `sso-attacks.org` URL) | `visuals/xslt-attack.md` |
| `payloads-extras/Web Cache Deception/Images/wcd.jpg` | 108,232 B | `Web Cache Deception/README.md:34` | `visuals/wcd-flow.md` |

The type-comparison matrix is reproduced in full (23×23 operands, every cell), so
the asset is the one case where a reader loses nothing by using the text alone.
The other three keep their picture because the spatial arrangement is the point.

## Separately referenced copy

| Asset | Size | Referenced from | Notes |
|---|---|---|---|
| `payloads/Web Cache Deception/Images/wcd.jpg` | 2,247 B | `payloads/Web Cache Deception/README.md:34` | Low-resolution copy used by the `payloads/` tree. |

`payloads/` and `payloads-extras/` are **not** duplicates of each other. They hold
the same subject matter with different markdown table formatting, and each tree
carries its own copies of the assets it references.

## Removed

| Asset | Size | Reason |
|---|---|---|
| `payloads-extras/Cross-Site Request Forgery/Images/CSRF-CheatSheet.png` | 417,021 B | Zero references anywhere in the repo, no surrounding prose. Nothing to reproduce. |
| `payloads-extras/Insecure Direct Object References/Images/idor.png` | 179,442 B | Zero references to the file. The token "idor" appears throughout as ordinary prose about the vulnerability class, never as a path. |
| `payloads-extras/GraphQL Injection/Images/htb-help.png` | 21,217 B | Zero references to the file. |
| `payloads-extras/SAML Injection/Images/SAML-xml-flaw.png` | 8,907 B | Zero references to the file. |

## Not binary at all — corrected

`misc/mindmaps-pdf/*.pdf` (4 files, 6,301 B total) were named `.pdf` but contained
plain Markdown — byte-for-byte valid `.md` with no PDF structure. They were
renamed to `misc/mindmaps/*.md` under a folder that no longer claims a format:

| Was | Now |
|---|---|
| `misc/mindmaps-pdf/CORS.pdf` | `misc/mindmaps/CORS.md` |
| `misc/mindmaps-pdf/SSRF.pdf` | `misc/mindmaps/SSRF.md` |
| `misc/mindmaps-pdf/XXE.pdf` | `misc/mindmaps/XXE.md` |
| `misc/mindmaps-pdf/Prototype Pollution.pdf` | `misc/mindmaps/Prototype Pollution.md` |

Content is byte-identical after the rename; only the extension and folder changed.
The four inbound links in `misc/web-hacking-notes.md:32-35` were updated to match.
No reproduction was needed — the files were always text.

## Removal discipline

An asset is deleted only after confirming that (a) nothing references its filename
anywhere in the repo, and (b) its content is either reproduced as text or absent
from the surrounding prose. Verification is by exact filename match — matching the
bare technique name would false-positive on prose about the topic.
