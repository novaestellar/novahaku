# Stream Monitoring
> **ID:** M-07015 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 88%

Monitor streaming behavior in real-time, collecting metrics on token generation rate, latency distribution, error frequency, and connection health without modifying the stream itself.

## How It Works
- Attach a passive observer to the stream that records arrival timestamps and chunk metadata
- Compute real-time metrics: TTFT, inter-token latency (p50/p95/p99), tokens/second, error rate
- Detect anomalies: sudden stalls, duplicate chunks, out-of-order delivery, truncated streams
- Emit structured logs or metrics to observability platforms (Prometheus, Datadog, CloudWatch)
- Generate health reports summarizing stream quality over a time window or request batch

## Example
```python
import time
from dataclasses import dataclass, field

@dataclass
class StreamMetrics:
    chunks: int = 0
    tokens: int = 0
    start_time: float = field(default_factory=time.monotonic)
    itl_samples: list = field(default_factory=list)
    errors: int = 0

    @property
    def ttft(self):
        return self.itl_samples[0] if self.itl_samples else 0

    @property
    def tokens_per_sec(self):
        elapsed = time.monotonic() - self.start_time
        return self.tokens / elapsed if elapsed > 0 else 0

    @property
    def p99_itl(self):
        sorted_samples = sorted(self.itl_samples)
        idx = int(len(sorted_samples) * 0.99)
        return sorted_samples[idx] if sorted_samples else 0

async def monitor_stream(stream, metrics: StreamMetrics):
    prev = time.monotonic()
    async for chunk in stream:
        now = time.monotonic()
        metrics.itl_samples.append(now - prev)
        metrics.chunks += 1
        prev = now
        yield chunk
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, DeepSeek V3, Llama 3.1 405B, Mistral Large

## Success Rate
88% — Purely observational technique with no stream modification; highest success rate as it avoids interference with stream delivery.

## Related Methods
- M-07005: Chunk Analysis
- M-07001: Stream Interception
- M-07006: Rate Limiting
