from typing import Any

from langchain.agents import AgentState
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field, TypeAdapter


class ChunkMetadata(BaseModel):
    langgraph_node: str = Field(...)


chunk_metadata_adapter = TypeAdapter(ChunkMetadata)

type Agent = CompiledStateGraph[AgentState[Any], Any, Any, Any]
