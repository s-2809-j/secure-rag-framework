from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from src.input_security_agent.models import Document

logger = logging.getLogger(__name__)


class AttackPackLoader:

    def __init__(self, attack_pack_root: str | Path) -> None:
        self.attack_pack_root = Path(attack_pack_root)

        if not self.attack_pack_root.exists():
            raise FileNotFoundError(
                f"Attack pack directory does not exist: "
                f"{self.attack_pack_root}"
            )

        if not self.attack_pack_root.is_dir():
            raise NotADirectoryError(
                f"Expected a directory: {self.attack_pack_root}"
            )

    def load(self) -> list[Document]:

        documents: list[Document] = []

        for category_dir in sorted(self.attack_pack_root.iterdir()):
            if not category_dir.is_dir():
                continue

            documents.extend(
                self._load_category(category_dir)
            )

        logger.info(
            "Loaded %d attack documents.",
            len(documents),
        )

        return documents

    def _load_category(
        self,
        category_dir: Path,
    ) -> list[Document]:

        documents: list[Document] = []

        for md_file in sorted(category_dir.glob("*.md")):
            try:
                text = md_file.read_text(
                    encoding="utf-8"
                ).strip()

                if not text:
                    logger.warning(
                        "Skipping empty markdown file: %s",
                        md_file,
                    )
                    continue

                documents.append(
                    Document(
                        content=text,
                        metadata={
                            "source": str(md_file),
                            "document_name": md_file.name,
                            "domain" : category_dir.name,
                            "filename" : md_file.name,
                            "attack_category": category_dir.name,
                        },
                    )
                )

            except Exception:
                logger.exception(
                    "Failed loading attack pack: %s",
                    md_file,
                )

        return documents