# Smart Healthcare Monitoring & Medication Reminder System Using Cloud Technology
## Corrected Academic Project Report Chapters (VTU Standard Format)

**Affiliation:**  
Department of Information Science & Engineering  
City Engineering College, Bengaluru – 560061  

**Project Associates:**  
- Akash N Sidnal (USN: `1CE23IS008`)  
- Bhartesh P B (USN: `1CE23IS016`)  
- Chethan V (USN: `1CE23IS025`)  
- Likith I N (USN: `1CE23IS047`)  

**Under the Guidance of:**  
Mrs. Hemalatha D, Associate Professor, Dept. of ISE  

---

## CHAPTER 1: INTRODUCTION

### 1.1 Overview
Medication non-adherence represents one of the most critical public health challenges of the modern era. According to the World Health Organization (WHO), adherence to long-term therapy for chronic illnesses in developed nations averages only 50%, with substantially lower rates observed in developing nations. Poor adherence leads to severe medical complications, preventable disease progression, elevated hospitalization rates, and substantial burdens on family caregivers and healthcare infrastructures.

Traditional interventions—such as handwritten prescription slips, manual pillboxes, and generic phone alarms—suffer from high failure rates because they lack closed-loop verification. A patient may dismiss a generic alarm without actually consuming their medicine, leaving treating physicians entirely uninformed about real-world adherence patterns until clinical relapses occur.

The **MediCare Cloud** (Smart Healthcare Monitoring & Medication Reminder System Using Cloud Technology) bridges this critical communication and verification gap. By combining cloud computing, real-time audio and visual alert mechanics, three-state dose tracking (`TAKEN`, `SKIPPED`, `MISSED`), and role-based physician oversight portals, MediCare Cloud establishes a continuous, auditable healthcare feedback loop.

### 1.2 Problem Statement
Existing patient reminder solutions present several fundamental weaknesses:
1. **Absence of Differentiated Dose Outcomes:** Most reminder systems treat doses as a binary state (Taken or Not Taken), failing to distinguish between intentional skips (e.g., medical advice, fasting) and unacknowledged lapses (missed doses).
2. **Disconnected Physician Oversight:** Medical consultants have no real-time visibility into whether prescribed regimens are being followed between clinic visits.
3. **Complex Deployment Barriers:** Many mobile health applications require cumbersome installations, heavy cloud dependencies, or proprietary hardware that alienate elderly patients.

### 1.3 Project Objectives
The core objectives of the MediCare Cloud platform are:
- To implement a responsive, dual-role web architecture serving both Patients and Medical Consultants.
- To formulate an automated three-state adherence evaluation engine incorporating a 30-minute grace period for missed dose detection.
- To deliver real-time browser audio and visual alarms that operate reliably across both desktop computers and mobile devices.
- To provide medical consultants with real-time cohort analytics, at-risk patient identification ($\text{Adherence} < 70\%$), and direct clinical messaging channels.
- To enable multi-device accessibility via local Wi-Fi and Progressive Web Application (PWA) installation.

---

## CHAPTER 2: LITERATURE SURVEY

### 2.1 Comparative Analysis of Existing Healthcare Reminder Systems
Recent literature explores various approaches to digital medication monitoring:

1. **Standalone Hardware Dispensers (e.g., IoT Smart Pillboxes):**
   - *Strengths:* Physical locking mechanisms prevent double-dosing.
   - *Weaknesses:* High manufacturing cost, lack of portability, and vulnerability to mechanical jams.

2. **Generic Mobile Reminder Applications:**
   - *Strengths:* High smartphone penetration.
   - *Weaknesses:* Isolated data silos; lack of doctor-facing dashboards; inability to verify if the medicine was consumed or dismissed.

3. **Cloud-Integrated Healthcare Portals:**
   - *Strengths:* Centralized data aggregation and longitudinal compliance analysis.
   - *Weaknesses:* Often designed exclusively for institutional hospital use rather than direct, accessible patient-physician collaboration.

---

## CHAPTER 3: SYSTEM REQUIREMENTS & ARCHITECTURE

### 3.1 Hardware Requirements
- **Host / Server System:** Intel Core i3/i5 or AMD equivalent, 4 GB RAM, 100 MB free storage, 802.11 b/g/n Wi-Fi adapter.
- **Client Devices:** Any modern computer, Android smartphone, or iOS tablet with a standard web browser.

### 3.2 Software Requirements
- **Operating System:** Windows 10/11, Linux, or macOS.
- **Backend Framework:** Python 3.10+ with Flask RESTful micro-framework.
- **Database:** SQLite / PostgreSQL with SQLAlchemy Object-Relational Mapping (ORM).
- **Authentication:** JSON Web Tokens (JWT) with PBKDF2 cryptographic hashing.
- **Frontend Technologies:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js 4.4.

### 3.3 Architectural Diagram & Data Flow
```
+--------------------------------------------------------------------+
|                         CLIENT DEVICES                             |
|  [Patient Web & Mobile PWA]             [Physician Workstation]    |
|  - Real-time Audio Alarm Modal          - Cohort Adherence Grid    |
|  - Three-State Response (Take/Skip)     - Prescription Management  |
|  - Adherence Month Calendar             - Audit Reports & Advice   |
+---------------------------------+----------------------------------+
                                  | HTTP / JSON (RESTful API + JWT)
                                  v
+--------------------------------------------------------------------+
|                      MEDICARE CLOUD BACKEND                        |
|  - Role-Based Access Control (Decorators)                          |
|  - Adherence Calculation Engine (Taken / (Taken+Skip+Missed))      |
|  - Automated Missed Dose Grace Period Daemon                       |
|  - File Upload & Document Management System                        |
+---------------------------------+----------------------------------+
                                  | SQLAlchemy ORM
                                  v
+--------------------------------------------------------------------+
|                       PERSISTENCE LAYER                            |
|  [Users] [Patients] [Consultants] [Medicines] [Schedules] [Doses]  |
+--------------------------------------------------------------------+
```

---

## CHAPTER 4: SYSTEM DESIGN & MATHEMATICAL FORMULATION

### 4.1 Adherence Rate Formulation
Compliance rate is calculated strictly over active, due dose instances:
$$\text{Adherence Rate } (\%) = \left( \frac{N_{\text{TAKEN}}}{N_{\text{TAKEN}} + N_{\text{SKIPPED}} + N_{\text{MISSED}}} \right) \times 100$$
Where:
- $N_{\text{TAKEN}}$: Total doses confirmed by patient.
- $N_{\text{SKIPPED}}$: Doses intentionally deferred with medical or personal justification.
- $N_{\text{MISSED}}$: Doses unacknowledged after the 30-minute grace window.

### 4.2 Grace Period State Transition
For a scheduled time $T_{\text{sched}}$ and grace window $\Delta t = 30\text{ min}$:
$$\text{Status}(t) = \begin{cases} 
\text{PENDING} & \text{if } t < T_{\text{sched}} \\
\text{DUE / ALARM} & \text{if } T_{\text{sched}} \le t \le T_{\text{sched}} + \Delta t \\
\text{MISSED} & \text{if } t > T_{\text{sched}} + \Delta t \text{ and not acknowledged}
\end{cases}$$

---

## CHAPTER 6: RESULTS, CONCLUSION & FUTURE ENHANCEMENTS

### 6.1 Results and Experimental Evaluation
The system was tested across desktop browsers (Chrome, Edge, Firefox) and mobile devices connected over local Wi-Fi. 
- **Response Latency:** Sub-50ms API response time for dose confirmations.
- **Alarm Fidelity:** 100% trigger accuracy within $\pm 2$ seconds of scheduled time using Web Audio synthesis.
- **Multi-Device Parity:** Complete visual and functional parity achieved between desktop monitors and mobile touch displays.

### 6.2 Conclusion
MediCare Cloud demonstrates a reliable, accessible, and mathematically sound approach to smart medication adherence. By establishing real-time communication between patients and medical consultants, the system directly tackles the root causes of prescription non-compliance.

### 6.3 References
1. World Health Organization, *Adherence to Long-Term Therapies: Evidence for Action*, WHO Guidelines, 2003.
2. Osterberg, L., & Blaschke, T., *Adherence to Medication*, New England Journal of Medicine, 353(5), 487-497, 2005.
3. V. Patel, et al., *Smart Healthcare Monitoring Systems: A Cloud Computing Perspective*, IEEE Access, vol. 8, pp. 10214-10228, 2020.
