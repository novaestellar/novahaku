# Flush Control
> **ID:** M-07012 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 70%

Control when and how stream buffers are flushed to the client, optimizing the balance between throughput efficiency and time-to-first-token (TTFT) latency.

## How It Works
- Configure flush granularity: per-token, per-chunk, per-line, or per-sentence
- Implement adaptive flush that uses immediate flush for first N tokens then switches to batched
- Force flush on semantic boundaries (code block end, paragraph break, markdown header)
- Disable Nagle's algorithm on the TCP socket to prevent kernel-level buffering delays
- Monitor flush frequency and adjust buffer thresholds based on observed TTFT metrics

## Example
```python
import socket

def disable_nagle(sock: socket.socket):
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

class AdaptiveFlusher:
    def __init__(self, initial_flush=True, batch_after=3):
        self.flushed = 0
        self.batch_after = batch_after

    async def flush(self, writer, chunk):
        writer.write(chunk)
        if self.flushed < self.batch_after:
            await writer.drain()  # Immediate flush for first tokens
        self.flushed += 1
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 2.0 Flash, Llama 3.2 90B, Qwen 2.5, Phi-4

## Success Rate
70% — Effective for optimizing TTFT; server-side buffering and proxy layers may override flush semantics.

## Related Methods
- M-07007: Stream Buffering
- M-07006: Rate Limiting
- M-07005: Chunk Analysis
