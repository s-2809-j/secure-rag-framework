from __future__ import annotations
from src.input_security_agent.detectors.prompt_injection_detector import PromptInjectionDetector
from src.input_security_agent.detectors.jailbreak_detector import JailbreakDetector
from src.input_security_agent.detectors.pii_detector import PIIDetector
from src.input_security_agent.detectors.malicious_instruction_detector import MaliciousInstructionDetector
from src.input_security_agent.detectors.system_prompt_detector import SystemPromptDetector
from src.document_security_agent.aggregation.document_aggregation_engine import (
    DocumentAggregationEngine,
)
from src.document_security_agent.chunking.document_chunker import (
    DocumentChunker,
)
from src.document_security_agent.detector.document_detector_engine import (
    DocumentDetectionEngine,
)
from src.document_security_agent.document_security_agent import (
    DocumentSecurityAgent,
)
from src.document_security_agent.document_security_pipeline import (
    DocumentSecurityPipeline,
)
from src.document_security_agent.escalation.document_escalation_engine import (
    DocumentEscalationEngine,
)
from src.document_security_agent.file_guard.file_guard import (
    FileGuard,
)
from src.document_security_agent.parser.document_parser import (
    DocumentParser,
)
from src.document_security_agent.preprocessing.document_normalizer import (
    DocumentNormalizer,
)
from src.document_security_agent.tier2.tier2_detection_engine import (
    Tier2DetectionEngine,
)
from src.input_security_agent.policies.rule_policy_engine import (
    RulePolicyEngine,
)
from src.input_security_agent.scoring.risk_scoring_engine import (
    RiskScoringEngine,
)

from src.document_security_agent.file_guard.extension_validator import (
    ExtensionValidator,
)
from src.document_security_agent.file_guard.mime_validator import (
    MimeValidator,
)
from src.document_security_agent.file_guard.size_validator import (
    SizeValidator,
)
from src.document_security_agent.file_guard.corruption_validator import (
    CorruptionValidator,
)
from src.document_security_agent.file_guard.malware_validator import (
    MalwareValidator,
)
from src.document_security_agent.tier2.detectors.llm_security_detector import LLMSecurityDetector
from src.document_security_agent.tier2.detectors.semantic_detector import SemanticDetector
from src.document_security_agent.parser.pdf_parser import PDFParser
from src.document_security_agent.parser.docx_parser import DocxParser
from src.document_security_agent.parser.txt_parser import TxtParser
from src.document_security_agent.parser.markdown_parser import MarkdownParser
from src.input_security_agent.preprocessing.input_normalizer import (
    InputNormalizer,
)
from src.knowledge_base.embedder import Embedder
from src.input_security_agent.semantic.attack_vector_store import (
    AttackVectorStore,
)
from src.input_security_agent.semantic.similarity_detector import (
    SimilarityDetector,
)
from src.llm.gemini_client import   GeminiLLMClient
# tier1_detectors = [
#     PromptInjectionDetector(),
#     JailbreakDetector(),
#     PIIDetector(),
#     MaliciousInstructionDetector(),
#     SystemPromptDetector(),
# ]

# tier2_detectors = [
#     SemanticDetector(...),
#     LLMSecurityDetector(...),
# ]
class DocumentSecurityFactory:

    @staticmethod
    def create_pipeline() -> DocumentSecurityPipeline:

        extension_validator = ExtensionValidator()
        mime_validator = MimeValidator()
        size_validator = SizeValidator()
        corruption_validator = CorruptionValidator()
        malware_validator = MalwareValidator()

        file_guard = FileGuard(
            extension_validator=extension_validator,
            mime_validator=mime_validator,
            size_validator=size_validator,
            corruption_validator=corruption_validator,
            malware_validator=malware_validator,
        )

        parsers = {
            ".pdf": PDFParser(),
            ".docx": DocxParser(),
            ".txt": TxtParser(),
            ".md": MarkdownParser(),
        }
        parser = DocumentParser(parsers=parsers)

        input_normalizer = InputNormalizer()
        normalizer = DocumentNormalizer(input_normalizer=input_normalizer)

        chunker = DocumentChunker()

        tier1_detectors = [
            PromptInjectionDetector(),
            JailbreakDetector(),
            PIIDetector(),
            MaliciousInstructionDetector(),
            SystemPromptDetector(),
        ]
        detection_engine = DocumentDetectionEngine(detectors=tier1_detectors)

        escalation_engine = DocumentEscalationEngine()

        # --- Tier-2 wiring ---
        embedder = Embedder()
        attack_vector_store = AttackVectorStore()
        similarity_detector = SimilarityDetector(
            embedder=embedder,
            vector_store=attack_vector_store,
        )
        semantic_detector = SemanticDetector(
            similarity_detector=similarity_detector,
        )

        llm_client = GeminiLLMClient()
        llm_security_detector = LLMSecurityDetector(llm_client=llm_client)

        tier2_detectors = [semantic_detector, llm_security_detector]
        tier2_engine = Tier2DetectionEngine(detectors=tier2_detectors)

        aggregation_engine = DocumentAggregationEngine()
        policy_engine = RulePolicyEngine()
        risk_engine = RiskScoringEngine()

        return DocumentSecurityPipeline(
            file_guard=file_guard,
            parser=parser,
            doc_normalizer=normalizer,
            chunker=chunker,
            detection_engine=detection_engine,
            aggregation_engine=aggregation_engine,
            policy_engine=policy_engine,
            risk_engine=risk_engine,
            escalation_engine=escalation_engine,
            tier2_engine=tier2_engine,
        )

    @staticmethod
    def create_agent() -> DocumentSecurityAgent:
        pipeline = DocumentSecurityFactory.create_pipeline()
        return DocumentSecurityAgent(pipeline=pipeline)