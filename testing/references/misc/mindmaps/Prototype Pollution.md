# Prototype Pollution — Mindmap

## Two Flavours
- **Client-side (DOM)**: browser JS merges user input into object prototypes
- **Server-side (Node.js)**: `lodash.merge`, `qs`, `hoek` etc. merge attacker JSON

## Core Primitives
- `__proto__`
- `constructor.prototype`
- `Object.prototype` via nested merge paths
- Payload: `{"__proto__": {"polluted": true}}`
- Via query string: `?__proto__[polluted]=true`
- Via bypassed filters: `__pro__proto__to__`, `constructor[prototype][polluted]=1`

## Client-Side Impact
- `Object.prototype.innerHTML` → XSS on every DOM element
- Bypass client-side sanitizers / deny-lists
- `fetch` option pollution, `srcdoc` injection

## Server-Side Impact
- Privilege escalation via `isAdmin` / `role` checks
- Auth bypass via polluted session/logic flags
- **RCE chains**: pollute `child_process` options
  - `Object.prototype.shell = "node"`
  - `Object.prototype.env = {"NODE_OPTIONS": "--require /proc/self/environ"}`
  - `Object.prototype.NODE_OPTIONS`
- DoS via polluted `toString`, `length`, `status`

## Gadgets
- `ejs` render options, `pug` `compileDebug`
- `child_process.exec` / `fork` / `spawn`
- `require` module resolution

## Detection
- Client: `Object.prototype.polluted` probes in console
- Server: send `{"__proto__":{"x":1}}` then observe behaviour change
- Tools: ppmap, nuclei prototype-pollution templates, Burp extensions

## Mitigation
- `Object.create(null)`, `Object.freeze(Object.prototype)`
- Schema validation, `--disable-proto=delete` in Node
