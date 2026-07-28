import cv2
import json
import os
import time
from ultralytics import YOLO
from brain import IntelligenceBrain

MODEL = YOLO("yolov8n.pt")
BRAIN = IntelligenceBrain("knowledge_base/safety_manual.pdf")

def extract_json(text):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return text[start:end] if start != -1 else None
    except: return None

def get_config():
    """Reads the config to check if the user granted permission to connect."""
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {"source": 0, "connected": False}

def start_integration():
    print("👁️ Guardian Eye Engine is STANDBY. Waiting for Dashboard Permission...")
    
    while True:
        config = get_config()
        source = config.get("source", 0)
        connected = config.get("connected", False)

        if not connected:
            # Standby Mode: Wait 1 second and check again
            time.sleep(1)
            continue
        
        print(f"✅ Permission Granted! Connecting to Source: {source}")
        cap = cv2.VideoCapture(source)
        
        while cap.isOpened():
            # check if user disconnected from dashboard
            current_config = get_config()
            if not current_config.get("connected", False) or current_config.get("source") != source:
                print("❌ Disconnecting... User revoked permission.")
                break

            ret, frame = cap.read()
            if not ret: break

            results = MODEL(frame, verbose=False)[0]
            for box in results.boxes:
                if int(box.cls[0]) == 0: 
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    is_danger = x2 > (frame.shape[1] / 2)
                    crop = frame[y1:y2, x1:x2]
                    timestamp = int(time.time())
                    img_name = f"violation_{timestamp}.jpg"
                    cv2.imwrite(img_name, crop)
                    
                    verdict = BRAIN.analyze_live_violation(img_name, is_danger)
                    json_str = extract_json(verdict)
                    if json_str:
                        try:
                            data = json.loads(json_str)
                            data['photo'] = img_name
                            with open("ai_signal.json", "w") as f:
                                json.dump(data, f)
                        except: pass

            cv2.line(frame, (frame.shape[1]//2, 0), (frame.shape[1]//2, frame.shape[0]), (0, 0, 255), 2)
            cv2.putText(frame, "RESTRICTED ZONE", (frame.shape[1]//2 + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imwrite("webcam_feed.jpg", frame)
            cv2.imshow("Guardian Eye - AI Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                cap.release()
                cv2.destroyAllWindows()
                return

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    start_integration()