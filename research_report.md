# SynchroTwin-AR: Deep Research Report

## 1. Introduction to SynchroTwin-AR

SynchroTwin-AR is an ambitious project aiming to make pre-verbal understanding visible and trainable through a dyadic synchrony score in real-time, mirrored in Augmented Reality (AR). The system compares what individuals tend to do (Default Narrative, DN) with what they actually did (Observed Narrative, ON) and offers counter-bias nudges. The ultimate goal is to help pairs learn to co-create better with more clarity and less drift over time.

This report details the deep research conducted into the core concepts, technologies, and architectural components outlined in the Preliminary Design Review (PDR) and Product Requirements (PRD) document for SynchroTwin-AR. The objective is to provide a comprehensive understanding of the underlying principles and technical considerations necessary for the successful implementation of this complex system.

## 2. Core Concepts and Problem Statement

The project addresses the problem that pre-verbal understanding is invisible, bias can drift decisions away from intent, and teams often lack safe feedback loops to see and steer their synchrony. The core hypotheses are:

*   **H1 (Synchrony)**: Increasing non-verbal synchrony (breath/micro-motion/tempo) improves silent mutual understanding.
*   **H2 (Feedback)**: Closed-loop AR biofeedback increases Resonance (R(t)) compared to no feedback.
*   **H3 (Agency)**: Showing DN↔ON divergence and offering counter-bias steps reduces bias divergence week-over-week.

The North-Star Metric for success is the mean improvement in Resonance during tasks (ΔR) and reduction in policy drift (Δ_bias) with positive task outcomes.

## 3. Dyadic Synchrony Measurement (R(t))

The SynchroTwin-AR system relies heavily on the real-time computation and streaming of a 


Resonance (R(t)) score. This score is a fusion of several physiological and behavioral synchrony measures:

### 3.1 Phase-Locking Value (PLV)

**Concept:** Phase-Locking Value (PLV) is a widely used measure to quantify the synchronization between two signals, particularly in neuroscience for analyzing neural activity. It assesses the consistency of phase differences between two oscillating signals over time. PLV values range from 0 to 1, where 0 indicates no phase synchrony and 1 indicates perfect phase synchrony (i.e., the relative phase between the two signals is identical and constant).

**Application in SynchroTwin-AR:** In the context of SynchroTwin-AR, PLV will likely be applied to physiological signals that exhibit oscillatory behavior, such as respiratory rhythms or micro-movements. By calculating the PLV between two individuals' signals, the system can quantify their non-verbal synchrony in terms of phase alignment.

**Mathematical Formulation (as per document):**

$\mathrm{PLV}(t)=\Big|\frac{1}{N}\sum_{k=1}^{N} e^{i(\phi_a(t_k)-\phi_b(t_k))}\Big|$

Where:
*   $\phi_a(t_k)$ and $\phi_b(t_k)$ are the phases of signals 'a' and 'b' at time point $t_k$.
*   $N$ is the number of time points or samples.
*   $i$ is the imaginary unit.

**Key Characteristics:**
*   **Range:** [0, 1]
*   **Interpretation:** Higher values indicate stronger phase synchrony.
*   **Advantages:** Relatively robust to amplitude changes and noise, focuses purely on phase relationships.
*   **Considerations:** Requires signals to have well-defined phases, often achieved through band-pass filtering to isolate specific frequency bands (e.g., for respiratory or micro-movement proxies).

### 3.2 Cross-Recurrence Quantification Analysis (CRQA)

**Concept:** Cross-Recurrence Quantification Analysis (CRQA) is a nonlinear correlational analysis technique used to identify and quantify recurrent patterns and synchronization between two different time series. It is an extension of Recurrence Quantification Analysis (RQA) and is particularly useful for analyzing complex, non-stationary, and non-linear data, such as behavioral or physiological time series in social interactions. CRQA works by constructing a cross-recurrence plot, which visually represents instances where the states of two time series are similar or 


close to each other at the same or different times. Key measures derived from CRQA include:

*   **Recurrence Rate (RR):** The density of recurrence points in the plot, indicating how often the two systems return to similar states.
*   **Determinism (DET):** The proportion of recurrence points that form diagonal lines, reflecting the predictability and deterministic structure in the coupled system.
*   **Laminarity (LAM):** The proportion of recurrence points that form vertical lines, indicating periods where one system is relatively static while the other changes.
*   **Trapping Time (TT):** The average length of vertical lines, representing the average time the systems remain in a recurrent state.

**Application in SynchroTwin-AR:** In SynchroTwin-AR, CRQA can be used to analyze the synchrony of discrete behavioral events or patterns, such as pause sequences in speech, gesture timings, or other micro-movements. By binarizing these events into time series, CRQA can quantify the deterministic and recurrent nature of their co-occurrence between two individuals, providing insights into their interactional synchrony.

**Key Characteristics:**
*   **Non-linear:** Suitable for complex, non-linear interactions.
*   **Event-based:** Can analyze synchrony of discrete events or categorical data.
*   **Robust to noise:** Less sensitive to noise compared to some linear measures.
*   **Provides detailed insights:** Offers various measures beyond simple correlation, revealing the structure of synchrony.

### 3.3 fNIRS Coherence

**Concept:** Functional Near-Infrared Spectroscopy (fNIRS) is a non-invasive neuroimaging technique that measures brain activity by detecting changes in blood oxygenation. When applied in a hyperscanning setup (simultaneously recording two or more individuals), fNIRS can be used to assess inter-brain synchrony, or 


brain-to-brain synchrony. Coherence, particularly wavelet coherence, is a common method used to quantify the functional connectivity and synchronization between fNIRS signals from different brains.

**Application in SynchroTwin-AR:** The document mentions fNIRS as an optional input for the Synchrony Engine. If fNIRS data is available, its coherence with another individual's fNIRS data would provide a direct measure of brain-to-brain synchrony, contributing to the overall R(t) score. This would add a neurophysiological layer to the synchrony assessment, complementing the behavioral and physiological measures.

**Key Characteristics:**
*   **Neurophysiological measure:** Directly assesses brain activity synchronization.
*   **Non-invasive:** Safe and suitable for various settings.
*   **Wavelet Coherence:** Often used to analyze fNIRS data, as it can capture frequency-dependent and time-varying synchronization.
*   **Contribution to R(t):** Provides a deeper, brain-level insight into dyadic synchrony.

### 3.4 Fusion of Synchrony Measures for R(t)

**Concept:** The SynchroTwin-AR system proposes a fusion approach to combine the individual synchrony measures (PLV, envelope correlation, CRQA, and fNIRS coherence) into a single Resonance score, R(t). This fusion is crucial for creating a comprehensive and robust measure of dyadic synchrony that integrates multiple facets of interaction.

**Mathematical Formulation (as per document):**

$R=\sigma(w_1\mathrm{PLV}+w_2 r_\text{env}+w_3 \mathrm{CRQA}n+w_4 C\text{fNIRS})$

Where:
*   $w_1, w_2, w_3, w_4$ are weights tuned via pilot studies (e.g., grid search).
*   $\sigma$ is a logistic function, mapping the weighted sum to a range between 0 and 1.
*   $r_\text{env}$ represents the envelope correlation.
*   $\mathrm{CRQA}n$ represents the normalized CRQA measure.
*   $C\text{fNIRS}$ represents the fNIRS coherence.

**Confidence Score:** The document also mentions a confidence score derived from SNR (Signal-to-Noise Ratio) and channel agreement. This confidence score is vital for understanding the reliability of the computed R(t) at any given moment, especially in real-world scenarios with potential sensor noise or data quality issues.

**Significance:** This fusion approach allows for a holistic assessment of synchrony, leveraging the strengths of different modalities. By weighting the contributions of each measure, the system can be optimized to reflect the most relevant aspects of synchrony for the specific application.

## 4. Augmented Reality (AR) Biofeedback

AR biofeedback is a critical component of SynchroTwin-AR, providing real-time visual cues to users based on their dyadic synchrony. This closed-loop feedback aims to increase Resonance (R(t)) and facilitate improved interaction.

### 4.1 Visual Cues

The AR interface will utilize specific visual elements to convey the synchrony information:

*   **Two Orbs:** These likely represent the two individuals in the dyad, with their relative positions or movements reflecting aspects of their interaction.
*   **Interference Rings:** These rings could visually represent the interplay or 


overlap of their physiological or behavioral states.

### 4.2 Mapping of Visual Cues to Synchrony Parameters

The document specifies a precise mapping between the visual cues and the calculated synchrony parameters:

*   **Distance ↔ Phase Drift:** The spatial distance between the two orbs in AR could represent the phase drift between the individuals' signals. A smaller distance would indicate less phase drift and higher synchrony.
*   **Glow ↔ R:** The intensity or color of the glow emanating from the orbs could be mapped to the Resonance score (R). A brighter or more vibrant glow would indicate higher synchrony.
*   **Size ↔ Confidence:** The size of the orbs could represent the confidence score of the R(t) calculation. Larger orbs would indicate higher confidence in the synchrony measurement.
*   **Ring Rate ↔ dR/dt:** The rate or speed of the interference rings could be mapped to the derivative of R with respect to time (dR/dt), indicating the rate of change of synchrony. A faster ring rate might suggest rapid changes in synchrony.

**Significance:** This detailed mapping allows for intuitive and immediate feedback to the users, enabling them to visually perceive their synchrony levels and adjust their behavior accordingly. The real-time nature of this feedback is crucial for the closed-loop biofeedback mechanism.

## 5. System Architecture and Backend Services

The SynchroTwin-AR project outlines a sophisticated microservices-based architecture designed for real-time data processing, analysis, and delivery. The core components include data ingestion, a synchrony engine, bias mirror, digital twin, and various data storage solutions.

### 5.1 Data Ingestion and Streaming (Kafka/Redpanda)

**Concept:** The system relies on a robust messaging queue for high-throughput, low-latency data ingestion from various client devices (Web, Mobile, AR, BCI Edge). Apache Kafka and Redpanda are both leading distributed streaming platforms capable of handling real-time data feeds.

**Kafka vs. Redpanda:**

*   **Apache Kafka:** A widely adopted open-source distributed streaming platform known for its high throughput, fault tolerance, and scalability. It is written in Scala and Java and relies on the Java Virtual Machine (JVM).
*   **Redpanda:** A Kafka-compatible streaming data platform written in C++. It aims to provide higher performance, lower latency, and simpler operations compared to Kafka, often with a smaller hardware footprint. Redpanda is designed to be a drop-in replacement for Kafka, offering the same API compatibility.

**Application in SynchroTwin-AR:** The architecture diagram indicates 


that Kafka/Redpanda will be used for data ingestion, serving as the backbone for real-time data streams from BCI Edge devices. The choice between Kafka and Redpanda will depend on specific performance requirements, operational overhead considerations, and existing infrastructure preferences. Redpanda's claims of higher performance and lower latency might make it a strong candidate for the real-time demands of SynchroTwin-AR.

### 5.2 Real-time Stream Processing (Apache Flink)

**Concept:** Apache Flink is a powerful open-source stream processing framework designed for high-throughput, low-latency, and fault-tolerant stream processing. It is particularly well-suited for real-time analytics, event-driven applications, and continuous data pipelines. Flink can process data streams with very low, sub-second latency, making it ideal for applications requiring immediate insights and reactions to events.

**Application in SynchroTwin-AR:** The architecture diagram shows the 


Synchrony Engine (Flink) processing data from Kafka/Redpanda. This indicates that Flink will be used for real-time computation of the Resonance (R(t)) score and other features derived from the incoming sensor data. Its ability to handle continuous data streams and perform complex computations in real-time is crucial for the responsiveness of the SynchroTwin-AR system.

### 5.3 Inter-Service Communication (gRPC)

**Concept:** gRPC (gRPC Remote Procedure Calls) is a modern, open-source, high-performance RPC (Remote Procedure Call) framework developed by Google. It uses HTTP/2 for transport and Protocol Buffers as the interface description language. gRPC is designed for efficient communication between microservices, especially in polyglot environments, offering advantages such as:

*   **High Performance:** Built on HTTP/2, which supports multiplexing, header compression, and server push, leading to lower latency and higher throughput compared to traditional HTTP/1.1 REST APIs.
*   **Strongly Typed Contracts:** Protocol Buffers enforce strict service contracts, ensuring type safety and reducing integration errors between services.
*   **Language Agnostic:** Code generation for various programming languages allows services written in different languages to communicate seamlessly.
*   **Efficient Serialization:** Protocol Buffers are more efficient in terms of serialization and deserialization compared to JSON or XML, leading to smaller message sizes.

**Application in SynchroTwin-AR:** The architecture diagram indicates that the Bias Mirror and Digital Twin services will communicate via gRPC. This choice aligns with the need for high-performance and reliable inter-service communication within a microservices architecture. gRPC would be particularly beneficial for the frequent and low-latency data exchanges required between these core backend components, ensuring efficient processing of policy vectors and bias calculations.

### 5.4 Data Storage Solutions

The SynchroTwin-AR project outlines a multi-tiered data storage strategy, utilizing different database technologies optimized for specific data types:

*   **Time-series Data (TimescaleDB/InfluxDB):**
    *   **Concept:** Time-series databases are optimized for storing and querying data points indexed by time. They are ideal for metrics, events, and sensor data that are collected over time.
    *   **TimescaleDB:** An open-source relational database that runs as an extension on PostgreSQL, combining the benefits of a relational database with the performance of a time-series database. It offers full SQL support and is well-suited for complex analytical queries.
    *   **InfluxDB:** An open-source time-series database written in Go, designed for high-performance ingestion and querying of time-series data. It is part of the TICK stack (Telegraf, InfluxDB, Chronograf, Kapacitor) and is often used for monitoring, IoT, and analytics.
    *   **Application in SynchroTwin-AR:** The document specifies TimescaleDB/InfluxDB for storing time-series data such as features and Resonance (R) values at 1-second and 250-millisecond granularities. This choice ensures efficient storage and retrieval of the high-volume, time-stamped data generated by the Synchrony Engine.

*   **Vector Data (pgvector/Milvus):**
    *   **Concept:** Vector databases are designed to store and query high-dimensional vectors, often used in machine learning for similarity search, embeddings, and semantic search.
    *   **pgvector:** An open-source extension for PostgreSQL that adds vector similarity search capabilities. It allows storing and querying vector embeddings directly within a PostgreSQL database.
    *   **Milvus:** An open-source vector database built for scalable similarity search. It is designed to handle massive-scale vector datasets and provides high-performance search capabilities.
    *   **Application in SynchroTwin-AR:** pgvector/Milvus will be used for storing policy vectors (φ embeddings) and semantic logs. This is crucial for the Bias Mirror and Digital Twin components, enabling efficient similarity searches and comparisons of behavioral patterns.

*   **Graph Data (Neo4j):**
    *   **Concept:** Graph databases are optimized for storing and querying highly connected data, representing entities (nodes) and their relationships (edges). They are well-suited for modeling complex relationships and performing graph traversals.
    *   **Neo4j:** A leading open-source graph database that provides a native graph storage and processing engine. It uses the Cypher query language, which is optimized for graph patterns.
    *   **Application in SynchroTwin-AR:** Neo4j will be used for storing knowledge graphs, particularly for the MRAP (Prior Reset + Retrieval) component. This will enable efficient retrieval of related concepts, motifs, and pathways, supporting ideation and counter-bias nudges.

*   **Object Storage (S3):**
    *   **Concept:** Object storage is a highly scalable and durable storage solution for unstructured data, such as images, videos, and raw sensor data. Data is stored as objects within buckets, and each object has a unique identifier.
    *   **AWS S3 (Amazon Simple Storage Service):** A widely used cloud-based object storage service known for its scalability, durability, and availability.
    *   **Application in SynchroTwin-AR:** S3 will be used for optional storage of raw media and raw sensor data, with lifecycle policies to manage data retention. This ensures that sensitive raw data is not stored by default and is only retained with explicit user consent.

## 6. Algorithms (Spec-Level)

The document provides specific algorithmic details for key components of the SynchroTwin-AR system, highlighting the mathematical foundations for Resonance calculation, Bias Mirror, Digital Twin, and MRAP.

### 6.1 Resonance R(t) Algorithms

As detailed in Section 3, the Resonance score (R) is a fusion of multiple physiological and behavioral synchrony measures. The algorithmic specifications include:

*   **Phase-Locking Value (PLV):** Calculated using the formula: $\mathrm{PLV}(t)=\Big|\frac{1}{N}\sum_{k=1}^{N} e^{i(\phi_a(t_k)-\phi_b(t_k))}\Big|$. This involves extracting phases from band-limited signals.
*   **Envelope Correlation ($r_\text{env}$):** Sliding Pearson correlation on band-limited envelopes, likely representing respiratory or micro-motion proxies.
*   **CRQA (CRQA_n):** Normalized Cross-Recurrence Quantification Analysis, applied to binarized pause/gesture sequences to compute recurrence and determinism.
*   **fNIRS Coupling ($C\text{fNIRS}$):** Wavelet coherence (0.01–0.1 Hz) projected to a scalar, indicating brain-to-brain synchrony.
*   **Fusion:** The weighted sum of these components passed through a logistic function: $R=\sigma(w_1\mathrm{PLV}+w_2 r_\text{env}+w_3 \mathrm{CRQA}n+w_4 C\text{fNIRS})$. Weights ($w_i$) are to be tuned via pilot studies.
*   **Confidence:** Derived from SNR and channel agreement, providing a measure of the reliability of the R(t) score.

### 6.2 Bias Mirror Algorithms

The Bias Mirror aims to quantify and address cognitive biases. The algorithms specified are:

*   **Bias Calculation ($b_i(\phi)$):** Logistic heads over a state vector $\phi(t) = [V,A,F,O,C] \oplus \mathrm{embed}(\text{text})$. This suggests a machine learning model that takes a multi-modal state vector (e.g., Valence, Arousal, Focus, Openness, Conscientiousness, and text embeddings) as input and outputs a bias score.
*   **Counter-bias Projection ($\phi’$):** $\phi’=(I-P_i)\phi,\quad P_i=\frac{w_i w_i^\top}{\|w_i\|^2}$. This formula describes a projection operation to reduce the influence of a specific bias ($w_i$) from the state vector $\phi$. This is a crucial part of the nudging mechanism.

### 6.3 Digital Twin Algorithms

The Digital Twin component compares the Default Narrative (DN) with the Observed Narrative (ON) and calculates the divergence:

*   **Default Narrative (DN):** Exponential Moving Average (EMA) over the Observed Narrative (ON). This implies that the DN is a learned, evolving representation of an individual's typical behavior or policy.
*   **Bias Divergence ($\Delta_\text{bias}$):** Calculated using either KL-divergence or cosine similarity:
    *   $\Delta_\text{bias}=\mathrm{KL}(\pi_{ON}\parallel \pi_{DN})$ (Kullback-Leibler divergence between ON and DN policy distributions).
    *   $1-\cos(\pi_{ON},\pi_{DN})$ (1 minus the cosine similarity between ON and DN policy vectors).

These algorithms are fundamental for quantifying the deviation from typical behavior and providing actionable insights for bias reduction.

### 6.4 MRAP (Prior Reset + Retrieval) Algorithms

MRAP (Memory, Retrieval, and Prioritization) is a sophisticated component for ideation and counter-bias strategies:

*   **Annealing ($\pi^{(\tau)}$):** $\pi^{(\tau)}=\mathrm{softmax}\big(\log \pi_{DN}/\tau\big),\ \tau>1$. This formula describes a temperature-controlled softmax operation on the log of the DN policy, allowing for a 


softening of the prior distribution, potentially to encourage exploration.
*   **Anti-priming:** Stochastic token drop/reshuffle (20–40%). This mechanism aims to prevent cognitive fixation by introducing randomness or disruption to existing thought patterns.
*   **Retrieval Channels:** Vector top-k, graph paths (≤3), motif mining; novel-yet-coherent filter. This indicates multiple strategies for retrieving relevant information from different data stores (vector, graph) and filtering for novelty and coherence.
*   **Triad Scoring:** Score = α·Fit − β·MDL + γ·Novelty. This formula suggests a scoring mechanism for retrieved ideas or solutions, balancing their fit to the problem, complexity (Minimum Description Length), and novelty.

### 6.5 Causal Playground Algorithms

The Causal Playground is designed for exploring counterfactuals and understanding the impact of interventions:

*   **Minimal SCM (Structural Causal Model):** This implies a simplified causal model of the system or interaction.
*   **Counterfactual Rollouts:** Y_x with interventions. This involves simulating different scenarios by intervening on specific variables in the causal model and observing the outcomes.
*   **Utility with Risk (EVR):** $\mathrm{EVR}=\mathbb{E}[U]-\lambda \mathrm{Var}(U)$. This formula represents Expected Value with Risk, where $U$ is utility, $\mathbb{E}[U]$ is expected utility, $\mathrm{Var}(U)$ is variance of utility (risk), and $\lambda$ is a risk aversion parameter. This allows for decision-making that balances potential gains with associated risks.

## 7. ML/NLP Lifecycle

The project outlines a comprehensive ML/NLP lifecycle, covering feature stores, model types, training data, evaluation, and drift detection.

*   **Feature Store:** Feast is mentioned, indicating a centralized system for managing and serving machine learning features, ensuring online/offline parity.
*   **Models:**
    *   **Bias heads (logistic/MLP):** Used for the Bias Mirror, with personalization via LoRA (Low-Rank Adaptation) or last-layer Fine-Tuning.
    *   **Persona/RAG (Retrieval-Augmented Generation):** Utilizes curated corpora, prompt/router per persona, guardrails, and citations, suggesting a sophisticated system for generating contextually relevant responses.
*   **Training Data:** A combination of synthetic and real (consented) data will be used for model training.
*   **Evaluation:** Per-model AUC/PR (Area Under the Curve/Precision-Recall) for individual models, and end-to-end ΔR/Δ_bias improvements for the overall system. Ablation studies (removing PLV/CRQA/fNIRS) will be conducted to quantify the contribution of each feature.
*   **Drift Detection:** PSI/KS (Population Stability Index/Kolmogorov-Smirnov) on $\phi$ distribution and Canary rollouts will be used to detect model drift and ensure performance stability. ADRs (Architecture Decision Records) will be used for threshold changes.
*   **Privacy:** DP-SGD (Differentially Private Stochastic Gradient Descent) is an optional consideration for cohort models, and raw PII (Personally Identifiable Information) will not be stored in training artifacts.

## 8. APIs (Selected)

The project defines key APIs for various functionalities:

### 8.1 Protobuf (Canonical Ingestion)

Protobuf (Protocol Buffers) is used for efficient, language-neutral, platform-neutral, extensible serialization of structured data. It is specified for canonical ingestion, ensuring a standardized and efficient data format for incoming sensor data.

*   **`SensorFrame` Message:**

    ```protobuf
    message SensorFrame {
      string session_id = 1;
      string user_id = 2;
      int64  t_unix_ms = 3;
      repeated float eeg_bands = 4;  // band powers or phases
      optional float resp_env = 5;
      optional float imu_proxy = 6;
      optional float fnirs_oxy = 7;
    }
    ```

    This message defines the structure for raw sensor data, including session and user IDs, timestamp, EEG band powers/phases, and optional respiratory envelope, IMU proxy, and fNIRS oxygenation data.

*   **`Resonance` Message:**

    ```protobuf
    message Resonance {
      string session_id = 1;
      int64  t_unix_ms = 2;
      float  plv = 3;
      float  r_env = 4;
      float  crqa = 5;
      float  fnirs = 6;
      float  r = 7;
      float  conf = 8;
    }
    ```

    This message defines the structure for the computed Resonance score and its components, including PLV, envelope correlation, CRQA, fNIRS coherence, the fused R value, and confidence.

### 8.2 OpenAPI (HTTP)

OpenAPI (formerly Swagger) is used for defining HTTP-based APIs, providing a standardized way to describe RESTful services. The following endpoints are specified:

*   `POST /v1/sessions`: For creating or joining sessions.
*   `POST /v1/sessions/{id}/phase`: For controlling session phases.
*   `GET /v1/sessions/{id}/resonance`: For pulling Resonance data (likely for debugging or specific client needs).
*   `POST /v1/twin/{user}/dn`: For building Default Narrative (DN) policies for a user.
*   `POST /v1/twin/{session}/{user}/debrief`: For initiating debriefing processes for a session and user.
*   `GET /v1/report/{session}`: For retrieving session reports.

### 8.3 Realtime Communication

*   **WebRTC DataChannel:** For real-time streaming of R frames, offering low-latency, peer-to-peer communication.
*   **WebSocket fallback:** For web clients that may not fully support WebRTC DataChannels.

## 9. Data & Storage

This section details the data types, storage solutions, retention policies, and schema highlights.

*   **Time-Series (features/R):** TimescaleDB (hypertables), 1s & 250ms granularities. This choice emphasizes the need for efficient storage and querying of high-volume, time-stamped data.
*   **Vector:** pgvector for $\phi$ embeddings & semantic logs; Milvus optional for scale. This supports efficient similarity search for policy vectors and semantic data.
*   **Graph:** Neo4j for knowledge paths (MRAP). This is crucial for modeling and querying complex relationships within the MRAP component.
*   **Object:** S3 for opt-in media/raw; lifecycle policies. This provides scalable and durable storage for unstructured data, with privacy considerations.
*   **Retention:** Features 90 days (default), metadata 1 year, raw media 0 days unless opt-in. This highlights a strong emphasis on data privacy and minimizing storage of sensitive raw data.

### 9.1 Schema Highlights

*   **`features` Table:**

    ```sql
    CREATE TABLE features(
      session UUID, user_id UUID, t TIMESTAMPTZ,
      plv REAL, r_env REAL, crqa REAL, fnirs REAL, r REAL, conf REAL,
      PRIMARY KEY(session, user_id, t)
    );
    ```

    This table stores the computed synchrony features and the fused Resonance score, along with session and user identifiers and timestamps.

*   **`policies` Table:**

    ```sql
    CREATE TABLE policies(
      user_id UUID, ts TIMESTAMPTZ,
      dn JSONB, on JSONB, delta_bias REAL
    );
    ```

    This table stores the Default Narrative (DN), Observed Narrative (ON), and the calculated bias divergence (`delta_bias`) for each user over time.

## 10. Security, Privacy, Ethics

This section emphasizes the critical importance of security, privacy, and ethical considerations in the SynchroTwin-AR project.

*   **Default Storage:** Only derived features are stored by default. Raw EEG/audio/video data is disabled unless explicit, per-session opt-in, demonstrating a strong commitment to user privacy.
*   **Encryption:** TLS 1.3 for in-transit encryption, mTLS (mutual TLS) for service-to-service communication, and AES-GCM for encryption at rest. Per-tenant DEKs (Data Encryption Keys) via KMS (Key Management Service) and Vault for secrets management ensure robust data protection.
*   **Consent Ledger:** An immutable, scope-wise consent ledger ensures transparent and auditable management of user consents.
*   **Compliance Posture:** GDPR/CCPA ready, with DSR (Data Subject Rights) export/delete flows and a DPIA (Data Protection Impact Assessment) template, indicating adherence to major data protection regulations.
*   **Ethics:** No “medical claims” are made, coercive nudges are avoided, and user-controlled transparency for bias outputs is prioritized, reflecting a responsible and ethical approach to the technology.

## 11. Reliability & Observability

This section outlines the measures for ensuring system reliability and providing comprehensive observability.

*   **SLIs/SLOs (Service Level Indicators/Objectives):**
    *   **Live freshness:** ≥99% frames <200 ms (SLO). This is a critical performance metric for real-time feedback.
    *   **Computation drift:** |R_online − R_offline| < 5% (p95). This ensures the consistency and accuracy of the Resonance calculation.
    *   **Uptime:** 99.5% for MVP, 99.9% for v1. These are standard availability targets for production systems.
*   **Telemetry:** Tracing (orchestrator→engine→client), metrics (lag, jitter, drop), and PII-scrubbed logs provide comprehensive insights into system behavior and performance.
*   **Runbooks:** Defined for common issues like sensor desync, TURN overload, and Kafka backpressure, enabling quick resolution of operational problems.
*   **Synthetic Load:** Testing with synthetic load including packet loss (10–20%) ensures system resilience under adverse network conditions.

## 12. DevOps & IaC

This section details the development, operations, and infrastructure as code practices.

*   **Repos:** Mono-repo strategy (Bazel/Turborepo) for managing code across multiple services.
*   **CI (Continuous Integration):** GitHub Actions + Buildkite for automated builds, testing, and static analysis (tsc/mypy strict). Distroless images are used for smaller, more secure deployment artifacts.
*   **CD (Continuous Deployment):** ArgoCD for GitOps-based continuous deployment, with canary deployments and feature flags (OpenFeature) for safe rollouts.
*   **IaC (Infrastructure as Code):** Terraform + Helm for managing infrastructure and Kubernetes (GKE/EKS) deployments. Autoscaling and resource QoS (Quality of Service) for low-latency services ensure efficient resource utilization and performance.

## 13. Testing & Validation Plan

A robust testing and validation plan is outlined to ensure the correctness and effectiveness of the system.

*   **DSP Correctness:** PLV/CRQA unit tests against analytic cases (e.g., perfect sync → R→1) to verify the accuracy of digital signal processing algorithms.
*   **Integration:** Simulated sensor streams → R(t) → AR loop testing to validate end-to-end functionality. Chaos tests (packet drop/latency) to assess system resilience.
*   **Human Studies:** A/B testing (AR-on vs AR-off) to evaluate the impact of AR feedback. Blinded raters for Task-B creativity and power analysis to detect ΔR=0.15 with α=0.05 for rigorous evaluation of human performance.
*   **Ablation:** Removing each feature channel and quantifying ΔR, Δ_bias regressions to understand the contribution of individual components.

## 14. Risks & Mitigations

Potential risks and their corresponding mitigation strategies are identified.

*   **Noisy Sensors:** Mitigation includes SNR gating, confidence-weighted R, and user guidance for sensor placement.
*   **Over-interpretation:** Disclaimers, showing confidence scores, and avoiding single-number “truth” prevent misinterpretation of results.
*   **Privacy:** Default no-raw storage, row-level encryption, and DP noise in research exports ensure user privacy.
*   **Network Jitter:** Predictive smoothing, jitter buffers, and adaptive bitrate for AR overlays mitigate the impact of network instability.

## 15. Roadmap

The project roadmap outlines key milestones and features for different release versions.

*   **D+14 (MVP):** Live R(t) + AR orbs; DN/ON + Δ_bias; debrief reports. This is the initial Minimum Viable Product.
*   **D+60:** MRAP + Triad; Causal Playground; improved weights; cohort analytics. This expands the system with advanced features.
*   **D+90:** Active-Inference loop (self-tuning feedback intensity & comfort bounds); multi-dyad rooms; enterprise SSO. This represents further maturation and enterprise-readiness.

## 16. Acceptance Criteria (Go/No-Go)

Specific criteria for project acceptance are defined.

*   Live R(t) visible & stable for ≥95% of a 15-min session on two commodity phones.
*   AR feedback improves ΔR vs control by ≥0.1 on average in pilot.
*   Debrief shows DN/ON/Δ_bias with one counter-bias step; users complete next-day 10-min step ≥60%.
*   No raw storage unless toggled; all flows gated by consent.

## 17. Appendices

### A) Minimal Session Protocol (script)

This outlines a structured session flow:

1.  **Baseline (60 s):** No visuals. Capture R₀.
2.  **Silent Sync (90 s):** AR on. Goal R>0.6 for ≥20 s.
3.  **Task-A (120 s):** Silent guess of each other’s chosen image/shape; record accuracy.
4.  **Task-B (240 s):** Silent co-design of a mark/logo (gestures/tempo only); later rated by blinded judges.
5.  **Debrief (240 s):** DN/ON, Δ_bias, one tiny step with timestamp.

### B) Core Pseudocode (online resonance)

```python
def resonance_window(winA, winB):
    # phase for low-band signals (resp/micro-movement)
    plv = abs(np.mean(np.exp(1j * (winA.phase - winB.phase))))
    r_env = pearson(winA.env, winB.env)  # sliding corr on envelopes
    crqa_n = normalized_crqa(winA.pause_seq, winB.pause_seq)  # determinism
    fnirs = wavelet_coherence(winA.fnirs, winB.fnirs) if (winA.fnirs and winB.fnirs) else 0.0
    r = logistic(w1*plv + w2*r_env + w3*crqa_n + w4*fnirs)
    conf = confidence_from_snr(winA.snr, winB.snr, channel_agreement=[plv, r_env])
    return {
        'plv': plv,
        'r_env': r_env,
        'crqa': crqa_n,
        'fnirs': fnirs,
        'r': r,
        'conf': conf
    }
```

### C) Data Dictionary (excerpt)

*   `r`: fused synchrony [0..1]
*   `conf`: 0..1 confidence from SNR/channel agreement
*   `delta_bias`: policy divergence scalar
*   `coh`: cosine($\phi_\text{now}$, $\phi_\text{intent}$) — optional coherence to stated intent

## Architect’s Note (stance & taste)

The architect’s note emphasizes the project’s commitment to turning 

