from flask import Flask, request, jsonify
from multiprocessing import Process, Manager
import cv2
from ultralytics import YOLO  # YOLOv8 for detection
import time
from flask_cors import CORS
import uuid

model = YOLO('yolo11n.pt')

def process_cctv_feed(feed_url,people_count_data):
        """Function to process a CCTV feed and update people count in shared memory."""
        cap = cv2.VideoCapture(feed_url)
        
        if not cap.isOpened():
            print(f"Error: Unable to open feed {feed_url}")
            return
        videoWriter = cv2.VideoWriter(f"{uuid.uuid4()}.mp4", cv2.VideoWriter_fourcc(*'mp4v') ,30, (int(cap.get(3)), int(cap.get(4))))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"{feed_url}: No frame captured.")
                break
            
            # Detect people in the frame using YOLO
            results = model.predict(frame, conf=0.5, show=False)
            # count = sum(1 for r in results for _ in r.boxes)  # Count detected people
            count = 0
            for result in results:
                for box in result.boxes:
                    if int(box.cls[0]) != 0:
                        continue
                    count += 1
                    # Get bounding box coordinates (x1, y1, x2, y2)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Draw a bounding rectangle around the detected person
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            videoWriter.write(frame)
            people_count_data[feed_url] = {
                "count": count,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        cap.release()
def main():
    manager = Manager()
    cctv_processes = {}  # Stores {url: process}
    people_count_data = manager.dict()
    print("Starting Flask App")
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Shared dictionary to store people counts for each CCTV feed
      # Shared dictionary {url: {"count": int, "timestamp": str}}

    # Load YOLO model for detection
   

    

    @app.route('/api/add-camera', methods=['POST'])
    def add_camera():
        """Start a new process for the given CCTV feed URL."""
        data = request.json
        feed_url = data.get('url')
        
        if feed_url in cctv_processes:
            return jsonify({"error": "CCTV feed already running."})
        
        process = Process(target=process_cctv_feed, args=(feed_url,people_count_data))
        process.start()
        cctv_processes[feed_url] = process
        people_count_data[feed_url] = {"count": 0, "timestamp": ""}  # Initialize data

        return jsonify({"message": f"Started processing for {feed_url}"})


    @app.route('/api/remove-camera', methods=['POST'])
    def remove_camera():
        """Terminate the process for the given CCTV feed URL."""
        data = request.json
        feed_url = data.get('url')
        
        process = cctv_processes.pop(feed_url, None)
        if process:
            try:
                process.terminate()
                process.join()  # Wait for the process to finish cleanly
            except Exception as e:
                return jsonify({"error": f"Failed to terminate process for {feed_url}: {str(e)}"}), 500
            
            people_count_data.pop(feed_url, None)  # Remove data from shared memory
            return jsonify({"message": f"Stopped processing for {feed_url}"}), 200
        
        return jsonify({"error": "CCTV feed not found."}), 404


    @app.route('/api/get-all', methods=['GET'])
    def get_all_data():
        """Retrieve real-time people count data for all CCTV feeds."""
        return jsonify(dict(people_count_data)), 200

    app.run(port=8000,debug=True, threaded=True)


if __name__ == '__main__':
    main()
