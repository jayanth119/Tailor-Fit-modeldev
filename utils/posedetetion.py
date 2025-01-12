import cv2
import mediapipe as mp

class PoseAndHandDetector:
    def __init__(self, pose_complexity=2, max_hands=2):
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        # self.mp_drawing = mp.solutions.drawing_utils
        
        self.pose = self.mp_pose.Pose(static_image_mode=True, model_complexity=pose_complexity)
        self.hands = self.mp_hands.Hands(static_image_mode=True, max_num_hands=max_hands, min_detection_confidence=0.5)

    def is_single_person_detected(self, pose_results):
        """
        checks if there is exactly one person in the image based on the visibility of landmarks.
        returns True if a single person is detected, otherwise False.
        """
        if pose_results.pose_landmarks:
            visible_landmarks = [lm.visibility for lm in pose_results.pose_landmarks.landmark if lm.visibility > 0.5]
            return len(visible_landmarks) >= 10  # Arbitrary threshold for sufficient points
        return False

    def extract_leg_coordinates(self, image_path):
        """
        extracts leg coordinates if a single person is detected in the image.
        """
        image = cv2.imread(image_path)
        if image is None:
            print("Error: Image not found or could not be loaded.")
            return

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(image_rgb)

        # Ensure only one person is detected
        if not self.is_single_person_detected(pose_results):
            print("More than one person or unclear pose detected. Function not executed.")
            return

        height, width, _ = image.shape
        leg_coordinates = {}
        lower_body_points = [
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
            self.mp_pose.PoseLandmark.LEFT_KNEE,
            self.mp_pose.PoseLandmark.RIGHT_KNEE,
            self.mp_pose.PoseLandmark.LEFT_ANKLE,
            self.mp_pose.PoseLandmark.RIGHT_ANKLE,
            self.mp_pose.PoseLandmark.LEFT_HEEL,
            self.mp_pose.PoseLandmark.RIGHT_HEEL,
            self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
            self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX,
        ]
        result  = []
        for point in lower_body_points:
            landmark = pose_results.pose_landmarks.landmark[point]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            leg_coordinates[point.name] = (x, y)
            result.append((point.name, x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

        # self.mp_drawing.draw_landmarks(
        #     image,
        #     pose_results.pose_landmarks,
        #     self.mp_pose.POSE_CONNECTIONS,
        #     self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        # )
        return result
        # Save the processed image with leg landmarks
        # output_path = "output_lower_body_with_coords.jpg"
        # cv2.imwrite(output_path, image)
        # print(f"Processed image with leg landmarks saved at {output_path}")
        # print("Extracted leg coordinates:", leg_coordinates)

    def extract_body_and_hand_keypoints(self, image_path):
        """
        extracts body and hand keypoints if a single person is detected in the image.
        """
        image = cv2.imread(image_path)
        if image is None:
            print("Error: Image not found or could not be loaded.")
            return

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(image_rgb)
        hand_results = self.hands.process(image_rgb)
        result =  []

        # Ensure only one person is detected
        if not self.is_single_person_detected(pose_results):
            print("More than one person or unclear pose detected. Function not executed.")
            return

        height, width, _ = image.shape
        body_points = [
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_ELBOW,
            self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
            self.mp_pose.PoseLandmark.LEFT_KNEE,
            self.mp_pose.PoseLandmark.RIGHT_KNEE,
            self.mp_pose.PoseLandmark.LEFT_ANKLE,
            self.mp_pose.PoseLandmark.RIGHT_ANKLE,
        ]

        for point in body_points:
            landmark = pose_results.pose_landmarks.landmark[point]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    result.append((point.name, x, y))
                    cv2.circle(image, (x, y), 3, (0, 0, 255), -1)
        return result
        # output_path = "output_body_and_hands.jpg"
        # cv2.imwrite(output_path, image)
        # print(f"Processed image with body and hand keypoints saved at {output_path}")

    def close(self):
        """
        release resources.
        """
        self.pose.close()
        self.hands.close()

if __name__ == "__main__":
   
  detector = PoseAndHandDetector()
  image_path = "/input/2top.jpg"
  print(detector.extract_leg_coordinates(image_path))
  print(detector.extract_body_and_hand_keypoints(image_path))
  detector.close()