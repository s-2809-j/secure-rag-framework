from pathlib import Path

from src.knowledge_base.loader import MarkdownLoader


def main():

    loader = MarkdownLoader(
        Path("domain_packs")
    )

    documents = loader.load()

    print("\n" + "=" * 80)
    print("LOADER TEST")
    print("=" * 80)

    print(f"\nTotal Documents Loaded : {len(documents)}")

    for index, document in enumerate(documents, start=1):

        print("\n" + "-" * 80)
        print(f"Document #{index}")
        print("-" * 80)

        print("Metadata")

        for key, value in document.metadata.items():
            print(f"{key:15}: {value}")

        print("\nContent Preview")

        preview = document.content[:250]

        print(preview)

        if len(document.content) > 250:
            print("...")

    print("\n" + "=" * 80)
    print("LOADER TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()