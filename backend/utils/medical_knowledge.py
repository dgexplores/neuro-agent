"""
Medical Knowledge Base for Neurological Conditions

This module provides evidence-based medical knowledge including:
- Treatment guidelines for neurological conditions
- Drug interaction checking with severity levels
- Clinical recommendations based on medical literature

References:
- Micromedex Drug Interactions Database
- Lexicomp Drug Interactions
- Neurology Drug Handbook, 2024
- Taiwan FDA Drug Safety Information
"""

from typing import List, Dict, Any, Tuple, Optional
from enum import Enum
from dataclasses import dataclass


class InteractionSeverity(str, Enum):
    """Drug interaction severity levels"""
    CONTRAINDICATED = "contraindicated"  # Do not co-administer
    SEVERE = "severe"                    # May cause serious adverse effects
    MODERATE = "moderate"                # May require monitoring or dosage adjustment
    MINOR = "minor"                      # Usually clinically insignificant


@dataclass
class DrugInteraction:
    """Detailed drug interaction information"""
    drug1: str
    drug2: str
    severity: InteractionSeverity
    description: str
    mechanism: str
    clinical_effects: List[str]
    recommendations: List[str]
    references: str


class NeuroMedicalKnowledge:
    """Medical knowledge base for neurological conditions and drug interactions"""

    def __init__(self):
        """Initialize medical knowledge base with treatment guidelines and drug interactions"""

        # Treatment guidelines for common neurological conditions
        self.treatment_guidelines = {
            "migraine": [
                "Consider triptans (sumatriptan, rizatriptan) for acute treatment in absence of contraindications",
                "Evaluate need for prophylactic therapy if ≥4 attacks/month (propranolol, topiramate, valproate)",
                "Assess and avoid trigger factors (stress, certain foods, sleep deprivation)",
                "Consider CGRP antagonists for refractory cases",
                "Non-pharmacological: Regular sleep, hydration, stress management"
            ],
            "stroke": [
                "IMMEDIATE CT/MRI imaging to rule out hemorrhage",
                "Consider IV alteplase if within 4.5 hour window and no contraindications",
                "Mechanical thrombectomy consideration for large vessel occlusion within 24 hours",
                "Aspirin 325mg within 24-48 hours if ischemic stroke",
                "Neurological monitoring in stroke unit",
                "Secondary prevention: antiplatelet therapy, statin, blood pressure control"
            ],
            "seizure": [
                "EEG evaluation recommended within 24-48 hours",
                "Consider antiepileptic drugs (levetiracetam, valproate, lamotrigine) based on seizure type",
                "Evaluate underlying causes: metabolic, structural, infectious",
                "MRI brain with epilepsy protocol if first unprovoked seizure",
                "Driving restrictions per local regulations",
                "Medication adherence counseling"
            ],
            "parkinson": [
                "DaTscan if diagnosis uncertain (distinguishes from essential tremor)",
                "Levodopa/carbidopa trial - gold standard for symptom control",
                "MAO-B inhibitors (rasagiline, selegiline) for early disease",
                "Physical therapy and occupational therapy evaluation",
                "Monitor for medication-induced complications (dyskinesias, on-off phenomenon)",
                "Screen for non-motor symptoms (depression, sleep disorders, constipation)"
            ],
            "multiple sclerosis": [
                "MRI brain and spine with gadolinium for diagnosis and monitoring",
                "Disease-modifying therapies (interferon-beta, glatiramer, fingolimod, natalizumab)",
                "Acute relapse treatment: high-dose IV methylprednisolone",
                "Symptomatic treatment: spasticity (baclofen), fatigue (modafinil), neuropathic pain (gabapentin)",
                "Physical therapy and rehabilitation",
                "Monitor for infections, especially with immunosuppressive therapies"
            ],
            "alzheimer": [
                "Cholinesterase inhibitors (donepezil, rivastigmine, galantamine) for mild-moderate dementia",
                "Memantine for moderate-severe dementia",
                "Neuropsychological testing to establish baseline",
                "Address cardiovascular risk factors",
                "Caregiver education and support",
                "Screen for depression and treat appropriately"
            ],
            "neuropathic pain": [
                "First-line: gabapentin or pregabalin",
                "Second-line: tricyclic antidepressants (amitriptyline) or SNRIs (duloxetine)",
                "Topical treatments for localized pain (lidocaine patches, capsaicin)",
                "Opioids reserved for refractory cases due to abuse potential",
                "Physical therapy and pain management programs",
                "Screen for underlying causes (diabetes, B12 deficiency, toxins)"
            ]
        }

        # Comprehensive neurological drug interactions database
        # Format: (drug1, drug2) -> DrugInteraction object
        self._interaction_database = self._initialize_drug_interactions()

    def _initialize_drug_interactions(self) -> Dict[Tuple[str, str], DrugInteraction]:
        """
        Initialize comprehensive drug interaction database

        Returns:
            Dictionary mapping drug pairs to interaction details
        """
        interactions = {}

        # Interaction 1: Warfarin + Aspirin
        interactions[("warfarin", "aspirin")] = DrugInteraction(
            drug1="Warfarin",
            drug2="Aspirin",
            severity=InteractionSeverity.SEVERE,
            description="Concurrent use significantly increases bleeding risk",
            mechanism="Additive anticoagulant and antiplatelet effects; aspirin inhibits platelet aggregation while warfarin inhibits vitamin K-dependent clotting factors",
            clinical_effects=[
                "Major bleeding (GI, intracranial, retroperitoneal)",
                "Prolonged bleeding time",
                "Easy bruising and petechiae"
            ],
            recommendations=[
                "Use combination only if clearly indicated (e.g., mechanical heart valve)",
                "Monitor INR closely, target lower range (2.0-2.5 vs 2.5-3.5)",
                "Consider gastroprotection with PPI",
                "Educate patient on bleeding signs",
                "Avoid NSAIDs and other antiplatelet agents"
            ],
            references="Micromedex 2024; ACC/AHA Anticoagulation Guidelines"
        )

        # Interaction 2: SSRIs + Triptans
        interactions[("sertraline", "sumatriptan")] = DrugInteraction(
            drug1="SSRIs (Sertraline, Fluoxetine, Paroxetine)",
            drug2="Triptans (Sumatriptan, Rizatriptan)",
            severity=InteractionSeverity.SEVERE,
            description="Risk of serotonin syndrome due to additive serotonergic effects",
            mechanism="Both agents increase serotonin availability at synapses; SSRIs inhibit reuptake, triptans are 5-HT1B/1D agonists",
            clinical_effects=[
                "Serotonin syndrome: agitation, confusion, hyperthermia",
                "Autonomic instability: tachycardia, labile BP, diaphoresis",
                "Neuromuscular hyperactivity: tremor, hyperreflexia, clonus",
                "GI symptoms: nausea, diarrhea"
            ],
            recommendations=[
                "Use combination with caution; risk is low but serious",
                "Start with lowest effective dose of triptan",
                "Educate patient on serotonin syndrome symptoms",
                "Monitor closely for 2-4 hours after first dose",
                "Consider alternative: non-serotonergic migraine treatments (NSAIDs, neuroleptics)"
            ],
            references="FDA Drug Safety Communication 2006; Neurology 2010;74:1358"
        )

        # Interaction 3: Levodopa + MAO Inhibitors
        interactions[("levodopa", "phenelzine")] = DrugInteraction(
            drug1="Levodopa",
            drug2="Non-selective MAO Inhibitors (Phenelzine, Tranylcypromine)",
            severity=InteractionSeverity.CONTRAINDICATED,
            description="Risk of hypertensive crisis; absolute contraindication",
            mechanism="MAO inhibitors prevent breakdown of dopamine formed from levodopa, leading to excessive catecholamine accumulation",
            clinical_effects=[
                "Hypertensive crisis: severe headache, chest pain, severe hypertension (>180/120)",
                "Risk of intracranial hemorrhage",
                "Tachycardia, arrhythmias",
                "Hyperpyrexia"
            ],
            recommendations=[
                "CONTRAINDICATED - do not use together",
                "Discontinue MAO inhibitor at least 14 days before starting levodopa",
                "MAO-B selective inhibitors (selegiline, rasagiline) at therapeutic doses are safe with levodopa",
                "Emergency treatment if occurs: phentolamine IV for hypertensive crisis"
            ],
            references="Parkinson's Disease Treatment Guidelines 2023; Br J Clin Pharmacol 1975"
        )

        # Interaction 4: Valproate + Lamotrigine
        interactions[("valproate", "lamotrigine")] = DrugInteraction(
            drug1="Valproate/Valproic Acid",
            drug2="Lamotrigine",
            severity=InteractionSeverity.SEVERE,
            description="Valproate inhibits lamotrigine metabolism, doubling plasma levels and increasing rash risk",
            mechanism="Valproate inhibits UDP-glucuronosyltransferase (UGT), the primary enzyme metabolizing lamotrigine",
            clinical_effects=[
                "Increased lamotrigine levels (2-fold increase)",
                "Stevens-Johnson syndrome (SJS) risk increased 5-10 fold",
                "Toxic epidermal necrolysis (TEN)",
                "Lamotrigine toxicity: ataxia, diplopia, dizziness"
            ],
            recommendations=[
                "Reduce lamotrigine dose by 50% when adding valproate",
                "Very slow lamotrigine titration (half the usual rate)",
                "Starting dose: 12.5mg every other day for 2 weeks, then 12.5mg daily",
                "Monitor for rash closely, especially first 8 weeks",
                "Discontinue immediately if rash appears",
                "Educate patient on early rash recognition"
            ],
            references="Epilepsia 2009;50(Suppl 4):2-4; Lamotrigine Prescribing Information 2024"
        )

        # Interaction 5: Carbamazepine + Oral Contraceptives
        interactions[("carbamazepine", "ethinyl estradiol")] = DrugInteraction(
            drug1="Carbamazepine",
            drug2="Oral Contraceptives (Ethinyl Estradiol, Levonorgestrel)",
            severity=InteractionSeverity.MODERATE,
            description="Carbamazepine reduces contraceptive efficacy through enzyme induction",
            mechanism="Carbamazepine induces CYP3A4 and other enzymes, accelerating metabolism of estrogens and progestins",
            clinical_effects=[
                "Decreased contraceptive efficacy",
                "Increased risk of unintended pregnancy",
                "Breakthrough bleeding",
                "Irregular menstrual cycles"
            ],
            recommendations=[
                "Use alternative contraception: IUD (copper or levonorgestrel), barrier methods",
                "If oral contraceptives used: consider higher dose (50mcg ethinyl estradiol minimum)",
                "Counsel patient on pregnancy risk",
                "Consider non-enzyme-inducing alternatives: levetiracetam, lamotrigine, valproate",
                "Backup barrier contraception recommended"
            ],
            references="Epilepsia 2006;47(Suppl 1):33-34; Contraception 2012;86:325"
        )

        # Interaction 6: Phenytoin + Warfarin
        interactions[("phenytoin", "warfarin")] = DrugInteraction(
            drug1="Phenytoin",
            drug2="Warfarin",
            severity=InteractionSeverity.MODERATE,
            description="Complex bidirectional interaction affecting both drug levels and anticoagulation",
            mechanism="Phenytoin induces warfarin metabolism initially, then competes for plasma protein binding; phenytoin also metabolized by CYP2C9 (warfarin inhibits)",
            clinical_effects=[
                "Initial decrease in INR (first 2-4 weeks) due to enzyme induction",
                "Later increase in INR due to protein binding displacement",
                "Unpredictable anticoagulation",
                "Phenytoin toxicity risk (ataxia, nystagmus, confusion)"
            ],
            recommendations=[
                "Monitor INR twice weekly for first month, then weekly",
                "Anticipate need for warfarin dose adjustment (may increase 20-40%)",
                "Monitor phenytoin levels if warfarin dose changed",
                "Consider alternative anticonvulsant (levetiracetam) or anticoagulant (DOAC if appropriate)",
                "Patient education on signs of bleeding and phenytoin toxicity"
            ],
            references="Clin Pharmacokinet 1984;9:309; Thromb Haemost 2003;90:998"
        )

        # Interaction 7: Ergotamines + Triptans
        interactions[("ergotamine", "sumatriptan")] = DrugInteraction(
            drug1="Ergotamines (Ergotamine, Dihydroergotamine)",
            drug2="Triptans (Sumatriptan, Rizatriptan, Eletriptan)",
            severity=InteractionSeverity.CONTRAINDICATED,
            description="Risk of prolonged vasospasm and ischemia; 24-hour washout required",
            mechanism="Both are vasoconstrictors acting on 5-HT receptors; additive vasoconstrictor effects",
            clinical_effects=[
                "Prolonged vasospasm",
                "Coronary ischemia/infarction",
                "Peripheral ischemia (cold, pale extremities)",
                "Cerebral ischemia",
                "Severe hypertension"
            ],
            recommendations=[
                "CONTRAINDICATED within 24 hours of each other",
                "Wait 24 hours after ergotamine before taking triptan",
                "Wait 24 hours after triptan before taking ergotamine",
                "Choose one class or the other, not both",
                "Educate patient on strict 24-hour separation",
                "Consider preventive therapy to reduce acute medication use"
            ],
            references="Headache 2008;48:3-5; Triptan Prescribing Information 2024"
        )

        # Interaction 8: Propranolol + Rizatriptan
        interactions[("propranolol", "rizatriptan")] = DrugInteraction(
            drug1="Propranolol",
            drug2="Rizatriptan",
            severity=InteractionSeverity.MODERATE,
            description="Propranolol increases rizatriptan plasma concentration",
            mechanism="Propranolol inhibits MAO-A, reducing rizatriptan first-pass metabolism",
            clinical_effects=[
                "Increased rizatriptan AUC (70% increase)",
                "Enhanced triptan effects (beneficial and adverse)",
                "Increased risk of triptan adverse effects: dizziness, somnolence, asthenia",
                "Potential for increased cardiovascular effects"
            ],
            recommendations=[
                "Reduce rizatriptan dose from 10mg to 5mg when used with propranolol",
                "Maximum rizatriptan dose: 5mg per dose, 10mg per 24 hours",
                "Monitor for excessive triptan effects",
                "Alternative: use different triptan (sumatriptan not affected)",
                "If using for migraine prophylaxis, consider non-beta-blocker alternatives"
            ],
            references="J Clin Pharmacol 1999;39:192; Rizatriptan Prescribing Information 2024"
        )

        # Interaction 9: Topiramate + Acetazolamide
        interactions[("topiramate", "acetazolamide")] = DrugInteraction(
            drug1="Topiramate",
            drug2="Carbonic Anhydrase Inhibitors (Acetazolamide, Zonisamide)",
            severity=InteractionSeverity.MODERATE,
            description="Increased risk of metabolic acidosis and kidney stones",
            mechanism="Both inhibit carbonic anhydrase; additive effects on bicarbonate loss and urinary pH",
            clinical_effects=[
                "Metabolic acidosis (decreased serum bicarbonate <17 mEq/L)",
                "Nephrolithiasis (kidney stones) - risk increased 2-4 fold",
                "Hypercalciuria",
                "Bone demineralization with chronic use"
            ],
            recommendations=[
                "Avoid combination if possible",
                "If used together: monitor serum bicarbonate every 3-6 months",
                "Increase fluid intake to 2-3 liters/day",
                "Consider potassium citrate supplementation (alkalinizes urine, prevents stones)",
                "Monitor for symptoms: fatigue, anorexia, hyperventilation",
                "Baseline and periodic renal ultrasound if high risk"
            ],
            references="Epilepsia 2000;41(Suppl 1):S61; Kidney Int 2006;70:1937"
        )

        # Interaction 10: Lithium + NSAIDs
        interactions[("lithium", "ibuprofen")] = DrugInteraction(
            drug1="Lithium",
            drug2="NSAIDs (Ibuprofen, Naproxen, Indomethacin)",
            severity=InteractionSeverity.MODERATE,
            description="NSAIDs reduce lithium renal clearance, increasing lithium levels",
            mechanism="NSAIDs inhibit prostaglandin synthesis, reducing renal blood flow and glomerular filtration rate, decreasing lithium excretion",
            clinical_effects=[
                "Lithium toxicity: tremor, confusion, ataxia, dysarthria",
                "GI symptoms: nausea, vomiting, diarrhea",
                "Severe toxicity: seizures, coma, renal failure, arrhythmias",
                "Lithium level increase of 20-60%"
            ],
            recommendations=[
                "Avoid NSAIDs if possible; use acetaminophen for pain/fever",
                "If NSAID necessary: use sulindac or aspirin (less effect on lithium)",
                "Monitor lithium levels weekly when starting/stopping NSAID",
                "Reduce lithium dose by 25-50% when adding NSAID",
                "Monitor renal function",
                "Educate patient on lithium toxicity symptoms"
            ],
            references="J Clin Psychiatry 2002;63:1134; Am J Psychiatry 1998;155:1465"
        )

        # Interaction 11: Gabapentin + Opioids
        interactions[("gabapentin", "morphine")] = DrugInteraction(
            drug1="Gabapentin/Pregabalin",
            drug2="Opioids (Morphine, Oxycodone, Hydrocodone)",
            severity=InteractionSeverity.SEVERE,
            description="Additive CNS depression and respiratory depression risk",
            mechanism="Both agents cause CNS depression through different mechanisms (GABA modulation vs mu-opioid receptor activation); additive sedative effects",
            clinical_effects=[
                "Severe sedation and somnolence",
                "Respiratory depression (dose-dependent)",
                "Increased risk of overdose death (2-fold increase)",
                "Dizziness, ataxia, confusion",
                "Falls risk in elderly"
            ],
            recommendations=[
                "Use combination with caution; consider alternative analgesics first",
                "Start both agents at lowest effective dose",
                "Slow titration with close monitoring",
                "Avoid in patients with sleep apnea or respiratory compromise",
                "Educate patient on respiratory depression signs",
                "Consider naloxone prescription for home rescue",
                "Regular reassessment of continued need for both medications"
            ],
            references="FDA Drug Safety Communication 2019; Br J Clin Pharmacol 2019;85:291"
        )

        # Interaction 12: Metoclopramide + Antipsychotics
        interactions[("metoclopramide", "haloperidol")] = DrugInteraction(
            drug1="Metoclopramide",
            drug2="Antipsychotics (Haloperidol, Risperidone, Olanzapine)",
            severity=InteractionSeverity.MODERATE,
            description="Increased risk of extrapyramidal symptoms and tardive dyskinesia",
            mechanism="Both agents block dopamine D2 receptors in basal ganglia; additive dopamine antagonism",
            clinical_effects=[
                "Extrapyramidal symptoms: dystonia, akathisia, parkinsonism",
                "Tardive dyskinesia (potentially irreversible)",
                "Neuroleptic malignant syndrome (rare but life-threatening)",
                "QTc prolongation"
            ],
            recommendations=[
                "Avoid combination if possible",
                "Use lowest effective dose and shortest duration if combination necessary",
                "Monitor for EPS symptoms at each visit",
                "Consider alternatives: ondansetron, domperidone (less CNS penetration)",
                "Anticholinergics (benztropine) for EPS treatment",
                "Discontinue both agents if tardive dyskinesia develops"
            ],
            references="Drug Saf 2004;27:1043; Mov Disord 2013;28:863"
        )

        # Interaction 13: Amitriptyline + Tramadol
        interactions[("amitriptyline", "tramadol")] = DrugInteraction(
            drug1="Tricyclic Antidepressants (Amitriptyline, Nortriptyline)",
            drug2="Tramadol",
            severity=InteractionSeverity.SEVERE,
            description="Increased risk of seizures and serotonin syndrome",
            mechanism="TCAs lower seizure threshold; tramadol has pro-convulsant effects and serotonergic activity; both inhibit serotonin/norepinephrine reuptake",
            clinical_effects=[
                "Increased seizure risk (up to 1% with combination)",
                "Serotonin syndrome (see SSRI + triptan interaction)",
                "Additive anticholinergic effects: urinary retention, confusion, tachycardia",
                "Excessive sedation"
            ],
            recommendations=[
                "Avoid combination if possible",
                "Alternative analgesics: NSAIDs, acetaminophen, non-tramadol opioids",
                "If used together: use lowest doses, monitor closely",
                "Screen for seizure risk factors (history of seizures, head trauma, CNS infection)",
                "Educate patient on seizure and serotonin syndrome warning signs",
                "Consider alternative antidepressant (SSRI has lower seizure risk)"
            ],
            references="Seizure 2005;14:129; Psychosomatics 2010;51:239"
        )

        # Interaction 14: Phenytoin + Carbamazepine (bidirectional)
        interactions[("phenytoin", "carbamazepine")] = DrugInteraction(
            drug1="Phenytoin",
            drug2="Carbamazepine",
            severity=InteractionSeverity.MODERATE,
            description="Complex bidirectional enzyme induction affecting both drug levels",
            mechanism="Both are CYP3A4 inducers and substrates; mutual enzyme induction reduces plasma levels of both drugs",
            clinical_effects=[
                "Decreased phenytoin levels (20-50% reduction)",
                "Decreased carbamazepine levels (variable)",
                "Increased risk of seizure breakthrough",
                "Carbamazepine-10,11-epoxide accumulation (toxic metabolite)",
                "Paradoxically can cause phenytoin toxicity initially due to competition"
            ],
            recommendations=[
                "Monitor both drug levels closely (baseline, then every 2-4 weeks initially)",
                "Anticipate need for dose increases (phenytoin 25-50%, carbamazepine 20-30%)",
                "Monitor for seizure control and toxicity symptoms",
                "Consider therapeutic drug monitoring guided dosing",
                "Alternative: use non-interacting antiepileptic (levetiracetam, lacosamide)",
                "Monitor CBC for additive bone marrow suppression risk"
            ],
            references="Ther Drug Monit 1986;8:387; Epilepsy Res 1996;26:151"
        )

        return interactions

    def check_drug_interactions(self, medications: List[str]) -> List[Dict[str, Any]]:
        """
        Check for drug interactions among a list of medications

        Args:
            medications: List of medication names (case-insensitive)

        Returns:
            List of dictionaries containing interaction details with:
                - drug1: First drug name
                - drug2: Second drug name
                - severity: Interaction severity level
                - description: Brief description
                - mechanism: Mechanism of interaction
                - clinical_effects: List of potential clinical effects
                - recommendations: List of clinical recommendations
                - references: Medical literature references

        Examples:
            >>> kb = NeuroMedicalKnowledge()
            >>> kb.check_drug_interactions(["warfarin", "aspirin"])
            [{'severity': 'severe', 'drug1': 'Warfarin', 'drug2': 'Aspirin', ...}]
        """

        if not medications or len(medications) == 0:
            return []

        interactions_found = []
        # Deduplicate and normalize medications (case-insensitive, whitespace stripped)
        medications_lower = list(set(med.lower().strip() for med in medications))

        # Check all pairwise combinations
        for i, med1 in enumerate(medications_lower):
            for med2 in medications_lower[i+1:]:
                # Check both directions in interaction database
                interaction = self._find_interaction(med1, med2)

                if interaction:
                    interactions_found.append({
                        "drug1": interaction.drug1,
                        "drug2": interaction.drug2,
                        "severity": interaction.severity.value,
                        "description": interaction.description,
                        "mechanism": interaction.mechanism,
                        "clinical_effects": interaction.clinical_effects,
                        "recommendations": interaction.recommendations,
                        "references": interaction.references
                    })

        # Sort by severity (contraindicated > severe > moderate > minor)
        severity_order = {
            InteractionSeverity.CONTRAINDICATED.value: 0,
            InteractionSeverity.SEVERE.value: 1,
            InteractionSeverity.MODERATE.value: 2,
            InteractionSeverity.MINOR.value: 3
        }

        interactions_found.sort(key=lambda x: severity_order.get(x["severity"], 999))

        return interactions_found

    def _find_interaction(self, drug1_lower: str, drug2_lower: str) -> Optional[DrugInteraction]:
        """
        Find interaction between two drugs in database

        Args:
            drug1_lower: First drug name (lowercase)
            drug2_lower: Second drug name (lowercase)

        Returns:
            DrugInteraction object if found, None otherwise
        """
        # Check exact match
        if (drug1_lower, drug2_lower) in self._interaction_database:
            return self._interaction_database[(drug1_lower, drug2_lower)]
        elif (drug2_lower, drug1_lower) in self._interaction_database:
            return self._interaction_database[(drug2_lower, drug1_lower)]

        # Check if drug name is contained in interaction drug names (partial match)
        for (db_drug1, db_drug2), interaction in self._interaction_database.items():
            if (drug1_lower in db_drug1 or db_drug1 in drug1_lower) and \
               (drug2_lower in db_drug2 or db_drug2 in drug2_lower):
                return interaction
            elif (drug2_lower in db_drug1 or db_drug1 in drug2_lower) and \
                 (drug1_lower in db_drug2 or db_drug2 in drug1_lower):
                return interaction

        return None

    def get_treatment_guidelines(self, condition: str) -> List[str]:
        """
        Get evidence-based treatment guidelines for a neurological condition

        Args:
            condition: Condition name (case-insensitive)

        Returns:
            List of treatment guideline strings

        Examples:
            >>> kb = NeuroMedicalKnowledge()
            >>> kb.get_treatment_guidelines("migraine")
            ['Consider triptans...', 'Evaluate need for prophylactic therapy...']
        """

        if not condition:
            return ["Consult current clinical guidelines"]

        condition_lower = condition.lower()

        # Check for exact or partial match in guidelines
        for key, guidelines in self.treatment_guidelines.items():
            if key in condition_lower or condition_lower in key:
                return guidelines

        return ["Consult current clinical guidelines for this condition"]

    def get_interaction_severity_stats(self) -> Dict[str, int]:
        """
        Get statistics on interaction severities in database

        Returns:
            Dictionary with counts for each severity level
        """
        stats = {
            "contraindicated": 0,
            "severe": 0,
            "moderate": 0,
            "minor": 0,
            "total": len(self._interaction_database)
        }

        for interaction in self._interaction_database.values():
            severity = interaction.severity.value
            if severity in stats:
                stats[severity] += 1

        return stats

    def search_drug_in_database(self, drug_name: str) -> List[str]:
        """
        Search for all interactions involving a specific drug

        Args:
            drug_name: Drug name to search (case-insensitive)

        Returns:
            List of drug names that interact with the queried drug
        """
        drug_lower = drug_name.lower().strip()
        interacting_drugs = []

        for (drug1, drug2), interaction in self._interaction_database.items():
            if drug_lower in drug1 or drug1 in drug_lower:
                if interaction.drug2 not in interacting_drugs:
                    interacting_drugs.append(interaction.drug2)
            elif drug_lower in drug2 or drug2 in drug_lower:
                if interaction.drug1 not in interacting_drugs:
                    interacting_drugs.append(interaction.drug1)

        return sorted(interacting_drugs)
