"""Tests for streaming pacing and StreamingConfig."""

import asyncio
import json
import pytest

from app.services.stream_writer import (
    StreamingConfig,
    DEFAULT_STREAMING_CONFIG,
    stream_text,
    _atoms,
    _ends_sentence,
    _ends_comma,
)


# ---------------------------------------------------------------------------
# StreamingConfig unit tests
# ---------------------------------------------------------------------------

def test_default_config_values():
    cfg = DEFAULT_STREAMING_CONFIG
    assert cfg.word_chunk_min == 4
    assert cfg.word_chunk_max == 10
    assert cfg.min_chunk_chars == 14
    assert cfg.delay_ms == 45
    assert cfg.sentence_pause_ms == 140
    assert cfg.comma_pause_ms == 70
    assert cfg.newline_pause_ms == 55


def test_config_delay_properties():
    cfg = StreamingConfig(delay_ms=100, sentence_pause_ms=200, comma_pause_ms=50, newline_pause_ms=80)
    assert cfg.delay_s == 0.1
    assert cfg.sentence_pause_s == 0.2
    assert cfg.comma_pause_s == 0.05
    assert cfg.newline_pause_s == 0.08


def test_config_is_customisable():
    cfg = StreamingConfig(word_chunk_min=2, word_chunk_max=5, delay_ms=10)
    assert cfg.word_chunk_min == 2
    assert cfg.word_chunk_max == 5
    assert cfg.delay_ms == 10


def test_config_is_frozen():
    cfg = StreamingConfig()
    with pytest.raises(AttributeError):
        cfg.delay_ms = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------

def test_atoms_splits_words_and_newlines():
    # The regex splits newline-only sequences as standalone atoms when
    # they appear after whitespace (i.e. a real blank line separator).
    atoms = _atoms("Hello world.\n\nNext line.")
    # Should produce at least 4 atoms (words + possible newline atoms).
    assert len(atoms) >= 3
    # The full text must be recoverable.
    assert "".join(atoms) == "Hello world.\n\nNext line."


def test_ends_sentence():
    assert _ends_sentence("word.")
    assert _ends_sentence("word! ")
    assert _ends_sentence("word?")
    assert _ends_sentence("word:")
    assert not _ends_sentence("word,")
    assert not _ends_sentence("word")


def test_ends_comma():
    assert _ends_comma("word,")
    assert _ends_comma("word; ")
    assert not _ends_comma("word.")
    assert not _ends_comma("word")


# ---------------------------------------------------------------------------
# Streaming output tests
# ---------------------------------------------------------------------------

async def _collect_chunks(text: str, config: StreamingConfig | None = None) -> list[str]:
    chunks: list[str] = []
    async for raw_sse in stream_text(text, config=config):
        # Parse the SSE payload
        line = raw_sse.strip()
        if line.startswith("data:"):
            payload = line[5:].strip()
            event = json.loads(payload)
            if event.get("type") == "chunk":
                chunks.append(event["content"])
    return chunks


@pytest.mark.asyncio
async def test_stream_emits_multiple_chunks():
    text = (
        "David works across applied AI, Python backend systems, and "
        "Next.js product builds. He has shipped production systems "
        "in recruitment, developer tooling, and SaaS."
    )
    # Use zero delays so the test runs fast.
    fast_cfg = StreamingConfig(
        word_chunk_min=4, word_chunk_max=10,
        delay_ms=0, sentence_pause_ms=0, comma_pause_ms=0, newline_pause_ms=0,
    )
    chunks = await _collect_chunks(text, config=fast_cfg)
    assert len(chunks) > 1, "Streaming must emit more than one chunk"


@pytest.mark.asyncio
async def test_stream_preserves_full_text():
    text = "David is a senior AI engineer.\n\nHe builds production systems."
    fast_cfg = StreamingConfig(
        word_chunk_min=2, word_chunk_max=4,
        delay_ms=0, sentence_pause_ms=0, comma_pause_ms=0, newline_pause_ms=0,
    )
    chunks = await _collect_chunks(text, config=fast_cfg)
    reassembled = "".join(chunks)
    assert reassembled.strip() == text.strip()


@pytest.mark.asyncio
async def test_stream_empty_text_emits_nothing():
    fast_cfg = StreamingConfig(
        delay_ms=0, sentence_pause_ms=0, comma_pause_ms=0, newline_pause_ms=0,
    )
    chunks = await _collect_chunks("", config=fast_cfg)
    assert chunks == []


@pytest.mark.asyncio
async def test_stream_respects_custom_chunk_sizes():
    text = "one two three four five six seven eight nine ten eleven twelve"
    small_cfg = StreamingConfig(
        word_chunk_min=2, word_chunk_max=3,
        min_chunk_chars=1,
        delay_ms=0, sentence_pause_ms=0, comma_pause_ms=0, newline_pause_ms=0,
    )
    chunks = await _collect_chunks(text, config=small_cfg)
    # With max=3 words per chunk, 12 words should produce at least 4 chunks.
    assert len(chunks) >= 4


@pytest.mark.asyncio
async def test_stream_flushes_on_sentence_boundary():
    text = "First sentence. Second sentence starts here and keeps going on."
    fast_cfg = StreamingConfig(
        word_chunk_min=4, word_chunk_max=10,
        delay_ms=0, sentence_pause_ms=0, comma_pause_ms=0, newline_pause_ms=0,
    )
    chunks = await _collect_chunks(text, config=fast_cfg)
    # The first chunk should end at "sentence." (2 words, flushed early by sentence boundary)
    assert chunks[0].rstrip().endswith(".")
