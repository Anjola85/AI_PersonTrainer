import cv2
import numpy as np
import time

import PoseModule as pm
import os
from AudioCommSys import text_to_speech
import threading

class utilities():
    def __init__(self) -> None:
        pass    

    def illustrate_exercise(self, example, exercise):  
        seconds = 3
        img = cv2.imread(example)
        img = cv2.resize(img, (980, 550))
        cv2.imshow("Exercise Illustration", img)  
        cv2.waitKey(1)
        
        instruction = "Up next is " + exercise + " IN!"

        if exercise != "Warm Up":
            text_to_speech(instruction)

        while seconds > 0:
            img = cv2.imread(example)
            img = cv2.resize(img, (980, 550))

            time.sleep(1)
            speaker_thread = threading.Thread(target=text_to_speech, args=(str(int(seconds))), kwargs={})
            speaker_thread.start()
            cv2.putText(img, exercise + " in: " + str(int(seconds)) , (350, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)    
            cv2.imshow("Exercise Illustration", img)  
            seconds -= 1
            cv2.waitKey(1)
        cv2.destroyAllWindows()

    def repitition_counter(self, per, count, direction):
        if (per == 100 and direction == 0):
            count += 0.5
            direction = 1
        if (per == 0 and direction == 1):
            count += 0.5
            direction = 0
            if int(count) != 0:
                speaker_thread = threading.Thread(target=text_to_speech, args=(str(int(count))), kwargs={})
                speaker_thread.start()
        return {"count": count, "direction":  direction}

    def display_rep_count(self, img, count, total_reps):
        cv2.rectangle(img, (0, 0), (550, 300), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, str(int(count)) + "/"+ str(total_reps), (40, 220), cv2.FONT_HERSHEY_PLAIN, 15, (0, 0, 255), 25)  


    def get_performance_bar_color(self, per):
        color =  (0, 205, 205)
        if 0 < per <= 30:
            color = (51, 51, 255)
        if 30 < per <= 60:
            color = (0, 165, 255)
        if 60 <= per <= 100:
            color = (0, 255, 255)
        return color

    def draw_performance_bar(self, img, per, bar, color, count):
        cv2.rectangle(img, (1600, 100), (1675, 650), color, 3)
        cv2.rectangle(img, (1600, int(bar)), (1675, 650), color, cv2.FILLED)
        cv2.putText(img, f'{int(per)} %', (1600, 75), cv2.FONT_HERSHEY_PLAIN, 4, color, 4)

class simulate_warmup():
    def __init__(self, difficulty_level = 1, reps=2, calories_burned = 0):
        self.reps = reps
        self.difficulty_level = difficulty_level
        self.calories_burned = calories_burned

    def skip(self):
        utilities().illustrate_exercise("TrainerImages/skip_illustration.jpeg", "Warm Up")
        cap = cv2.VideoCapture("TrainerData/gym_day_skip.mov")
        detector = pm.posture_detector()
        count = 0
        direction = 0
        start = time.process_time()
        total_reps = self.reps * self.difficulty_level * 3

        while count < total_reps:
            success, img = cap.read()
            img = detector.find_person(img, False)  
            landmark_list = detector.find_landmarks(img, False)

            if len(landmark_list) != 0:
                left_arm_angle = detector.find_angle(img, 11, 13, 15)
                right_arm_angle = detector.find_angle(img, 12, 14, 16)

                left_leg_angle = detector.find_angle(img, 24, 26, 28)
                right_leg_angle = detector.find_angle(img, 23, 25, 27)

                per = np.interp(left_arm_angle, (130, 145), (0, 100))
                bar = np.interp(left_arm_angle, (130, 145), (650, 100))

                color = utilities().get_performance_bar_color(per)
                # When exercise is in start or terminal state
                if per == 100 or per == 0:
                    color = (0, 255, 0)
                    rep = utilities().repitition_counter(per, count, direction)
                    count = rep["count"]
                    direction = rep["direction"]

                utilities().draw_performance_bar(img, per, bar, color, count)
            
            utilities().display_rep_count(img, count, total_reps)
            cv2.imshow("Skipping", img)
            cv2.waitKey(1)
        time_elapsed = int(time.process_time() - start)

        # Calorie calculator: Duration (in minutes)*(MET*3.5*weight in kg)/200
        calories_burned = int((time_elapsed/60) * ((8.0 * 3.5 * 64 )/50))

        return {"calories": calories_burned, "time_elapsed": time_elapsed}


class simulate_target_exercies():
    def __init__(self, difficulty_level=1, reps=2):
        self.reps= reps
        self.difficulty_level = difficulty_level

    def push_ups(self):
        utilities().illustrate_exercise("TrainerImages/push_up_illustration.jpeg", "PUSH UP'S")
        cap = cv2.VideoCapture("TrainerData/push_ups.mp4")
        detector = pm.posture_detector()
        count = 0
        direction = 0
        start = time.process_time()
        total_reps = self.reps * self.difficulty_level

        while count < total_reps:
            success, img = cap.read()
            img = detector.find_person(img, False)    
            landmark_list = detector.find_landmarks(img, False)

            if len(landmark_list) != 0:
                left_arm_angle = detector.find_angle(img, 11, 13, 15)
                right_arm_angle = detector.find_angle(img, 12, 14, 16)

                per = np.interp(left_arm_angle, (220, 280), (0, 100))
                bar = np.interp(left_arm_angle, (220, 280), (650, 100))
        
                color = utilities().get_performance_bar_color(per)
                # When exercise is in start or terminal state
                if per == 100 or per == 0:
                    color = (0, 255, 0)
                    rep = utilities().repitition_counter(per, count, direction)
                    count = rep["count"]
                    direction = rep["direction"]
                utilities().draw_performance_bar(img, per, bar, color, count)

            utilities().display_rep_count(img, count, total_reps)
            cv2.imshow("Push Ups", img)
            cv2.waitKey(1)
            if count == (self.reps * self.difficulty_level):
                break
            time_elapsed = int(time.process_time() - start)
            calories_burned = (time_elapsed/60) * ((4.0 * 3.5 * 64 )/200)

        return {"calories": calories_burned, "time_elapsed": time_elapsed}

    def bicep_curls(self):
        utilities().illustrate_exercise("TrainerImages/bicep_curls_illustration.jpeg", "BICEP CURLS")
        cap = cv2.VideoCapture("TrainerData/bicep_curls.mov")
        detector = pm.posture_detector()
        count = 0
        direction = 0
        start = time.process_time()
        total_reps = self.reps * self.difficulty_level

        while count < total_reps:
            success, img = cap.read()
            img = detector.find_person(img, False)
            landmark_list = detector.find_landmarks(img, False)

            if len(landmark_list) != 0:
                right_arm_angle = detector.find_angle(img, 12, 14, 16)

                per = np.interp(right_arm_angle, (50, 160), (0, 100))
                bar = np.interp(right_arm_angle, (50, 160), (650, 100))
               
                color = utilities().get_performance_bar_color(per)
                # When exercise is in start or terminal state
                if per == 100 or per == 0:
                    color = (0, 255, 0)
                    rep = utilities().repitition_counter(per, count, direction)
                    count = rep["count"]
                    direction = rep["direction"]
                utilities().draw_performance_bar(img, per, bar, color, count)

            utilities().display_rep_count(img, count, total_reps)
            cv2.imshow("Image", img)
            cv2.waitKey(1)

            time_elapsed = int(time.process_time() - start)
            calories_burned = (time_elapsed/60) * ((4.0 * 3.5 * 64 )/200)
        return {"calories": calories_burned, "time_elapsed": time_elapsed}

    def mountain_climbers(self):
        utilities().illustrate_exercise("TrainerImages/mountain_climber_illustraion.jpeg", "MOUNTAIN CLIMBERS")
        cap = cv2.VideoCapture("TrainerData/gym_day_climbers.mov")
        detector = pm.posture_detector()
        count = 0
        direction = 0
        start = time.process_time()

        total_reps = self.reps * self.difficulty_level 

        while count < total_reps:
            success, img = cap.read()
            img = detector.find_person(img, False)    
            landmark_list = detector.find_landmarks(img, False)

            if len(landmark_list) != 0:
                left_arm_angle = detector.find_angle(img, 11, 13, 15)
                right_arm_angle = detector.find_angle(img, 12, 14, 16)
                left_leg_angle = detector.find_angle(img, 24, 26, 28)

                right_leg_angle = detector.find_angle(img, 23, 25, 27)

                per = np.interp(right_leg_angle, (220, 280), (0, 100))
                bar = np.interp(right_leg_angle, (220, 280), (650, 100))

                color = utilities().get_performance_bar_color(per)
                # When exercise is in start or terminal state
                if per == 100 or per == 0:
                    color = (0, 255, 0)
                    rep = utilities().repitition_counter(per, count, direction)
                    count = rep["count"]
                    direction = rep["direction"]

                utilities().draw_performance_bar(img, per, bar, color, count)

            utilities().display_rep_count(img, count, total_reps)
            cv2.imshow("Mountain Climbers", img)
            cv2.waitKey(1)
            time_elapsed = int(time.process_time() - start)
            calories_burned = (time_elapsed/60) * ((4.0 * 3.5 * 64 )/200)

        return {"calories": calories_burned, "time_elapsed": time_elapsed}

    def squats(self):
        utilities().illustrate_exercise("TrainerImages/squats_illustration.jpeg", "SQUATS")
        cap = cv2.VideoCapture("TrainerData/gym_day_squats.mov")
        detector = pm.posture_detector()
        count = 0
        direction = 0
        start = time.process_time()

        total_reps = self.reps * self.difficulty_level 

        while count < total_reps:
            success, img = cap.read()
            img = detector.find_person(img, False)    
            landmark_list = detector.find_landmarks(img, False)

            if len(landmark_list) != 0:
                right_leg_angle = detector.find_angle(img, 24, 26, 28)
                left_leg_angle = detector.find_angle(img, 23, 25, 27)

                per = np.interp(left_leg_angle, (190, 240), (0, 100))
                bar = np.interp(left_leg_angle, (190, 240), (650, 100))

                color = utilities().get_performance_bar_color(per)
                # When exercise is in start or terminal state
                if per == 100 or per == 0:
                    color = (0, 255, 0)
                    rep = utilities().repitition_counter(per, count, direction)
                    count = rep["count"]
                    direction = rep["direction"]
                utilities().draw_performance_bar(img, per, bar, color, count)

            utilities().display_rep_count(img, count, total_reps)
            cv2.imshow("Squats", img)
            cv2.waitKey(1)
            time_elapsed = int(time.process_time() - start)
            calories_burned = (time_elapsed/60) * ((4.0 * 3.5 * 64 )/200)
        return {"calories": calories_burned, "time_elapsed": time_elapsed}

class start_workout_session():
    def __init__(self, difficulty_level=1):
        self.difficulty_level = difficulty_level

    def completion_screen(self, congrats_img):
        seconds = 3
        while seconds >= 0:
            img = cv2.imread(congrats_img)
            img = cv2.resize(img, (980, 550))
            cv2.imshow("Image", img)  
            time.sleep(1)
            seconds -= 1
            cv2.waitKey(1)

    def calculate_performance(self, all_exercises):
        total_calories = 0
        time_elapsed = 0
        for exercise in all_exercises:
            total_calories = exercise["calories"] + total_calories
            time_elapsed = exercise["time_elapsed"] + time_elapsed
        return {"calories":  round(total_calories), "time_elapsed": time_elapsed}

    def complete_path(self):
        warm_ups = simulate_warmup(self.difficulty_level)
        target_exercises = simulate_target_exercies(self.difficulty_level)

        skipping_performance =   warm_ups.skip()
        squats_performance = target_exercises.squats()
        mc_performance = target_exercises.mountain_climbers()
        bicep_curls_performance = target_exercises.bicep_curls()
        pushup_performance = target_exercises.push_ups()
        
        overall_performance = [skipping_performance, squats_performance, bicep_curls_performance,  mc_performance, pushup_performance]

        return  self.calculate_performance(overall_performance)

def main():  
    session = start_workout_session()
    performance = session.complete_path()
    print(performance)

if __name__ == "__main__":
    main()
