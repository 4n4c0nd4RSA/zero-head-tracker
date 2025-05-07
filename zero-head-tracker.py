import cv2
import numpy as np
import mediapipe as mp
import time
from collections import deque
import vgamepad as vg  # Virtual gamepad library for controller emulation
import tkinter as tk
from tkinter import ttk
import threading
import queue

class SettingsWindow:
    def __init__(self, settings_queue):
        self.root = tk.Tk()
        self.root.title("Face Tracker Settings")
        self.root.geometry("400x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Queue for sending settings updates to the tracking thread
        self.settings_queue = settings_queue
        
        # Settings variables
        self.x_sensitivity = tk.DoubleVar(value=10.0)
        self.y_sensitivity = tk.DoubleVar(value=10.0)
        self.invert_x = tk.BooleanVar(value=True)
        self.invert_y = tk.BooleanVar(value=True)
        self.smoothing_frames = tk.IntVar(value=1)
        self.show_face_mesh = tk.BooleanVar(value=False)
        self.controller_stick = tk.StringVar(value="right")  # 'left' or 'right'
        
        # Setup variable tracing for real-time updates
        self.x_sensitivity.trace_add("write", self.settings_changed)
        self.y_sensitivity.trace_add("write", self.settings_changed)
        self.invert_x.trace_add("write", self.settings_changed)
        self.invert_y.trace_add("write", self.settings_changed)
        self.smoothing_frames.trace_add("write", self.settings_changed)
        self.show_face_mesh.trace_add("write", self.settings_changed)
        self.controller_stick.trace_add("write", self.settings_changed)
        
        # Create UI
        self.create_ui()
        
        # Flag to indicate tracking status
        self.running = False
        self.should_close = False
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Head Orientation Tracker", font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Status indicator
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="Status: Ready", font=('Helvetica', 10))
        self.status_label.pack(side=tk.LEFT)
        
        self.status_indicator = tk.Canvas(self.status_frame, width=15, height=15, bg="yellow")
        self.status_indicator.pack(side=tk.RIGHT)
        self.status_indicator.create_oval(2, 2, 13, 13, fill="yellow", outline="")
        
        # Sensitivity settings
        sensitivity_frame = ttk.LabelFrame(main_frame, text="Sensitivity", padding="10")
        sensitivity_frame.pack(fill=tk.X, pady=(0, 10))
        
        # X Sensitivity
        ttk.Label(sensitivity_frame, text="Yaw Sensitivity:").grid(row=0, column=0, sticky=tk.W, pady=5)
        x_scale = ttk.Scale(sensitivity_frame, from_=1.0, to=20.0, orient=tk.HORIZONTAL, 
                           variable=self.x_sensitivity, length=200)
        x_scale.grid(row=0, column=1, padx=10)
        x_value_label = ttk.Label(sensitivity_frame, textvariable=self.x_sensitivity)
        x_value_label.grid(row=0, column=2)
        
        # Y Sensitivity  
        ttk.Label(sensitivity_frame, text="Pitch Sensitivity:").grid(row=1, column=0, sticky=tk.W, pady=5)
        y_scale = ttk.Scale(sensitivity_frame, from_=1.0, to=20.0, orient=tk.HORIZONTAL,
                           variable=self.y_sensitivity, length=200)
        y_scale.grid(row=1, column=1, padx=10)
        y_value_label = ttk.Label(sensitivity_frame, textvariable=self.y_sensitivity)
        y_value_label.grid(row=1, column=2)
        
        # Inversion settings
        inversion_frame = ttk.LabelFrame(main_frame, text="Axis Inversion", padding="10")
        inversion_frame.pack(fill=tk.X, pady=(0, 10))
        
        invert_x_check = ttk.Checkbutton(inversion_frame, text="Invert Yaw (X Axis)", variable=self.invert_x)
        invert_x_check.pack(anchor=tk.W, pady=5)
        
        invert_y_check = ttk.Checkbutton(inversion_frame, text="Invert Pitch (Y Axis)", variable=self.invert_y)
        invert_y_check.pack(anchor=tk.W, pady=5)
        
        # Controller settings
        controller_frame = ttk.LabelFrame(main_frame, text="Controller Settings", padding="10")
        controller_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Controller stick selection
        ttk.Label(controller_frame, text="Control Stick:").pack(anchor=tk.W, pady=(0, 5))
        
        stick_frame = ttk.Frame(controller_frame)
        stick_frame.pack(fill=tk.X)
        
        left_stick_radio = ttk.Radiobutton(stick_frame, text="Left Stick", 
                                         variable=self.controller_stick, value="left")
        left_stick_radio.pack(side=tk.LEFT, padx=10)
        
        right_stick_radio = ttk.Radiobutton(stick_frame, text="Right Stick", 
                                          variable=self.controller_stick, value="right")
        right_stick_radio.pack(side=tk.LEFT, padx=10)
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(main_frame, text="Advanced Settings", padding="10")
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Smoothing frames
        ttk.Label(advanced_frame, text="Smoothing Frames:").grid(row=0, column=0, sticky=tk.W, pady=5)
        smoothing_scale = ttk.Scale(advanced_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                  variable=self.smoothing_frames, length=200)
        smoothing_scale.grid(row=0, column=1, padx=10)
        smoothing_value_label = ttk.Label(advanced_frame, textvariable=self.smoothing_frames)
        smoothing_value_label.grid(row=0, column=2)
        
        # Show face mesh
        show_mesh_check = ttk.Checkbutton(advanced_frame, text="Show Face Mesh", 
                                        variable=self.show_face_mesh)
        show_mesh_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Control buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=10)
        
        self.start_button = ttk.Button(buttons_frame, text="Start Tracking", 
                                    command=self.start_tracking)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.calibrate_button = ttk.Button(buttons_frame, text="Recalibrate", 
                                       command=self.request_calibration, state=tk.DISABLED)
        self.calibrate_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop Tracking", 
                                   command=self.stop_tracking, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Information display (for FPS, orientation values)
        self.info_frame = ttk.LabelFrame(main_frame, text="Live Information", padding="10")
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fps_var = tk.StringVar(value="FPS: --")
        self.orientation_var = tk.StringVar(value="Yaw: -- Pitch: --")
        
        ttk.Label(self.info_frame, textvariable=self.fps_var).pack(anchor=tk.W, pady=2)
        ttk.Label(self.info_frame, textvariable=self.orientation_var).pack(anchor=tk.W, pady=2)
        
        # Instructions
        instructions = ttk.Label(main_frame, text="Instructions:\n"
                               "• Adjust settings in real-time while tracking\n"
                               "• Press 'Start Tracking' to begin\n"
                               "• Use 'Recalibrate' to set neutral position\n"
                               "• Press 'Stop Tracking' when finished",
                               justify=tk.LEFT)
        instructions.pack(pady=(0, 10))
    
    def settings_changed(self, *args):
        """Send updated settings to the tracking thread"""
        if self.running:
            settings = self.get_settings()
            self.settings_queue.put(settings)
    
    def start_tracking(self):
        """Signal to start the tracking thread"""
        self.running = True
        self.settings_queue.put({"command": "start", **self.get_settings()})
        self.start_button.config(state=tk.DISABLED)
        self.calibrate_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running")
        self.status_indicator.itemconfig(1, fill="green")
    
    def stop_tracking(self):
        """Signal to stop the tracking thread"""
        self.running = False
        self.settings_queue.put({"command": "stop"})
        self.start_button.config(state=tk.NORMAL)
        self.calibrate_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped")
        self.status_indicator.itemconfig(1, fill="red")
    
    def request_calibration(self):
        """Signal to recalibrate head position"""
        self.settings_queue.put({"command": "calibrate"})
    
    def on_closing(self):
        """Handle window close event"""
        if self.running:
            self.stop_tracking()
        self.should_close = True
        self.settings_queue.put({"command": "exit"})
        self.root.destroy()
    
    def update_info(self, fps, yaw, pitch):
        """Update the information display with live tracking data"""
        self.fps_var.set(f"FPS: {fps:.1f}")
        self.orientation_var.set(f"Yaw: {yaw:.2f} Pitch: {pitch:.2f}")
    
    def get_settings(self):
        """Get current settings values"""
        return {
            'x_sensitivity': self.x_sensitivity.get(),
            'y_sensitivity': self.y_sensitivity.get(),
            'invert_x': self.invert_x.get(),
            'invert_y': self.invert_y.get(),
            'smoothing_frames': int(self.smoothing_frames.get()),
            'show_face_mesh': self.show_face_mesh.get(),
            'controller_stick': self.controller_stick.get()
        }
    
    def run(self):
        """Run the Tkinter main loop"""
        self.root.mainloop()

class HeadOrientationController:
    def __init__(self, settings_queue, info_queue):
        self.settings_queue = settings_queue
        self.info_queue = info_queue
        self.settings = None
        
        # Configure face mesh with optimized settings
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            static_image_mode=False
        )
        
        # Initialize virtual Xbox controller 
        # Using vgamepad to create an Xbox 360 virtual controller
        try:
            self.gamepad = vg.VX360Gamepad()
            print("Virtual Xbox 360 controller initialized successfully")
        except Exception as e:
            print(f"Error initializing virtual controller: {e}")
            print("Make sure vgamepad is properly installed and ViGEmBus driver is running")
            raise
        
        # Key landmark indices for orientation tracking
        self.NOSE_TIP = 1
        self.FOREHEAD = 151
        self.CHIN = 199
        self.LEFT_TEMPLE = 162
        self.RIGHT_TEMPLE = 389
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        
        # Smoothing buffers
        self.yaw_buffer = deque(maxlen=10)  # Will be updated from settings
        self.pitch_buffer = deque(maxlen=10)
        
        # Calibration data
        self.center_yaw = None
        self.center_pitch = None
        self.is_calibrated = False
        self.calibration_requested = False
        
        # Initialize virtual Xbox controller
        self.gamepad = vg.VX360Gamepad()
        
        # For FPS calculation
        self.last_time = time.time()
        self.fps = 0
        
        # Control flags
        self.running = False
        self.exit_requested = False
    
    def update_settings(self, new_settings):
        """Update controller settings with new values"""
        if not self.settings:
            self.settings = new_settings
            return
        
        # If smoothing frames changed, resize the buffers
        if 'smoothing_frames' in new_settings and new_settings['smoothing_frames'] != self.settings['smoothing_frames']:
            new_size = new_settings['smoothing_frames']
            
            # Create new buffers with the updated size
            new_yaw_buffer = deque(maxlen=new_size)
            new_pitch_buffer = deque(maxlen=new_size)
            
            # Preserve existing values (up to the new size)
            new_yaw_buffer.extend(list(self.yaw_buffer)[-new_size:])
            new_pitch_buffer.extend(list(self.pitch_buffer)[-new_size:])
            
            self.yaw_buffer = new_yaw_buffer
            self.pitch_buffer = new_pitch_buffer
        
        # Update all settings
        self.settings.update(new_settings)
    
    def calculate_head_orientation(self, face_landmarks):
        """Calculate head orientation (yaw and pitch) based on facial landmarks"""
        # 3D coordinates for key landmarks
        nose = np.array([
            face_landmarks[self.NOSE_TIP].x,
            face_landmarks[self.NOSE_TIP].y,
            face_landmarks[self.NOSE_TIP].z
        ])
        
        forehead = np.array([
            face_landmarks[self.FOREHEAD].x,
            face_landmarks[self.FOREHEAD].y,
            face_landmarks[self.FOREHEAD].z
        ])
        
        chin = np.array([
            face_landmarks[self.CHIN].x,
            face_landmarks[self.CHIN].y,
            face_landmarks[self.CHIN].z
        ])
        
        left_temple = np.array([
            face_landmarks[self.LEFT_TEMPLE].x,
            face_landmarks[self.LEFT_TEMPLE].y,
            face_landmarks[self.LEFT_TEMPLE].z
        ])
        
        right_temple = np.array([
            face_landmarks[self.RIGHT_TEMPLE].x,
            face_landmarks[self.RIGHT_TEMPLE].y,
            face_landmarks[self.RIGHT_TEMPLE].z
        ])
        
        # Calculate yaw (horizontal rotation) using left-right temple positions
        yaw = (right_temple[2] - left_temple[2])
        
        # Calculate pitch (vertical rotation) using forehead-chin axis
        pitch = (chin[2] - forehead[2])
        
        return yaw, pitch
    
    def calibrate(self):
        """Calibration to find neutral head orientation"""
        print("CALIBRATION: Please look straight at the screen")
        print("Calibrating for 2 seconds...")
        
        calibration_yaw = []
        calibration_pitch = []
        
        cv2.namedWindow('Head Orientation Controller')
        
        # Visual countdown for calibration
        start_time = time.time()
        countdown_duration = 3  # 3 second countdown
        
        while time.time() - start_time < countdown_duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            remaining = countdown_duration - (time.time() - start_time)
            cv2.putText(frame, f"CALIBRATION IN: {remaining:.1f}s", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            cv2.putText(frame, "Look straight at screen", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            
            cv2.imshow('Head Orientation Controller', frame)
            cv2.waitKey(1)
        
        # Actual calibration data collection
        start_time = time.time()
        calibration_duration = 2  # 2 second calibration
        
        while time.time() - start_time < calibration_duration:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0].landmark
                yaw, pitch = self.calculate_head_orientation(face_landmarks)
                calibration_yaw.append(yaw)
                calibration_pitch.append(pitch)
            
            elapsed = time.time() - start_time
            cv2.putText(frame, f"Calibrating... {calibration_duration - elapsed:.1f}s", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Hold still", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Head Orientation Controller', frame)
            cv2.waitKey(1)
        
        if calibration_yaw and calibration_pitch:
            self.center_yaw = np.mean(calibration_yaw)
            self.center_pitch = np.mean(calibration_pitch)
            self.is_calibrated = True
            print(f"Calibration complete! Center Yaw: {self.center_yaw:.3f}, Pitch: {self.center_pitch:.3f}")
            
            # Clear buffers after calibration
            self.yaw_buffer.clear()
            self.pitch_buffer.clear()
        else:
            print("Calibration failed - no face detected")
    
    def get_normalized_orientation(self, face_landmarks):
        """Extract head orientation and normalize based on calibration"""
        yaw, pitch = self.calculate_head_orientation(face_landmarks)
        
        if self.is_calibrated:
            # Normalize based on calibration and apply sensitivity
            normalized_yaw = (yaw - self.center_yaw) * self.settings['x_sensitivity']
            normalized_pitch = (pitch - self.center_pitch) * self.settings['y_sensitivity']
        else:
            # Fallback if not calibrated
            normalized_yaw = yaw * self.settings['x_sensitivity']
            normalized_pitch = pitch * self.settings['y_sensitivity']
        
        # Clamp values between -1 and 1 for controller input
        normalized_yaw = max(-1, min(1, normalized_yaw))
        normalized_pitch = max(-1, min(1, normalized_pitch))
        
        return normalized_yaw, normalized_pitch
    
    def check_for_commands(self):
        """Check for commands and settings updates from the GUI thread"""
        try:
            # Non-blocking queue check
            while not self.settings_queue.empty():
                message = self.settings_queue.get(block=False)
                
                if "command" in message:
                    command = message.pop("command")
                    
                    if command == "start":
                        self.running = True
                        self.update_settings(message)
                    elif command == "stop":
                        self.running = False
                        # Reset controller when stopped
                        self.gamepad.reset()
                        self.gamepad.update()
                    elif command == "calibrate":
                        self.calibration_requested = True
                    elif command == "exit":
                        self.exit_requested = True
                        self.running = False
                else:
                    # Regular settings update
                    self.update_settings(message)
                
                self.settings_queue.task_done()
        except queue.Empty:
            pass
    
    def run(self):
        """Main tracking loop with live settings updates"""
        while not self.exit_requested:
            # Check for commands and settings updates
            self.check_for_commands()
            
            if self.running:
                # Handle calibration request
                if self.calibration_requested:
                    self.calibrate()
                    self.calibration_requested = False
                
                # If not calibrated yet, do initial calibration
                if not self.is_calibrated:
                    self.calibrate()
                
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Calculate FPS
                current_time = time.time()
                dt = current_time - self.last_time
                if dt > 0:
                    self.fps = 1.0 / dt
                self.last_time = current_time
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)
                
                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0].landmark
                    yaw, pitch = self.get_normalized_orientation(face_landmarks)
                    
                    # Update buffers
                    self.yaw_buffer.append(yaw)
                    self.pitch_buffer.append(pitch)
                    
                    # Calculate smoothed orientations
                    if len(self.yaw_buffer) > 0 and len(self.pitch_buffer) > 0:
                        smoothed_yaw = sum(self.yaw_buffer) / len(self.yaw_buffer)
                        smoothed_pitch = sum(self.pitch_buffer) / len(self.pitch_buffer)
                        
                        # Apply inversion if enabled
                        final_yaw = -smoothed_yaw if self.settings['invert_x'] else smoothed_yaw
                        final_pitch = -smoothed_pitch if self.settings['invert_y'] else smoothed_pitch
                        
                        # Update controller based on selected stick
                        if self.settings['controller_stick'] == 'left':
                            self.gamepad.left_joystick_float(x_value_float=final_yaw, y_value_float=final_pitch)
                        else:
                            self.gamepad.right_joystick_float(x_value_float=final_yaw, y_value_float=final_pitch)
                        self.gamepad.update()  # Send updated controller state
                        
                        # Send tracking info to the GUI
                        self.info_queue.put({
                            'fps': self.fps,
                            'yaw': final_yaw,
                            'pitch': final_pitch
                        })
                        
                        # Draw face mesh if enabled
                        if self.settings['show_face_mesh']:
                            for landmark in face_landmarks:
                                x = int(landmark.x * frame.shape[1])
                                y = int(landmark.y * frame.shape[0])
                                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        
                        # Visualize head orientation vectors
                        nose_x = int(face_landmarks[self.NOSE_TIP].x * frame.shape[1])
                        nose_y = int(face_landmarks[self.NOSE_TIP].y * frame.shape[0])
                        
                        # Draw yaw vector (horizontal)
                        yaw_end_x = int(nose_x + final_yaw * 50)
                        cv2.line(frame, (nose_x, nose_y), (yaw_end_x, nose_y), (255, 0, 0), 2)
                        
                        # Draw pitch vector (vertical)
                        pitch_end_y = int(nose_y + final_pitch * 50)
                        cv2.line(frame, (nose_x, nose_y), (nose_x, pitch_end_y), (0, 0, 255), 2)
                        
                        # Display info
                        cv2.putText(frame, f"FPS: {self.fps:.1f} | {self.settings['controller_stick'].title()} Stick", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        cv2.putText(frame, f"Sensitivity - Yaw: {self.settings['x_sensitivity']:.1f} Pitch: {self.settings['y_sensitivity']:.1f}", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        cv2.putText(frame, f"Smoothing: {self.settings['smoothing_frames']} frames", 
                                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                else:
                    # Reset selected stick to center when no face is detected
                    if self.settings['controller_stick'] == 'left':
                        # Reset left stick to neutral position (0,0)
                        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
                    else:
                        # Reset right stick to neutral position (0,0)
                        self.gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
                    # Send the updated controller state
                    self.gamepad.update()
                    
                    # Display warning that face is not detected
                    cv2.putText(frame, "No face detected", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "Controller stick centered", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow('Head Orientation Controller', frame)
                
                # Check for key press to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    self.exit_requested = True
            else:
                # Small delay when not running to prevent CPU overuse
                time.sleep(0.1)
                
                # Still check for key press to quit even when not running
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.exit_requested = True
        
        # Clean up
        print("Exiting...")
        # Properly reset the virtual controller
        try:
            self.gamepad.reset()  # Reset all controller inputs
            self.gamepad.update()  # Send the reset state
            print("Virtual controller reset successfully")
        except Exception as e:
            print(f"Error resetting controller: {e}")
            
        # Release camera resources
        self.cap.release()
        # Close all OpenCV windows
        cv2.destroyAllWindows()

def update_gui(settings_window, info_queue):
    """Function to update the GUI with tracking information"""
    while True:
        try:
            if settings_window.should_close:
                break
                
            # Non-blocking check for new info
            try:
                info = info_queue.get(block=False)
                settings_window.update_info(info['fps'], info['yaw'], info['pitch'])
                info_queue.task_done()
            except queue.Empty:
                pass
            
            # Update the GUI
            settings_window.root.update()
            time.sleep(0.03)  # 30 fps update rate for GUI
        except tk.TclError:
            # Window has been destroyed
            break

if __name__ == "__main__":
    # Create queues for thread communication
    settings_queue = queue.Queue()
    info_queue = queue.Queue()
    
    # Create the settings window
    settings_window = SettingsWindow(settings_queue)
    
    # Create and start the tracking controller in a separate thread
    tracker = HeadOrientationController(settings_queue, info_queue)
    tracking_thread = threading.Thread(target=tracker.run)
    tracking_thread.daemon = True
    tracking_thread.start()
    
    # Create and start the GUI update thread
    gui_update_thread = threading.Thread(target=update_gui, args=(settings_window, info_queue))
    gui_update_thread.daemon = True
    gui_update_thread.start()
    
    # Run the settings window (main thread)
    try:
        settings_window.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
    
    # Wait for threads to finish
    if tracking_thread.is_alive():
        tracker.exit_requested = True
        tracking_thread.join(timeout=1.0)
    
    print("Program terminated.")