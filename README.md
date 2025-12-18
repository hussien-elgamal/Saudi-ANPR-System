# 🦅 VisionGate: Enterprise Saudi ANPR System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688?style=for-the-badge&logo=fastapi)
![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-purple?style=for-the-badge)
![PaddleOCR](https://img.shields.io/badge/OCR-PaddleOCR-red?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live%20Production-success?style=for-the-badge)

<br>

**A High-Performance, Hybrid AI System for Real-Time Saudi License Plate Recognition.**
<br>
*Engineered for Security Patrols, Smart Airports, and Gated Communities.*

</div>

---

## 📖 Executive Summary
**VisionGate** is a production-grade microservice designed to automate vehicle access control and security monitoring in the KSA region.

Unlike generic OCR scripts, VisionGate is engineered to handle **Real-World Chaos**:
* **Motion Blur:** Captures clear text from moving vehicles.
* **Angled Views:** Reads plates up to 45° skew using custom geometry logic.
* **Dual Language:** Simultaneously parses Arabic and English characters.

The system is deployed as a **Mobile-First Solution**, allowing security officers to scan vehicles directly via a secure web interface connected to the central API.

---

## 📱 Live Mobile Deployment
The following screenshots demonstrate the system running in a live environment, accessed via a mobile patrol device using a secure tunnel.

| **Live Feed & Detection** | **Instant Recognition & Logging** |
|:-------------------------:|:---------------------------------:|
| <img src="assets/img1.jpeg" width="300"> | <img src="assets/img2.jpeg" width="300"> |
| *Real-time detection with bounding boxes* | *< 100ms Inference & Hotlist Checking* |

> **Note:** The UI provides instant visual feedback (Green/Red) to the officer based on the vehicle's security status.

---

## 🏗️ System Architecture 
VisionGate follows a scalable **Microservices Architecture**, capable of processing streams from CCTV RTSP feeds or HTTP Mobile uploads.

```mermaid
graph TD
    subgraph "📍 Input Layer (The Edge)"
        Mobile[📱 Mobile Patrol App]
        CCTV[📹 Surveillance CCTV]
    end

    subgraph "⚙️ VisionGate Engine (GPU Cluster)"
        PP[🎨 Preprocessing<br/>CLAHE & Sharpening]
        Det[🧠 YOLOv8<br/>Localization]
        Rec[📖 PaddleOCR<br/>Unclip Ratio 1.8]
        Logic[🇸🇦 Saudi Syntax Mapper]
    end

    subgraph "💾 Action & Security Layer"
        DB[(Wanted Database)]
        Gate[🚧 IoT Barrier]
        Alert[🚨 Security Dashboard]
    end

    Mobile -->|HTTPS Post| PP
    CCTV -->|RTSP Stream| PP
    PP --> Det --> Rec --> Logic
    Logic -->|Normalized Text| DB
    
    DB -- "Authorized" --> Gate
    DB -- "WANTED!" --> Alert


🌍 Real-World Use Cases
1. Smart Parking (Ticketless Entry)
Automating entry for thousands of cars daily with high throughput.


sequenceDiagram
    participant Car as 🚗 Vehicle
    participant Cam as 📹 Camera
    participant API as 🦅 VisionGate API
    participant Gate as 🚧 Barrier

    Car->>Cam: Approaches Gate
    Cam->>API: Sends Frame
    Note over API: Enhancing -> YOLO -> OCR
    API->>API: Validate Saudi Syntax
    API-->>Gate: {status: "Authorized", plate: "1234 KSA"}
    Gate->>Car: Opens Barrier (0.2s Latency)
2. Law Enforcement (Patrol Units)
Helping officers identify stolen vehicles in real-time.


sequenceDiagram
    participant Officer as 👮 Mobile App
    participant API as 🦅 VisionGate API
    participant DB as 💾 Hotlist DB

    Officer->>API: Captures Plate Image
    API->>DB: Check "Wanted" Status
    
    alt Vehicle is Wanted
        DB-->>API: ALERT: Stolen Vehicle!
        API-->>Officer: 🚨 RED ALERT SCREEN
    else Vehicle Clear
        API-->>Officer: ✅ Status Clear
    end

🛠️ Technical Highlights
🔹 The Hybrid AI Pipeline
Standard models fail on angled plates common in CCTV setups. VisionGate uses a custom pipeline:

Localization: YOLOv8n trained specifically on Saudi datasets (King Saud University Benchmark).

Refinement: Custom unclip_ratio=1.8 parameter in PaddleOCR to expand bounding boxes for slanted text.

Failover: Automatically degrades from GPU (CUDA) to CPU if hardware issues are detected, ensuring 24/7 uptime.

🔹 The Logic Mapper (Mapper.py)
Raw OCR output is often noisy. The SaudiPlateMapper class implements heuristic logic:

Symbol Filtering: Removes non-alphanumeric noise.

Spatial Logic: Prioritizes the right-most 3 letters (Arabic standard).

Syntax Enforcement: Validates [3 Letters] + [3-4 Numbers] structure.

💻 Installation & Setup
Prerequisites: Python 3.9+, CUDA Toolkit (Optional).



# 1. Clone the Repository
git clone https://github.com/hussien-elgamal/Saudi-ANPR-System.git
cd Saudi-ANPR-System

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Run the Microservice
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
API Response Example
POST /detect/



{
  "status": "success",
  "data": {
    "plate_ar": "ق ب ب 6102",
    "plate_en": "6102 G B B",
    "confidence": 0.98,
    "is_wanted": false,
    "action": "LOG_AND_PASS"
  }
}
👨‍💻 Author
Hussien Elgamal Mid-Level AI Engineer & Data Specialist

Open for collaboration on Computer Vision, Smart City, and Security AI projects.