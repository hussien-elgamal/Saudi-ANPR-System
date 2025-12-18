<div align="center">🦅 VisionGate: Enterprise Saudi ANPR SystemA High-Performance, Hybrid AI System for Real-Time Saudi License Plate Recognition Engineered for Security Patrols, Smart Airports, and Gated Communities.</div>📖 Executive SummaryVisionGate is a production-grade ANPR microservice designed specifically for real-world vehicle security and access control in the Kingdom of Saudi Arabia.Unlike generic OCR projects, VisionGate tackles real operational challenges:🚗 Motion Blur — Reads plates from moving vehicles📐 Angled Views — Supports up to 45° skew🌙 Low Light & Glare — Image enhancement via CLAHE🌍 Dual Language — Processes Arabic & English plates simultaneouslyThe system is mobile-first, allowing security officers to scan vehicles directly from their phones while all AI processing runs securely on the backend.📱 Live Mobile Deployment ExamplesRepresentative screenshots of real-time ANPR in mobile apps (detection with bounding boxes and recognition results).Android DemoMobile App IntegrationDetection View<img src="https://www.sd-toolkit.com/images/sdtanpr_usage/sdt-anpr-android-screenshot_600x.jpg" width="200"><img src="https://adaptiverecognition.com/wp-content/uploads/2024/04/anpr-lpr-mobile-app-product-image-1-768x512.png" width="300"><img src="https://i.ytimg.com/vi/kU2J_8FIr7U/maxresdefault.jpg" width="300">(Source: SD-Toolkit)(Source: Adaptive Recog.)(Source: MaxSoft)🟢 Green / 🔴 Red visual feedback is provided instantly based on vehicle status (< 100ms inference & hotlist check).🏗️ System ArchitectureVisionGate follows a scalable microservices architecture, capable of processing Mobile HTTPS uploads and CCTV RTSP video streams.🌍 Real-World Use Cases1. Smart Parking (Ticketless Entry)Automating entry for thousands of cars daily with high throughput.sequenceDiagram
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
2. Law Enforcement (Patrol Units)Helping officers identify stolen vehicles in real-time.sequenceDiagram
    participant Cop as 👮 Mobile App
    participant API as 🦅 VisionGate API
    participant DB as 💾 Hotlist DB

    Cop->>API: Captures Plate Image
    API->>DB: Check "Wanted" Status
    
    alt Vehicle is Wanted
        DB-->>API: ALERT: Stolen Vehicle!
        API-->>Cop: 🚨 RED ALERT SCREEN
    else Vehicle Clear
        DB-->>API: Status Clear
        API-->>Cop: 🟢 GREEN CLEAR SCREEN
    end
🛠️ Technical Highlights🔹 The Hybrid AI PipelineStandard models fail on angled plates common in CCTV setups. VisionGate uses a custom pipeline:Localization: YOLOv8n trained on Saudi datasets (e.g., King Saud University Benchmark).Refinement: Custom unclip_ratio=1.8 in PaddleOCR to expand bounding boxes for slanted text.Failover: Automatically degrades from GPU (CUDA) to CPU if hardware issues occur, ensuring 24/7 uptime.🔹 The Logic Mapper (mapper.py)Raw OCR output is often noisy. The SaudiPlateMapper class implements heuristic logic:Symbol Filtering: Removes non-alphanumeric noise.Spatial Logic: Prioritizes the right-most 3 letters (Arabic standard).Syntax Enforcement: Validates [3 Letters] + [3-4 Numbers] structure.📸 Examples of Saudi License PlatesThese images illustrate typical Saudi plates (close-ups, on vehicles, angled, low light, and motion blur scenarios) that VisionGate handles effectively.Close-upOn VehicleAngled View(Source: Wiki Commons)(Source: Shutterstock)(Source: Wiki Commons)Note: The system is trained to handle motion blur and low-light conditions common in night patrols.💻 Installation & SetupPrerequisites: Python 3.9+, CUDA Toolkit (Optional for GPU acceleration).# 1. Clone the Repository
git clone [https://github.com/hussien-elgamal/Saudi-ANPR-System.git](https://github.com/hussien-elgamal/Saudi-ANPR-System.git)
cd Saudi-ANPR-System

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Run the Microservice
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
📡 API Response ExamplePOST /detect/
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
👨‍💻 AuthorHussien Elgamal Mid-Level AI Engineer & Data Specialist Open for collaboration on Computer Vision, Smart City, and Security AI projects.
