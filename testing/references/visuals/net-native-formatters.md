# .NET native formatters

Reproduction of the formatter comparison table used in the Insecure
Deserialization notes.

The **Format** column marks how directly the formatter can be driven to code
execution: red means no extra precondition beyond the format itself, amber means
the attacker needs control of the expected type or a weak resolver.

| Name | Format | Additional requirements | Gadgets |
|---|---|---|---|
| **BinaryFormatter** | Binary | none | `ISerializable` gadgets |
| **NetDataContractSerializer** | XML | none | `ISerializable` gadgets |
| **SoapFormatter** | SOAP XML | none | `ISerializable` gadgets |
| **DataContractSerializer** | XML | Control of the expected type, or `knownTypes`, or a weak `DataContractResolver` | Setter gadgets; some `ISerializable` gadgets |
| **XmlSerializer** | XML | Control of the expected type | Quite limited; does not work with interfaces |
| **JavaScriptSerializer** | JSON | Insecure `TypeResolver` | Setter gadgets |
| **DataContractJsonSerializer** | JSON | Control of the expected type, or `knownTypes` | Setter gadgets; some `ISerializable` gadgets |
| **ObjectStateFormatter** | Text, Binary | none | Uses `BinaryFormatter` internally; `TypeConverter` gadgets |
| **LosFormatter** | Text, Binary | none | Uses `ObjectStateFormatter` internally |
| **BinaryMessageFormatter** | Binary | none | Uses `BinaryFormatter` internally |
| **XmlMessageFormatter** | XML | Control of the expected type | Uses `XmlSerializer` internally |

## Reading the table

The four formatters with no precondition are the interesting ones: if a target
deserializes attacker-controlled bytes with `BinaryFormatter`,
`NetDataContractSerializer`, `SoapFormatter`, `ObjectStateFormatter`,
`LosFormatter`, or `BinaryMessageFormatter`, the only remaining work is finding a
gadget chain that reaches a dangerous method.

The three that merely *wrap* another formatter matter because they extend the
reach of the ones underneath — `LosFormatter` and `ObjectStateFormatter` both land
on `BinaryFormatter`, so a target that is not obviously using `BinaryFormatter`
may still be exploitable through them. `ObjectStateFormatter` adds
`TypeConverter` gadgets to the available set.

Source: `pwntester`, "Attacking .NET serialization", slide 15.
