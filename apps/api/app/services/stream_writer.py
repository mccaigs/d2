import asyncio
import json
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.models.chat import ChatMetadata


@dataclass(frozen=True, slots=True)
class StreamingConfig:
    """Tuneable knobs for streamed-text pacing."""

    word_chunk_min: int = 4
    word_chunk_max: int = 10
    min_chunk_chars: int = 14
    delay_ms: int = 45
    sentence_pause_ms: int = 140
    comma_pause_ms: int = 70
    newline_pause_ms: int = 55

    @property
    def delay_s(self) -> float:
        return self.delay_ms / 1000

    @property
    def sentence_pause_s(self) -> float:
        return self.sentence_pause_ms / 1000

    @property
    def comma_pause_s(self) -> float:
        return self.comma_pause_ms / 1000

    @property
    def newline_pause_s(self) -> float:
        return self.newline_pause_ms / 1000


DEFAULT_STREAMING_CONFIG = StreamingConfig()


def _sse(event_type: str, content: str) -> str:
    return f"data: {json.dumps({'type': event_type, 'content': content})}\n\n"


# Split the answer into ordered atoms that preserve whitespace/newlines
# so the frontend can render the stream exactly as produced by the builder.
_ATOM_RE = re.compile(r"\n+|[^\s]+\s*")


def _atoms(text: str) -> list[str]:
    return _ATOM_RE.findall(text)


def _ends_sentence(chunk: str) -> bool:
    stripped = chunk.rstrip()
    return bool(stripped) and stripped[-1] in ".!?:"


def _ends_comma(chunk: str) -> bool:
    stripped = chunk.rstrip()
    return bool(stripped) and stripped[-1] in ",;"


async def stream_text(
    text: str,
    config: StreamingConfig | None = None,
) -> AsyncIterator[str]:
    """Yield the answer in natural, pace-aware chunks.

    Rules:
    - Newlines are emitted as their own chunk so markdown structure is
      preserved without fragmenting inline text.
    - Words are grouped in batches of ``config.word_chunk_min`` to
      ``config.word_chunk_max``, flushing early on sentence or comma
      boundaries so the cadence feels human.
    - Slightly longer pauses after sentence-ending punctuation.
    - Shorter pauses after commas / semicolons.
    """
    cfg = config or DEFAULT_STREAMING_CONFIG

    if not text:
        return

    buffer: list[str] = []
    words_in_buffer = 0

    for atom in _atoms(text):
        if atom.startswith("\n"):
            if buffer:
                yield _sse("chunk", "".join(buffer))
                buffer = []
                words_in_buffer = 0
                await asyncio.sleep(cfg.delay_s)
            yield _sse("chunk", atom)
            await asyncio.sleep(cfg.newline_pause_s)
            continue

        buffer.append(atom)
        words_in_buffer += 1

        current = "".join(buffer)
        at_min = words_in_buffer >= cfg.word_chunk_min
        at_max = words_in_buffer >= cfg.word_chunk_max
        long_enough = len(current) >= cfg.min_chunk_chars
        sentence_break = _ends_sentence(atom)
        comma_break = _ends_comma(atom)

        should_flush = (
            sentence_break
            or at_max
            or (at_min and long_enough)
            or (at_min and comma_break)
        )

        if should_flush:
            yield _sse("chunk", current)
            buffer = []
            words_in_buffer = 0
            if sentence_break:
                await asyncio.sleep(cfg.sentence_pause_s)
            elif comma_break:
                await asyncio.sleep(cfg.comma_pause_s)
            else:
                await asyncio.sleep(cfg.delay_s)

    if buffer:
        yield _sse("chunk", "".join(buffer))
        await asyncio.sleep(cfg.delay_s)


async def stream_metadata(metadata: ChatMetadata) -> AsyncIterator[str]:
    """Yield a single metadata event after text streaming is complete."""
    payload = {
        "type": "metadata",
        "sources": [s.model_dump() for s in metadata.sources],
        "follow_ups": metadata.follow_ups,
        "intent": metadata.intent,
        "cta": metadata.cta.model_dump() if metadata.cta else None,
        "show_contact_form": metadata.show_contact_form,
        "contact_reason": metadata.contact_reason,
    }
    yield f"data: {json.dumps(payload)}\n\n"


async def stream_done() -> AsyncIterator[str]:
    yield "data: [DONE]\n\n"


async def stream_response(
    text: str, metadata: ChatMetadata
) -> AsyncIterator[str]:
    async for chunk in stream_text(text):
        yield chunk
    async for event in stream_metadata(metadata):
        yield event
    async for done in stream_done():
        yield done
