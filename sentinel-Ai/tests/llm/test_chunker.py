from pathlib import Path

from src.knowledge_base.loader import MarkdownLoader
from src.knowledge_base.chunker import TextChunker


def main():

    loader = MarkdownLoader(
        Path("domain_packs")
    )

    documents = loader.load()

    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = chunker.chunk_documents(
        documents
    )

    print("\n" + "=" * 80)
    print("CHUNKER TEST")
    print("=" * 80)

    print(f"\nDocuments Loaded : {len(documents)}")
    print(f"Chunks Generated : {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):

        print("\n" + "-" * 80)
        print(f"Chunk #{index}")
        print("-" * 80)

        print("Metadata")

        for key, value in chunk.metadata.items():
            print(f"{key:15}: {value}")

        print("\nChunk Length")

        print(len(chunk.content))

        print("\nChunk Preview")

        preview = chunk.content[:200]

        print(preview)

        if len(chunk.content) > 200:
            print("...")

    print("\n" + "=" * 80)
    print("CHUNKER TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()