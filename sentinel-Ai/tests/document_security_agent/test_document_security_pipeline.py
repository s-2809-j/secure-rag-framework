# tests/document_security_agent/test_document_security_pipeline.py

from pathlib import Path

from src.document_security_agent.document_security_agent import (
    DocumentSecurityAgent,
)
from src.document_security_agent.factory.document_security_factory import (
    DocumentSecurityFactory,
)
from src.document_security_agent.models import FileMetadata


# expected_allowed:
#     True  -> document should be ALLOWED (benign)
#     False -> document should be BLOCKED (malicious)
# expected_categories:
#     set of AttackCategory .value strings that MUST appear somewhere
#     in the aggregation report's category_summaries for the test
#     to be considered correct. Empty set = no specific category
#     required (only expected_allowed is checked).
TEST_DOCUMENTS = [
    (
        "Benign",
        Path(
            "tests/document_security_agent/fixtures/benign/hr_policy.txt"
        ),
        True,
        set(),
    ),
    (
        "Prompt Injection",
        Path(
            "tests/document_security_agent/fixtures/malicious/prompt_injection.txt"
        ),
        False,
        {"prompt_injection"},
    ),
    (
        "Jailbreak",
        Path(
            "tests/document_security_agent/fixtures/malicious/jailbreak.txt"
        ),
        False,
        {"jailbreak"},
    ),
    (
        "PII",
        Path(
            "tests/document_security_agent/fixtures/malicious/pii.txt"
        ),
        False,
        {"pii"},
    ),
    (
        "Mixed Attack",
        Path(
            "tests/document_security_agent/fixtures/malicious/mixed_attack.txt"
        ),
        False,
        {"prompt_injection", "jailbreak"},
    ),
    (
        "System Prompt Leak",
        Path(
            "tests/document_security_agent/fixtures/malicious/system_prompt_leak.txt"
        ),
        False,
        {"system_prompt_leakage"},
    ),
]


def print_banner(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def print_separator() -> None:
    print("-" * 90)


def execute_test(
    agent: DocumentSecurityAgent,
    name: str,
    file_path: Path,
    expected_allowed: bool,
    expected_categories: set[str],
) -> bool:
    """
    Returns True if the test passed (no crash AND correct verdict
    AND all expected categories were detected), False otherwise.
    """

    print_banner(f"TEST : {name}")

    if not file_path.exists():
        print(f"Document not found : {file_path}")
        return False

    metadata = FileMetadata(
        filename=file_path.name,
        extension=file_path.suffix,
        mime_type="text/plain",
        size_bytes=file_path.stat().st_size,
    )

    try:

        decision = agent.analyze(
            file_path=str(file_path),
            metadata=metadata,
        )

        print_separator()
        print("FINAL DECISION")
        print_separator()

        print(f"Allowed          : {decision.allowed}")
        print(f"Message          : {decision.message}")

        print_separator()
        print("RISK")
        print_separator()

        print(
            f"Risk Level       : "
            f"{decision.risk_assessment.risk_level}"
        )

        print(
            f"Risk Score       : "
            f"{decision.risk_assessment.risk_score:.2f}"
        )

        print_separator()
        print("POLICY")
        print_separator()

        print(
            f"Allowed          : "
            f"{decision.policy_evaluation.allowed}"
        )

        print(
            f"Explanation      : "
            f"{decision.policy_evaluation.explanation}"
        )

        print_separator()
        print("AGGREGATION")
        print_separator()

        aggregation = decision.aggregation_report

        print(
            f"Total Chunks     : "
            f"{aggregation.statistics.total_chunks}"
        )

        print(
            f"Flagged Chunks   : "
            f"{aggregation.statistics.flagged_chunks}"
        )

        print(
            f"Safe Chunks      : "
            f"{aggregation.statistics.safe_chunks}"
        )

        print()

        detected_categories: set[str] = set()

        for summary in aggregation.category_summaries:

            detected_categories.add(summary.category.value)

            print(
                f"[{summary.category.value}]"
            )

            print(
                f"  Affected Chunks : "
                f"{summary.affected_chunks}"
            )

            print(
                f"  Matches         : "
                f"{summary.total_matches}"
            )

            print(
                f"  Confidence      : "
                f"{summary.highest_confidence:.2f}"
            )

            print()

        print_separator()
        print("TIER-1")

        tier1 = decision.detection_report.tier1_report

        print(
            f"Chunks           : "
            f"{len(tier1.chunk_results)}"
        )

        print_separator()
        print("TIER-2")

        tier2 = decision.detection_report.tier2_report

        if tier2 is not None:

            print(
                f"Chunks           : "
                f"{len(tier2.chunk_results)}"
            )

            for chunk_result in tier2.chunk_results:
                seen_detectors = {
                    vr.detector_name for vr in chunk_result.validation_results
                }
                print(
                    f"  Detectors that ran on this chunk : "
                    f"{sorted(seen_detectors)}"
                )

        else:

            print("Chunks           : 0")

        # --------------------------------------------------
        # Verdict checking (this is what makes it a REAL test)
        # --------------------------------------------------

        print_separator()
        print("VERDICT CHECK")
        print_separator()

        failures: list[str] = []

        if decision.allowed != expected_allowed:
            failures.append(
                f"Expected allowed={expected_allowed}, "
                f"got allowed={decision.allowed}"
            )

        missing_categories = expected_categories - detected_categories

        if missing_categories:
            failures.append(
                f"Missing expected categories: {sorted(missing_categories)} "
                f"(detected: {sorted(detected_categories)})"
            )

        if failures:
            print_separator()
            print("TEST FAILED (wrong verdict)")
            print_separator()
            for failure in failures:
                print(f"  - {failure}")
            return False

        print_separator()
        print("TEST PASSED")
        return True

    except Exception as exc:

        print_separator()
        print("TEST FAILED (exception)")
        print_separator()

        print(type(exc).__name__)
        print(exc)
        return False


def main():

    print_banner("DOCUMENT SECURITY PIPELINE TEST")

    #
    # Uses the production factory.
    #
    # The factory should build the complete pipeline
    # with all production dependencies.
    #
    agent = DocumentSecurityFactory.create_agent()

    results: list[tuple[str, bool]] = []

    for name, path, expected_allowed, expected_categories in TEST_DOCUMENTS:

        passed = execute_test(
            agent=agent,
            name=name,
            file_path=path,
            expected_allowed=expected_allowed,
            expected_categories=expected_categories,
        )

        results.append((name, passed))

    print_banner("SUMMARY")

    total = len(results)
    passed_count = sum(1 for _, passed in results if passed)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")

    print()
    print(f"{passed_count}/{total} tests passed.")

    print_banner(
        "DOCUMENT SECURITY PIPELINE TEST COMPLETED"
    )

    if passed_count != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()