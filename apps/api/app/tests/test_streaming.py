import asyncio
import json

from app.models.chat import ChatMetadata
from app.services.stream_writer import stream_response


def test_stream_response_emits_chunks_and_metadata() -> None:
    metadata = ChatMetadata(sources=[], follow_ups=[], intent="profile_overview")

    async def collect() -> list[str]:
      return [event async for event in stream_response("Bidworx analyses tenders.", metadata)]

    events = asyncio.run(collect())
    assert any("Bidworx" in event for event in events)
    metadata_payloads = [
        event.removeprefix("data: ").strip()
        for event in events
        if '"type": "metadata"' in event
    ]
    assert metadata_payloads
    assert json.loads(metadata_payloads[0])["intent"] == "profile_overview"
