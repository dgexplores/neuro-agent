# NeuroAgent MVP Roadmap - MoSCoW Prioritization

## Overview
This document breaks down NeuroAgent's three core features into Minimum Viable Product (MVP) deliverables using MoSCoW prioritization method:
- **Must Have**: Critical for MVP launch
- **Should Have**: Important but not vital for initial release
- **Could Have**: Desirable but can be deferred
- **Won't Have**: Out of scope for MVP

---

## Feature 1: Multi-Modal Diagnosis (多模態診斷)

### Must Have 🔴
1. **Text-Based Symptom Input**
   - Simple form for chief complaint entry
   - Basic symptom checklist (15-20 common neurological symptoms)
   - Free-text notes field
   - Required: Age, gender, symptom duration
   - **Deliverable**: Functional symptom input form
   - **Acceptance**: User can input symptoms and receive AI response

2. **Basic Differential Diagnosis Generation**
   - Integration with AWS Bedrock (Claude 3 Sonnet)
   - Top 3 differential diagnoses with confidence scores
   - Plain text explanation for each diagnosis
   - **Deliverable**: AI-powered diagnosis suggestions
   - **Acceptance**: Returns 3 diagnoses within 5 seconds

3. **Medical History Input**
   - Checklist for past medical conditions (10 common conditions)
   - Current medications list (free text)
   - Allergies field
   - **Deliverable**: Structured history capture
   - **Acceptance**: History data incorporated into AI prompt

4. **Basic Vital Signs**
   - Blood pressure, heart rate, temperature fields
   - Input validation (numeric ranges)
   - **Deliverable**: Vital signs form
   - **Acceptance**: Vital signs included in diagnosis context

### Should Have 🟡
5. **Advanced Symptom Assessment**
   - NIHSS (National Institutes of Health Stroke Scale) calculator
   - GCS (Glasgow Coma Scale) calculator
   - Symptom severity ratings (1-10)
   - Temporal pattern selection (acute, chronic, intermittent)
   - **Deliverable**: Clinical scoring tools
   - **Acceptance**: Scores auto-calculated and included in diagnosis

6. **Lab Results Input**
   - Common neurological lab values (CBC, metabolic panel)
   - Structured data entry with reference ranges
   - Abnormal value highlighting
   - **Deliverable**: Lab results form with validation
   - **Acceptance**: Lab data influences diagnostic suggestions

7. **Image Upload Interface**
   - Support for JPEG/PNG uploads (CT/MRI scans)
   - S3 storage integration
   - Basic image preview
   - **Deliverable**: File upload to S3
   - **Acceptance**: Images stored and linked to case

8. **Enhanced Diagnosis Presentation**
   - Confidence score visualization (progress bars)
   - Red flags and warning signs highlighted
   - Evidence citations (medical literature references)
   - **Deliverable**: Rich diagnosis results UI
   - **Acceptance**: Results displayed with visual hierarchy

### Could Have 🟢
9. **AI Image Analysis**
   - AWS Rekognition Medical integration
   - Automated abnormality detection in CT/MRI
   - Computer vision annotations
   - **Deliverable**: AI-powered image interpretation
   - **Acceptance**: Image findings included in diagnosis

10. **Multi-Language Support**
    - Traditional Chinese (繁體中文) interface
    - Bilingual medical terminology
    - Language toggle switch
    - **Deliverable**: Chinese UI translation
    - **Acceptance**: All labels and messages in Chinese

11. **Voice Input**
    - Speech-to-text for symptom description
    - AWS Transcribe Medical integration
    - **Deliverable**: Voice recording button
    - **Acceptance**: Voice converted to text in symptom field

12. **Timeline Visualization**
    - Symptom progression timeline
    - Interactive date/time picker
    - Visual representation of symptom evolution
    - **Deliverable**: Timeline component
    - **Acceptance**: Chronological view of symptom history

### Won't Have ⚪
- Real-time video consultation
- Integration with wearable devices
- 3D brain imaging visualization
- Genetic data analysis
- Telemedicine appointment scheduling

---

## Feature 2: Drug Interaction Checking (藥物交互檢查)

### Must Have 🔴
1. **Basic Drug Input**
   - Searchable drug name field (autocomplete)
   - Taiwan FDA approved drugs database (top 200 neurological drugs)
   - Current medications list
   - **Deliverable**: Drug search and selection
   - **Acceptance**: User can add multiple drugs to list

2. **Critical Interaction Detection**
   - Check for severe (contraindicated) interactions
   - Database of 50+ critical neurological drug pairs
   - Alert modal for dangerous combinations
   - **Deliverable**: Real-time interaction warnings
   - **Acceptance**: Critical interactions flagged immediately

3. **Basic Safety Recommendations**
   - Contraindications (pregnancy, renal/hepatic impairment)
   - Standard dosing information
   - Common side effects list
   - **Deliverable**: Drug safety information panel
   - **Acceptance**: Safety info displayed for each drug

### Should Have 🟡
4. **Moderate Interaction Detection**
   - Moderate severity interactions (require monitoring)
   - Drug-disease interactions
   - Dosage adjustment recommendations
   - **Deliverable**: Tiered interaction warnings
   - **Acceptance**: 3-tier severity system (critical/moderate/minor)

5. **Alternative Drug Suggestions**
   - AI-generated safer alternatives
   - Therapeutic equivalents
   - Reasoning for each suggestion
   - **Deliverable**: Alternative medication recommendations
   - **Acceptance**: 2-3 alternatives per problematic drug

6. **Allergy Cross-Reactivity**
   - Check drug allergies against new prescriptions
   - Cross-reactivity warnings (e.g., penicillin allergy)
   - **Deliverable**: Allergy checking logic
   - **Acceptance**: Allergies prevent contraindicated drugs

7. **Interaction Severity Scoring**
   - Numerical risk score (0-100)
   - Color-coded warnings (red/yellow/green)
   - Explanation of risk factors
   - **Deliverable**: Risk scoring algorithm
   - **Acceptance**: Each interaction has severity score

### Could Have 🟢
8. **Comprehensive Drug Database**
   - Full Taiwan FDA database (5000+ drugs)
   - Over-the-counter medications
   - Herbal supplements and TCM
   - **Deliverable**: Extended drug database
   - **Acceptance**: 90%+ drug coverage

9. **Pharmacokinetic Details**
   - Absorption, distribution, metabolism, excretion (ADME) data
   - Half-life and peak concentration
   - Food interaction warnings
   - **Deliverable**: Detailed pharmacology info
   - **Acceptance**: ADME data displayed for each drug

10. **Personalized Dosing**
    - Dosing calculators based on age/weight/renal function
    - Pediatric and geriatric adjustments
    - **Deliverable**: Dosing calculator widget
    - **Acceptance**: Personalized dose recommendations

11. **Drug History Tracking**
    - Historical medication list
    - Adverse reaction documentation
    - Medication adherence notes
    - **Deliverable**: Medication history timeline
    - **Acceptance**: Past medications viewable with dates

### Won't Have ⚪
- Real-time pharmacy inventory integration
- E-prescribing functionality
- Insurance formulary checking
- Medication reminder system
- Drug cost comparison

---

## Feature 3: Case Management (病例管理)

### Must Have 🔴
1. **Create New Case**
   - Anonymous patient ID generation (no PHI in MVP)
   - Case creation timestamp
   - Assigned case ID (UUID)
   - **Deliverable**: Case creation endpoint
   - **Acceptance**: New cases stored in DynamoDB

2. **Basic Case Storage**
   - Save patient symptoms, history, vitals
   - Store AI diagnosis results
   - DynamoDB table structure
   - **Deliverable**: Case data persistence
   - **Acceptance**: Cases retrievable by case ID

3. **Case List View**
   - Simple table/list of recent cases
   - Display: case ID, date, chief complaint
   - Basic search by case ID
   - **Deliverable**: Case listing page
   - **Acceptance**: Shows last 20 cases

4. **Case Detail View**
   - Full case information display
   - All input data and AI outputs
   - Diagnosis results and recommendations
   - **Deliverable**: Case detail page
   - **Acceptance**: Complete case info displayed

### Should Have 🟡
5. **Case Search and Filter**
   - Search by symptoms, diagnosis, date range
   - Filter by urgency level
   - Sort by date/relevance
   - **Deliverable**: Search and filter UI
   - **Acceptance**: Cases filtered in <2 seconds

6. **Case Updates and Notes**
   - Add follow-up notes to existing cases
   - Track case progression
   - Note timestamps and author
   - **Deliverable**: Case update functionality
   - **Acceptance**: Notes appended to case history

7. **Case Status Management**
   - Status workflow (open → in-progress → resolved)
   - Visual status indicators
   - Status change history
   - **Deliverable**: Case status system
   - **Acceptance**: Status tracked through lifecycle

8. **Basic Analytics**
   - Total cases count
   - Most common diagnoses
   - Average case resolution time
   - **Deliverable**: Dashboard with 3-5 KPIs
   - **Acceptance**: Analytics refresh daily

### Could Have 🟢
9. **Advanced Search**
   - Full-text search across all case fields
   - Fuzzy matching for symptom terms
   - Elasticsearch integration
   - **Deliverable**: Elasticsearch-powered search
   - **Acceptance**: Searches return results in <1 second

10. **Case Tagging and Categorization**
    - Custom tags (e.g., "stroke", "migraine")
    - Tag-based filtering
    - Tag cloud visualization
    - **Deliverable**: Tagging system
    - **Acceptance**: Cases tagged and filterable by tags

11. **Export Functionality**
    - Export case to PDF report
    - CSV export for bulk cases
    - HL7/FHIR format export
    - **Deliverable**: Export feature
    - **Acceptance**: PDF generated with all case data

12. **Collaboration Features**
    - Case sharing (secure link)
    - Comments and discussions
    - @mention notifications
    - **Deliverable**: Collaborative case review
    - **Acceptance**: Multiple users can view/comment

13. **Case Templates**
    - Pre-filled templates for common conditions
    - Template library (stroke, migraine, seizure)
    - Custom template creation
    - **Deliverable**: Template system
    - **Acceptance**: Cases creatable from templates

### Won't Have ⚪
- EHR integration (Epic/Cerner)
- PACS integration for imaging
- Billing and coding features
- Appointment scheduling
- Patient portal access
- Mobile app (MVP is web-only)

---

## MVP Development Phases

### Phase 1: Core Foundation (Weeks 1-2)
**Must Have items only**
- Multi-modal diagnosis: Items 1-4 (text input, basic diagnosis, history, vitals)
- Drug interaction: Items 1-3 (drug input, critical interactions, safety info)
- Case management: Items 1-4 (create, store, list, view cases)
- **Goal**: End-to-end workflow functional

### Phase 2: Enhanced Functionality (Weeks 3-4)
**Should Have items**
- Multi-modal diagnosis: Items 5-8 (scoring tools, labs, images, enhanced UI)
- Drug interaction: Items 4-7 (moderate interactions, alternatives, allergies, scoring)
- Case management: Items 5-8 (search, updates, status, analytics)
- **Goal**: Production-ready MVP

### Phase 3: Competitive Differentiation (Post-MVP)
**Could Have items**
- Advanced AI features (image analysis, voice input)
- Comprehensive data (full drug database, TCM)
- Power user features (advanced search, export, collaboration)
- **Goal**: Market differentiation

---

## Success Criteria for MVP Launch

### Functional Requirements
- ✅ User can input symptoms and receive 3 differential diagnoses
- ✅ Critical drug interactions detected and warned
- ✅ Cases saved and retrievable
- ✅ All core workflows take <10 seconds
- ✅ No critical bugs in happy path

### Non-Functional Requirements
- ✅ 95%+ uptime during demo period
- ✅ HIPAA-compliant data handling (no PHI in MVP)
- ✅ Mobile-responsive UI (works on tablets)
- ✅ Accessible (WCAG 2.1 Level A minimum)
- ✅ API response time <3 seconds (p95)

### Business Requirements
- ✅ Demonstrates all 3 core features
- ✅ Addresses all 3 user stories (neurologist, nurse, IT admin)
- ✅ AWS Bedrock integration showcased
- ✅ Ready for hackathon demo presentation
- ✅ Deployable to AWS with CDK

---

## Risk Mitigation

### High-Risk Items
1. **AWS Bedrock API Latency**
   - Mitigation: Implement streaming responses, loading states
   - Fallback: Pre-cache common diagnosis patterns

2. **Drug Database Completeness**
   - Mitigation: Start with top 200 drugs, expand iteratively
   - Fallback: Manual drug entry if not in autocomplete

3. **Image Upload/Storage Costs**
   - Mitigation: Defer to "Should Have" phase, use S3 lifecycle policies
   - Fallback: Remove image feature if budget constrained

### Medium-Risk Items
4. **DynamoDB Query Performance**
   - Mitigation: Design efficient indexes, use pagination
   - Fallback: In-memory caching for recent cases

5. **Medical Accuracy Concerns**
   - Mitigation: Include prominent disclaimers, require physician review
   - Fallback: Position as "decision support" not "diagnosis"

---

## Dependencies

### External Services
- AWS Bedrock (Claude 3 Sonnet) - Must Have
- AWS DynamoDB - Must Have
- AWS S3 - Should Have
- AWS Rekognition Medical - Could Have
- Taiwan FDA Drug Database API - Should Have

### Technical Skills Required
- Python (FastAPI) - Must Have
- React 18 - Must Have
- AWS CDK - Must Have
- Medical domain knowledge - Should Have
- DevOps/deployment - Should Have

---

**Document Version**: 1.0
**Last Updated**: October 12, 2025
**Author**: Claude Code with NeuroAgent team
**Purpose**: AWS AI Agent Global Hackathon MVP Planning
