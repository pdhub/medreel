# AI Medical Content Studio

**An AI-powered, multi-agent video production system for medical professionals.**

Transform raw doctor recordings into professionally edited, regional-language medical explainer videos using specialized AI agents, media-processing tools and human quality control.

---

## 1. Problem Statement

Medical professionals have valuable knowledge and expertise but often lack the time, technical skills or resources to consistently produce high-quality educational video content.

Creating a professional medical explainer video involves several activities:

- Reviewing and understanding raw video recordings.
- Identifying useful segments and removing unnecessary footage.
- Creating engaging introductions and hooks.
- Transcribing spoken content.
- Editing cuts, pauses and transitions.
- Improving lighting, framing and audio quality.
- Generating synchronized subtitles.
- Translating and localizing content into regional languages and dialects.
- Creating medical diagrams and illustrations that explain the spoken content.
- Adding titles, captions, animations and branding.
- Rendering and delivering the final video.

These tasks are repetitive, time-consuming and require multiple skills.

Our objective is to automate this production process using a coordinated multi-agent AI system.

### The proposed solution

A doctor uploads a raw video.

Our system analyzes the video, understands its spoken content, plans the editing process, creates relevant visual assets, generates localized captions, processes the footage and produces a professionally edited video.

The final video is delivered to the doctor for approval and publishing.

**Input:** Raw doctor-recorded video.

**Output:** Professionally edited, medically reviewed, regional-language explainer video ready for social media publishing.

---

## 2. Product Vision

Build an AI-native content production system where specialized agents perform the responsibilities of a professional video production team.

The system should be capable of:

1. Understanding the content of a medical recording.
2. Identifying important information and structuring it into a coherent narrative.
3. Detecting unnecessary segments, pauses and mistakes.
4. Generating engaging hooks and introductions without changing the doctor's intended meaning.
5. Producing synchronized captions in regional languages.
6. Generating medical illustrations and diagrams based on the spoken content.
7. Improving video lighting, framing and audio quality.
8. Creating consistent branding, transitions and motion graphics.
9. Evaluating the final video against production and medical accuracy requirements.
10. Delivering the finished video to the doctor.

The long-term objective is to operate an AI-powered medical content production agency with minimal manual intervention.

---

## 3. High-Level Workflow

```text
             DOCTOR
                |
                |
        Upload Raw Video
                |
                v
       VIDEO INTAKE SERVICE
                |
                v
        MEDIA INSPECTION
                |
                v
       AI PRODUCTION MANAGER
                |
       +--------+---------+
       |        |         |
       v        v         v
   Content   Transcript  Video
   Analysis   Agent     Analysis
       |        |         |
       +--------+---------+
                |
                v
       CONTENT UNDERSTANDING
                |
                v
        EDITING PLANNER
                |
       +--------+----------+
       |        |          |
       v        v          v
     Hook    Localization  Medical
    Agent      Agent      Diagram
                           Agent
       |        |          |
       +--------+----------+
                |
                v
        VIDEO PRODUCTION
                |
       +--------+----------+
       |        |          |
       v        v          v
     Cutting  Captions   Lighting &
     & Timing  & Text    Framing
       |        |          |
       +--------+----------+
                |
                v
         VIDEO RENDERING
                |
                v
          QUALITY CONTROL
                |
          +-----+------+
          |            |
          v            v
        Failed       Passed
          |            |
          v            v
      Correction    HUMAN REVIEW
          |            |
          +----->------+
                       |
                       v
                DOCTOR APPROVAL
                       |
                       v
                 FINAL VIDEO
                       |
                       v
                    DELIVERY
```

---

## 4. Multi-Agent Architecture

The system will use specialized agents coordinated through a central orchestrator.

Each agent will have a defined responsibility, structured inputs and outputs, access to specific tools and measurable evaluation criteria.

### 4.1 Production Manager / Supervisor Agent

**Responsibility:** Coordinate the complete video production workflow.

Responsibilities:

- Receive a new production request.
- Initialize the production job.
- Inspect workflow status.
- Delegate tasks to specialized agents.
- Maintain shared production state.
- Handle dependencies between agents.
- Retry failed operations where appropriate.
- Escalate unresolved problems to a human.
- Ensure all required production stages are completed.

The supervisor should not perform every task itself. It should coordinate specialized agents and deterministic processing services.

### 4.2 Video Analysis Agent

**Responsibility:** Understand the raw video.

Responsibilities:

- Inspect video metadata.
- Identify scene changes.
- Analyze video segments.
- Identify speaking sections and potential mistakes.
- Detect long pauses and unusable footage.
- Identify important visual moments.
- Generate a structured video analysis report.

Expected output:

- Video metadata.
- Segment timestamps.
- Scene descriptions.
- Potential cut points.
- Relevant visual observations.
- Editing recommendations.

### 4.3 Transcription Agent

**Responsibility:** Convert spoken content into timestamped text.

Responsibilities:

- Extract audio from the video.
- Transcribe speech.
- Identify the spoken language.
- Generate timestamped segments.
- Identify uncertain words.
- Preserve medical terminology.
- Produce structured transcript data.

Initial transcription engine: Whisper.

Expected output:

- Original transcript.
- Timestamped segments.
- Detected language.
- Confidence information where available.
- Uncertain terminology requiring review.

### 4.4 Content Understanding Agent

**Responsibility:** Understand the medical subject and structure the narrative.

Responsibilities:

- Analyze the transcript.
- Identify the primary medical topic.
- Extract important concepts.
- Identify explanations and examples.
- Identify repetitive or irrelevant sections.
- Organize the content into a logical sequence.
- Suggest opportunities for visual explanations.

For example, for a video about hypertension:

- Introduction to blood pressure.
- Explanation of systolic and diastolic pressure.
- Causes and risk factors.
- Potential complications.
- Measurement and prevention.

The agent must preserve the doctor's original clinical meaning.

### 4.5 Hook and Storytelling Agent

**Responsibility:** Improve viewer engagement and content structure.

Responsibilities:

- Identify the most interesting opening statement.
- Generate alternative hooks.
- Suggest an appropriate introduction.
- Identify sections that can be shortened.
- Improve narrative continuity.
- Recommend an effective closing statement.

The agent must not invent medical claims or introduce unsupported clinical statements.

Any proposed changes to spoken medical content require doctor approval.

### 4.6 Editing Planner Agent

**Responsibility:** Generate an executable editing plan.

This agent converts content analysis into a structured timeline.

Responsibilities:

- Select candidate segments.
- Identify unnecessary pauses.
- Suggest cuts and transitions.
- Recommend scene ordering.
- Identify important phrases for emphasis.
- Decide where diagrams and illustrations are needed.
- Specify titles and text overlays.
- Produce a timestamped editing specification.

Example:

```json
{
  "video_id": "video_001",
  "scenes": [
    {
      "start": 0,
      "end": 5,
      "type": "hook",
      "title": "Understanding Hypertension",
      "visual": "doctor_closeup"
    },
    {
      "start": 5,
      "end": 20,
      "type": "explanation",
      "title": "What is blood pressure?",
      "visual": "heart_and_arteries"
    },
    {
      "start": 20,
      "end": 35,
      "type": "medical_explanation",
      "title": "Systolic and Diastolic",
      "visual": "blood_pressure_diagram"
    }
  ]
}
```

The editing planner produces instructions. Actual media operations should be executed through deterministic tools.

### 4.7 Localization Agent

**Responsibility:** Generate regional-language versions of the video.

Initial language support:

- Assamese.
- Bengali.

Responsibilities:

- Translate captions into the target language.
- Preserve medical terminology.
- Adapt wording to natural regional speech.
- Avoid literal translations that sound unnatural.
- Maintain subtitle timing.
- Check spelling and grammar.
- Identify terms requiring doctor review.

Localization must preserve the original clinical meaning.

The system should support dialect-specific terminology and vocabulary rather than assuming that one translation works for every regional audience.

### 4.8 Medical Diagram Agent

**Responsibility:** Create educational visuals based on the medical concepts discussed in the video.

For a hypertension explainer, potential visuals include:

- Heart pumping blood.
- Artery cross-section.
- Blood pressure measurement.
- Systolic and diastolic pressure.
- Effects of hypertension on organs.

Responsibilities:

- Identify concepts that need visual explanation.
- Generate diagram specifications.
- Select appropriate visual styles.
- Generate or retrieve suitable illustrations.
- Associate illustrations with transcript timestamps.
- Produce assets for the rendering pipeline.

Medical illustrations must be educationally accurate and reviewed before delivery. Generated visuals must not introduce misleading anatomy or unsupported clinical information.

### 4.9 Video Processing Agent

**Responsibility:** Execute the editing plan.

Responsibilities:

- Remove unnecessary segments.
- Apply cuts.
- Reframe footage to vertical format.
- Improve brightness and contrast.
- Correct colour where appropriate.
- Normalize audio.
- Insert titles and graphics.
- Add transitions.
- Insert medical illustrations.
- Synchronize captions.
- Render the final video.

Primary tools:

- FFmpeg for media processing.
- Remotion for graphics, titles and compositions.

The actual editing operations should be deterministic wherever possible. The agent should select and configure operations rather than independently manipulating arbitrary media.

### 4.10 Quality Assurance Agent

**Responsibility:** Evaluate the final video before delivery.

Quality checks:

**Video quality**
- Correct resolution and aspect ratio.
- No black frames or missing footage.
- No unintended gaps.
- Correct scene ordering.
- Appropriate transitions.

**Audio quality**
- Speech is audible.
- No clipping.
- Audio and video remain synchronized.

**Caption quality**
- Correct spelling.
- Correct medical terminology.
- Proper subtitle synchronization.
- Correct regional-language rendering.

**Content quality**
- No unsupported medical claims.
- No accidental changes to clinical meaning.
- Medical diagrams correspond to the doctor's explanation.
- No missing important sections.

The QA agent should produce a structured report containing passed checks, failed checks and issues requiring human intervention.

---

## 5. Technology Stack

The initial implementation will prioritize tools already available in the development environment.

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python / FastAPI | API and application logic |
| Agent orchestration | LangGraph | Stateful multi-agent workflows |
| LLM | Pluggable LLM provider | Reasoning and structured outputs |
| Transcription | Whisper | Speech recognition |
| Media processing | FFmpeg | Editing, cropping, audio and encoding |
| Video inspection | ffprobe | Media metadata |
| Video composition | Remotion | Titles, diagrams and graphics |
| Experimental rendering | HyperFrames | Timeline-based video generation |
| Database | PostgreSQL | Customers and job state |
| Queue | Redis | Background processing |
| Storage | S3-compatible storage | Original and rendered videos |
| Monitoring | OpenTelemetry | Execution tracing and observability |

Technology choices should remain modular so that individual services can be replaced without redesigning the entire system.

---

## 6. Video Production Pipeline

Every production request should follow a defined sequence.

### Stage 1: Video Intake

- Receive the uploaded video.
- Validate file format and size.
- Store the original recording.
- Generate a unique production job.
- Inspect media metadata.
- Initialize workflow state.

### Stage 2: Media Understanding

- Extract audio.
- Transcribe speech.
- Analyze video segments.
- Identify scene boundaries.
- Identify relevant spoken content.
- Produce a structured transcript and video analysis.

### Stage 3: Content Planning

- Understand the medical topic.
- Structure the narrative.
- Suggest a hook.
- Identify unnecessary sections.
- Generate an editing timeline.
- Identify opportunities for medical diagrams.

### Stage 4: Localization

- Generate Assamese or Bengali captions.
- Adapt terminology to the target dialect.
- Preserve original timestamps.
- Validate subtitle formatting.
- Flag uncertain translations.

### Stage 5: Asset Generation

- Generate medical diagram specifications.
- Create titles and text overlays.
- Prepare illustrations.
- Prepare branding elements.
- Associate assets with video timestamps.

### Stage 6: Video Editing

- Apply cuts and transitions.
- Remove unnecessary pauses.
- Reframe footage.
- Improve lighting and colour.
- Normalize audio.
- Insert subtitles.
- Insert medical diagrams.
- Apply branding and animations.

### Stage 7: Rendering

- Generate the final video composition.
- Render using the selected video engine.
- Encode the final MP4.
- Store the output.

### Stage 8: Quality Assurance

- Inspect the rendered video.
- Validate subtitles.
- Validate audio synchronization.
- Check rendering errors.
- Evaluate medical content preservation.
- Generate a quality report.

### Stage 9: Human Approval and Delivery

- Present the rendered video for human review.
- Allow corrections.
- Obtain doctor approval.
- Deliver the final MP4.
- Maintain production history.

---

## 7. Workflow State Management

Video production is a long-running process. It must not depend on a single uninterrupted agent execution.

Every production job should have persistent state.

Suggested states:

```text
CREATED
  |
UPLOADED
  |
INSPECTING
  |
TRANSCRIBING
  |
ANALYZING
  |
PLANNING
  |
LOCALIZING
  |
GENERATING_ASSETS
  |
EDITING
  |
RENDERING
  |
QUALITY_CHECK
  |
HUMAN_REVIEW
  |
DOCTOR_APPROVAL
  |
DELIVERED
```

Failure states:

```text
FAILED
RETRY_PENDING
NEEDS_HUMAN_INTERVENTION
REJECTED
CANCELLED
```

Each stage should:

- Persist its inputs and outputs.
- Be independently executable.
- Support retries.
- Avoid duplicating completed work.
- Record execution time and cost.
- Maintain an audit trail.

The system should resume from the last successful checkpoint rather than restarting the complete production pipeline.

---

## 8. Engineering Principles

### Deterministic execution over unnecessary autonomy

Not every component needs to be an AI agent.

Use ordinary software for:

- File handling.
- Video encoding.
- Cropping and resizing.
- Subtitle synchronization.
- Audio normalization.
- Rendering.
- Database operations.
- Workflow status management.

Use agents where reasoning and contextual decisions are required.

### Human-in-the-loop

Medical content requires additional safeguards.

The system must not autonomously:

- Invent clinical statements.
- Change medical advice.
- Alter dosage or treatment information.
- Present generated diagrams as clinically validated.
- Publish videos without approval.

The doctor remains the authority on clinical accuracy.

### Evaluation-driven development

Every agent must have measurable acceptance criteria.

Maintain evaluation datasets for:

- Transcription accuracy.
- Medical terminology recognition.
- Assamese and Bengali translation quality.
- Caption synchronization.
- Editing plan quality.
- Medical content preservation.
- Diagram relevance.
- Final video quality.

Every prompt, model or workflow change should be tested against existing evaluations.

### Observability

Record:

- Agent inputs and outputs.
- Tool calls.
- Execution duration.
- Model usage.
- Token consumption.
- Errors and retries.
- Human corrections.
- Final quality scores.

Sensitive customer footage and medical information must not be unnecessarily exposed in logs.

---

## 9. Repository Structure

Initial proposed structure:

```text
medical-content-studio/
│
├── apps/
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   └── schemas/
│   │
│   └── web/
│
├── agents/
│   ├── supervisor/
│   ├── video_analysis/
│   ├── transcription/
│   ├── content_understanding/
│   ├── hook_generation/
│   ├── editing_planner/
│   ├── localization/
│   ├── medical_diagrams/
│   ├── video_processing/
│   └── quality_assurance/
│
├── workflows/
│   ├── production_graph.py
│   ├── state.py
│   ├── nodes.py
│   └── routing.py
│
├── services/
│   ├── storage/
│   ├── transcription/
│   ├── ffmpeg/
│   ├── rendering/
│   └── notifications/
│
├── media/
│   ├── templates/
│   ├── fonts/
│   ├── illustrations/
│   └── branding/
│
├── prompts/
│   ├── content_analysis/
│   ├── localization/
│   ├── editing/
│   └── quality/
│
├── evaluations/
│   ├── transcription/
│   ├── localization/
│   ├── medical_accuracy/
│   ├── editing/
│   └── rendering/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── end_to_end/
│
├── infrastructure/
│   ├── docker/
│   └── deployment/
│
├── docs/
│   ├── architecture.md
│   ├── agent_design.md
│   ├── workflow.md
│   └── evaluation_strategy.md
│
├── README.md
├── pyproject.toml
└── docker-compose.yml
```

This is the intended target structure. Implementation should remain incremental; empty directories and placeholder agents are not required at the beginning.

---

## 10. Development Roadmap

The project will be developed incrementally.

### Phase 1: Working Video Production Pipeline

**Objective:** Produce a complete edited video from a raw recording.

Implement:

- Video upload and storage.
- Media inspection.
- Whisper transcription.
- Timestamped subtitles.
- Basic content analysis.
- FFmpeg video processing.
- Remotion titles and graphics.
- Final video rendering.
- Manual quality review.

Success criterion:

A doctor can submit a video and receive a properly edited video through a functioning production pipeline.

### Phase 2: Intelligent Editing

**Objective:** Introduce AI-assisted editing decisions.

Implement:

- Video content analysis.
- Hook generation.
- Content segmentation.
- Editing plan generation.
- Automatic cut suggestions.
- Visual asset recommendations.
- Automated caption correction.

Success criterion:

The system can produce an editable, structured production plan with useful cuts and visual recommendations.

### Phase 3: Regional Language Production

**Objective:** Support regional medical content.

Initial languages:

- Assamese.
- Bengali.

Implement:

- Translation and localization.
- Regional terminology dictionaries.
- Dialect-aware phrasing.
- Subtitle quality evaluations.
- Medical terminology validation.

Success criterion:

The system produces readable, synchronized regional-language captions that preserve the doctor's intended meaning.

### Phase 4: Multi-Agent Orchestration

**Objective:** Introduce specialized agents and coordinated execution.

Implement:

- Supervisor agent.
- Specialized agent responsibilities.
- Shared workflow state.
- Conditional routing.
- Checkpointing.
- Retries and error recovery.
- Human approval interrupts.
- Agent tracing and evaluations.

Success criterion:

The production workflow can coordinate specialized agents and resume after failures without losing completed work.

### Phase 5: Production and Business Operations

**Objective:** Turn the system into a repeatable commercial service.

Implement:

- Customer management.
- Monthly production plans.
- Job tracking.
- Automated notifications.
- Delivery management.
- Usage and cost tracking.
- Quality reports.
- Operational analytics.

Success criterion:

Multiple doctors can submit jobs and receive consistent deliverables without requiring the founder to manually coordinate every production step.

---

## 11. Initial Product Constraints

The first version will focus on:

- Doctor-led educational videos.
- Short-form social media explainers.
- Assamese and Bengali localization.
- Vertical 1080 × 1920 output.
- Human-reviewed medical content.
- Human-approved final delivery.

Out of scope initially:

- AI-generated doctor avatars.
- Autonomous medical advice.
- Automated diagnosis.
- Fully autonomous publishing.
- Complex 3D medical animation.
- Support for every Indian language.
- Building a proprietary video editing engine.

---

## 12. Definition of Success

The system will be considered successful when:

1. A doctor can upload a raw video.
2. The system can analyze and transcribe it.
3. An editing plan is generated.
4. Relevant hooks and scene suggestions are produced.
5. Regional-language captions are generated.
6. Relevant medical diagrams are created or selected.
7. Video cuts, framing, lighting and audio are processed.
8. A final video is rendered.
9. Quality checks are completed.
10. A human approves the final output.
11. The edited video is delivered to the doctor.

Business success will additionally be measured through:

- Production cost per video.
- Average production turnaround.
- Founder time per customer.
- Percentage of automated production steps.
- Caption error rate.
- Revision rate.
- Customer retention.
- Gross margin.

---

## 13. Guiding Principle

**We are not building another video editor. We are building an AI-powered medical content production workforce.**

The objective is to convert a doctor's raw knowledge into high-quality, localized, educational video content through specialized AI agents, deterministic media-processing systems and human oversight.

The system should become increasingly autonomous as we learn from real production workflows, customer feedback and evaluation results.

Our long-term vision is a regional-language medical content operations platform that can serve hundreds of medical professionals without requiring a proportional increase in manual production effort.