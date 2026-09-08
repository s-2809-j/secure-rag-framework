from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EscalationRule:
    """
    High-confidence trigger that indicates the response
    should be evaluated by the Tier-2 Safety Judge.

    A rule match DOES NOT imply the response is unsafe.
    It only requests semantic evaluation.
    """

    name: str

    pattern: re.Pattern[str]

    description: str


CYBER_ABUSE_RULES: tuple[EscalationRule, ...] = (

    EscalationRule(
        name="reverse_shell",
        pattern=re.compile(
            r"\breverse\s+shell\b",
            re.IGNORECASE,
        ),
        description="Reverse shell instructions detected.",
    ),

    EscalationRule(
        name="credential_dumping",
        pattern=re.compile(
            r"\bcredential\s+dump(?:ing)?\b",
            re.IGNORECASE,
        ),
        description="Credential dumping detected.",
    ),

    EscalationRule(
        name="privilege_escalation",
        pattern=re.compile(
            r"\bprivilege\s+escalation\b",
            re.IGNORECASE,
        ),
        description="Privilege escalation detected.",
    ),

    EscalationRule(
        name="shellcode",
        pattern=re.compile(
            r"\bshellcode\b",
            re.IGNORECASE,
        ),
        description="Shellcode detected.",
    ),

    EscalationRule(
        name="ransomware_source",
        pattern=re.compile(
            r"\bransomware\b",
            re.IGNORECASE,
        ),
        description="Ransomware-related content detected.",
    ),

    EscalationRule(
        name="bypass_security_controls",
        pattern=re.compile(
            r"\bbypass\s+(?:basic\s+)?security\s+controls?\b",
            re.IGNORECASE,
        ),
        description="Security control bypass detected.",
    ),

    EscalationRule(
        name="bypass_authentication",
        pattern=re.compile(
            r"\bbypass\s+authentication\b",
            re.IGNORECASE,
        ),
        description="Authentication bypass detected.",
    ),

    EscalationRule(
        name="disable_antivirus",
        pattern=re.compile(
            r"\bdisable\s+(?:windows\s+)?(?:defender|antivirus|av)\b",
            re.IGNORECASE,
        ),
        description="Antivirus disabling detected.",
    ),

    EscalationRule(
        name="evade_detection",
        pattern=re.compile(
            r"\bevade\s+detection\b",
            re.IGNORECASE,
        ),
        description="Detection evasion detected.",
    ),

    EscalationRule(
        name="exploit_vulnerability",
        pattern=re.compile(
            r"\bexploit\s+(?:a\s+)?vulnerabilit(?:y|ies)\b",
            re.IGNORECASE,
        ),
        description="Exploit guidance detected.",
    ),

    EscalationRule(
        name="lateral_movement",
        pattern=re.compile(
            r"\blateral\s+movement\b",
            re.IGNORECASE,
        ),
        description="Lateral movement detected.",
    ),

    EscalationRule(
        name="command_and_control",
        pattern=re.compile(
            r"\b(?:command\s+and\s+control|c2)\b",
            re.IGNORECASE,
        ),
        description="Command-and-control terminology detected.",
    ),

    EscalationRule(
        name="persistence_mechanism",
        pattern=re.compile(
            r"\bpersistence\b",
            re.IGNORECASE,
        ),
        description="Persistence mechanism detected.",
    ),

)

MALWARE_DEVELOPMENT_RULES: tuple[EscalationRule, ...] = (

    EscalationRule(
        name="keylogger",
        pattern=re.compile(
            r"\bkeylogger\b",
            re.IGNORECASE,
        ),
        description="Keylogger development detected.",
    ),

    EscalationRule(
        name="payload_generator",
        pattern=re.compile(
            r"\bpayload\s+generator\b",
            re.IGNORECASE,
        ),
        description="Payload generation detected.",
    ),

    EscalationRule(
        name="meterpreter",
        pattern=re.compile(
            r"\bmeterpreter\b",
            re.IGNORECASE,
        ),
        description="Meterpreter detected.",
    ),

)

WEAPON_RULES: tuple[EscalationRule, ...] = (

    EscalationRule(
        name="explosive_device",
        pattern=re.compile(
            r"\bexplosive\s+device\b",
            re.IGNORECASE,
        ),
        description="Explosive device detected.",
    ),

    EscalationRule(
        name="improvised_explosive",
        pattern=re.compile(
            r"\bimprovised\s+explosive\b",
            re.IGNORECASE,
        ),
        description="IED-related content detected.",
    ),

    EscalationRule(
        name="weapon_construction",
        pattern=re.compile(
            r"\bbuild\s+(?:a|an)\s+weapon\b",
            re.IGNORECASE,
        ),
        description="Weapon construction detected.",
    ),

)
CRIMINAL_FACILITATION_RULES: tuple[EscalationRule, ...] = (

    EscalationRule(
        name="identity_theft",
        pattern=re.compile(
            r"\bidentity\s+theft\b",
            re.IGNORECASE,
        ),
        description="Identity theft related content detected.",
    ),

    EscalationRule(
        name="credit_card_fraud",
        pattern=re.compile(
            r"\bcredit\s+card\s+fraud\b",
            re.IGNORECASE,
        ),
        description="Credit card fraud detected.",
    ),

    EscalationRule(
        name="counterfeit_currency",
        pattern=re.compile(
            r"\bcounterfeit\s+currency\b",
            re.IGNORECASE,
        ),
        description="Counterfeit currency detected.",
    ),

)

EXTREMISM_RULES: tuple[EscalationRule, ...] = (

    EscalationRule(
        name="terrorist_recruitment",
        pattern=re.compile(
            r"\bjoin\s+(?:our\s+)?terrorist\s+group\b",
            re.IGNORECASE,
        ),
        description="Potential terrorist recruitment detected.",
    ),

    EscalationRule(
        name="extremist_manifesto",
        pattern=re.compile(
            r"\bextremist\s+manifesto\b",
            re.IGNORECASE,
        ),
        description="Extremist manifesto detected.",
    ),

    EscalationRule(
        name="pledge_allegiance",
        pattern=re.compile(
            r"\bpledge\s+allegiance\b",
            re.IGNORECASE,
        ),
        description="Extremist allegiance language detected.",
    ),

)

MASS_VIOLENCE_RULES: tuple[EscalationRule, ...] = (

    EscalationRule(
        name="mass_casualty_attack",
        pattern=re.compile(
            r"\bmass\s+casualty\b",
            re.IGNORECASE,
        ),
        description="Mass casualty content detected.",
    ),

    EscalationRule(
        name="school_shooting",
        pattern=re.compile(
            r"\bschool\s+shooting\b",
            re.IGNORECASE,
        ),
        description="School shooting related content detected.",
    ),

    EscalationRule(
        name="biological_weapon",
        pattern=re.compile(
            r"\bbiological\s+weapon\b",
            re.IGNORECASE,
        ),
        description="Biological weapon related content detected.",
    ),
    

)

ESCALATION_RULES: tuple[EscalationRule, ...] = (
    *CYBER_ABUSE_RULES,
    *MALWARE_DEVELOPMENT_RULES,
    *WEAPON_RULES,
    *CRIMINAL_FACILITATION_RULES,
    *EXTREMISM_RULES,
    *MASS_VIOLENCE_RULES,
)

__all__ = [
    "EscalationRule",
    "ESCALATION_RULES",
]