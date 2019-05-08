import os

data_dir=os.path.expanduser("~/Dropbox/facerecognition/")
face_database_path=os.path.join(data_dir,"facedb")
capture_path=os.path.join(data_dir,"captured_images")
training_data_file=os.path.join(data_dir,"lidi_training_set.npz")
model_path=os.path.join(data_dir,"lidi_face_model.pkl")

face_image_size=(100,100)


number_of_times_to_upsample=1
frame_skip=8

class Input:
    #stream_url = "/dev/video0"
    stream_url = "rtsp://163.10.22.229/live.sdp"
    # stream_url="http://163.10.22.229/video2.mjpg"
    # ffplay -fflags nobuffer -rtsp_transport udp rtsp://163.10.22.229/live.sdp

    # webcam resolution at capture time
    capture_resolution = (800, 600)
input=Input()

class GUI:
    application_resolution=(800,600)
    #resolution of the display
    display_resolution=input.capture_resolution
    application_name="Bienvenido al III-LIDI"

gui=GUI()


class FaceRecognition:
    LOCALIZATION_HOG="hog"
    LOCALIZATION_CNN = "cnn"
    #
    face_image_extension_factor = 1
    localization_method = LOCALIZATION_HOG

    # downsampling to apply before recognition
    downsampling = 1

    # size of embedding vector the cnn outputs
    embedding_length=128

recognition=FaceRecognition()

class Learning:
    # save images of the faces of people unrecognized by the system
    save_unrecognized_peoples_faces = False
    save_recognized_peoples_faces = False
    save_full_images = False
learning=Learning()

class Sound:
    # True to say the name of the recognized widgets through tts
    voice_greeting_enabled=True
sound=Sound()
class Server:
    bind_ip = '0.0.0.0'
    bind_port = 9876

server=Server()
# SERVER


class TrackingSettings:
    # minimum IoU to consider two detections as belonging to the same object
    iou_threshold = 0.1  # range [0-1]

    # minimum time to live in msecs for a detection window
    ttl_initial = 50

    # minimum time in ms before a prediction is emitted
    warmup_time = 0

    # minimum number of samples in a tracking window before considering
    # an object as unrecognized or  recognized
    minimum_samples = 0

    # minimum average probability to recognize an object
    face_classification_treshold_proba = 0.5

tracking = TrackingSettings()


class Client:
    throttle_requests = 1 / 30
    display_delay = 0
    font="Arial"


client=Client()


class Capture:
    frame_skip=2
    max_elements_in_queue=20
    motion_detection_treshold=0.1

capture=Capture()
