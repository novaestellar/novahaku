# PHP loose comparison (`==`) matrix

Reproduction of the comparison table used in the Type Juggling notes. The values
are the result of `==` between the row and column operands.

Header row and first column hold the same sequence of operands.

| `==` | `TRUE` | `FALSE` | `1` | `2` | `0.2` | `-2` | `0` | `-1` | `"-1"` | `"0"` | `"1"` | `NULL` | `[]` | `{}` | `"xyz"` | `""` | `"0e1"` | `"0e99"` | `"2abc"` | `".2abc"` | `"-2abc"` | `"0x2"` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `TRUE` | true | false | true | false | true | false | true | false | false | true | true | false | false | false | false | false | true | true | true | true | true | true |
| `FALSE` | false | true | false | true | false | true | false | true | false | false | false | true | false | false | false | true | false | false | false | false | false | false |
| `1` | true | false | true | false | false | false | false | false | false | false | true | false | false | false | true | false | false | false | false | false | false | false |
| `2` | true | false | false | true | false | false | false | false | false | false | false | false | false | false | false | false | false | false | true | false | false | true |
| `0.2` | true | false | false | false | true | false | false | false | false | false | false | false | false | false | false | false | false | false | false | false | false | false |
| `-2` | true | false | false | false | false | true | false | false | false | false | false | false | false | false | false | false | false | false | false | false | true | false |
| `0` | false | true | false | false | false | false | true | false | false | true | false | true | false | false | false | true | true | true | true | true | false | false |
| `-1` | true | false | false | false | false | false | false | true | true | false | false | false | false | false | false | false | false | false | false | false | false | false |
| `"-1"` | true | false | false | false | false | false | false | true | true | false | false | false | false | false | false | false | false | false | false | false | false | false |
| `"0"` | false | true | false | false | false | false | true | false | false | true | false | true | false | false | false | true | true | true | true | true | false | false |
| `"1"` | true | false | true | false | false | false | false | false | false | false | true | false | false | false | false | false | false | false | false | false | false | false |
| `NULL` | false | true | false | false | false | false | true | false | false | false | false | true | true | true | false | true | false | false | false | false | false | false |
| `[]` | false | true | false | false | false | false | true | false | false | false | false | true | true | true | false | false | false | false | false | false | false | false |
| `{}` | false | false | false | false | false | false | false | false | false | false | false | true | true | true | false | false | false | false | false | false | false | false |
| `"xyz"` | true | false | true | false | false | false | false | false | false | false | false | false | false | false | true | false | false | false | false | false | false | false |
| `""` | false | true | false | false | false | false | false | false | false | false | false | false | false | false | false | true | false | false | false | false | false | false |
| `"0e1"` | true | false | true | false | false | false | true | false | false | true | false | false | false | false | false | false | true | true | false | false | false | false |
| `"0e99"` | true | false | true | false | false | false | true | false | false | true | false | false | false | false | false | false | true | true | false | false | false | false |
| `"2abc"` | true | false | false | true | false | false | false | false | false | false | false | false | false | false | false | false | false | false | true | false | false | false |
| `".2abc"` | true | false | false | false | true | false | false | false | false | false | false | false | false | false | false | false | false | false | false | true | false | false |
| `"-2abc"` | true | false | false | false | false | true | false | false | false | false | false | false | false | false | false | false | false | false | false | false | true | false |
| `"0x2"` | true | false | false | true | false | false | false | false | false | false | false | false | false | false | false | false | false | false | false | false | false | true |

## What the matrix shows

The rows that matter for exploitation are the scientific-notation collisions and
the numeric-string coercions:

- `"0e1" == "0e99"` is **true**. Both parse as `0` in scientific notation, so two
  different magic hashes compare equal.
- `"0e1" == "0"` and `"0e1" == 0` are **true**, and the same holds for `"0e99"`.
- `"1" == 1` is true, but `"1" == 2` is false — numeric strings coerce.
- `"2abc" == 2` is true (leading numeric prefix wins), while `"xyz" == 1` is also
  true — a non-numeric string compared against a number coerces to `0` in PHP < 8,
  which makes `0 == "xyz"` style bypasses work.
- `NULL == []`, `NULL == {}`, and `NULL == ""` are all true, so a missing or null
  value matches an empty container.
- `"0" == FALSE` and `"0" == NULL` are true — the classic auth-bypass primitive.

The `0e` family is the reason magic-hash attacks work: any hash comparison using
`==` where both sides look like `0e` followed by digits evaluates as equal.
