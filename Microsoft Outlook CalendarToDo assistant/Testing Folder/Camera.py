import cv2 
import face_recognition
import os 


#Test out facial recoginizations
known_faces_dir = 'Testing Folder/Known_faces'
known_encodings = [] #Known faces encoding
known_names = [] #KNown faces name

if os.path.exists(known_faces_dir):
    for filename in os.listdir(known_faces_dir):
        person_file_path = os.path.join(known_faces_dir, filename)
        
        for person_name in os.listdir(person_file_path):
            image_path = os.path.join(person_file_path, person_name)
            print(image_path)#Logging
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])  # Use the first encoding
                known_names.append(os.path.splitext(filename)[0])  # Use filename as label
        print('known faces lodaded and encoded')
else:
    print('No file called KnownFace')


cap = cv2.VideoCapture(0)

running = True

while running:
    ret, frame = cap.read() #Checks if frames was successfully captured then save the frame onto 'frame'
    
    if not ret:
        print('failed to grab ret')
        break
    
    smaller_frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    
    rgb_frame = cv2.cvtColor(smaller_frame, cv2.COLOR_BGR2RGB) #Changes the BGR to RGB which is required for facial recognization
     
    frame_count = 0
    if frame_count % 5 == 0:  # Process every 5th frame
        face_locations = face_recognition.face_locations(rgb_frame, model='hog') #Detects faces 
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations) #Encodes the faces 
        
        
        #Compares the seen face to known faces
        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, encoding)
            name = "Unknown"
            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index] 
                print('detected' + name)
                running = False #breaks the finding person function once a detected person is found
    frame_count += 1
    


#Lets go all of resouces such as the cam etc
cap.release()
cv2.destroyAllWindows()