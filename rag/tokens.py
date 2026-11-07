"""Token counting. cl100k_base is a proxy: Titan and Cohere tokenize differently.
Chunk budgets are in cl100k tokens; billed tokens come from Bedrock response headers."""
import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


def ntok(s: str) -> int:
    return len(_enc.encode(s))


def encode(s: str):
    return _enc.encode(s)


def decode(t) -> str:
    return _enc.decode(t)
