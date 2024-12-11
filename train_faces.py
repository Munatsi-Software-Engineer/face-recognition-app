import cv2
import os
import numpy as np
import json  # Import json module to save label mapping

# Create a folder to store training images if it doesn't exist
if not os.path.exists('training_images'):
    os.makedirs('training_images')

# Initialize the face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def collect_training_data():
    images = []
    labels = []
    label_dict = {}
    current_label = 0

    for person_name in os.listdir('training_images'):
        person_dir = os.path.join('training_images', person_name)
        if not os.path.isdir(person_dir):
            continue

        label_dict[current_label] = person_name  # Map label to person name

        for image_name in os.listdir(person_dir):
            image_path = os.path.join(person_dir, image_name)
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray)

            for (x, y, w, h) in faces:
                images.append(gray[y:y + h, x:x + w])
                labels.append(current_label)

        current_label += 1

    return images, labels, label_dict

images, labels, label_dict = collect_training_data()

# Train the recognizer
recognizer.train(images, np.array(labels))

# Save the trained model
recognizer.save('training_data.yml')

# Save the label mapping to a JSON file
with open('label_mapping.json', 'w') as f:
    json.dump(label_dict, f)

print("Training complete. Model saved as 'training_data.yml'")
print("Label mapping:", label_dict)