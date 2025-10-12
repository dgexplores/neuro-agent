from typing import List, Dict, Any

class NeuroMedicalKnowledge:
    """Medical knowledge base for neurological conditions"""

    def __init__(self):
        self.treatment_guidelines = {
            "migraine": [
                "Consider triptans for acute treatment",
                "Evaluate need for prophylactic therapy",
                "Assess trigger factors"
            ],
            "stroke": [
                "Immediate CT/MRI imaging",
                "Consider thrombolytic therapy if within window",
                "Neurological monitoring required"
            ],
            "seizure": [
                "EEG evaluation recommended",
                "Consider antiepileptic drugs",
                "Evaluate underlying causes"
            ],
            "parkinson": [
                "DaTscan if diagnosis uncertain",
                "Levodopa trial consideration",
                "Physical therapy evaluation"
            ]
        }

        self.drug_interactions = {
            ("warfarin", "aspirin"): "Increased bleeding risk",
            ("phenytoin", "carbamazepine"): "Decreased phenytoin levels",
        }

    def get_treatment_guidelines(self, condition: str) -> List[str]:
        """Get evidence-based treatment guidelines"""

        condition_lower = condition.lower()

        for key, guidelines in self.treatment_guidelines.items():
            if key in condition_lower:
                return guidelines

        return ["Consult current clinical guidelines"]

    def check_drug_interactions(self, medications: List[str]) -> List[str]:
        """Check for drug interactions"""

        interactions = []

        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                interaction_key = (med1.lower(), med2.lower())
                reverse_key = (med2.lower(), med1.lower())

                if interaction_key in self.drug_interactions:
                    interactions.append(f"{med1} + {med2}: {self.drug_interactions[interaction_key]}")
                elif reverse_key in self.drug_interactions:
                    interactions.append(f"{med1} + {med2}: {self.drug_interactions[reverse_key]}")

        return interactions
