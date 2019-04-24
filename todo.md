## Face Recognition app TODO
---------------------------------

* Tracking
    * Track detections by IOU
        * settings.py IOU params, ttl DONE
        * Ignore prob for now

* TTS
    * Record if id was greeted
    * greet person is id was not greeted
    * use gTTS
    
* Unrecognized faces save
    * save only face (without background)
    
* Styling
    * Fix margin issue for topbar DONE
    * Add icon  of tick or ? to the right indicating if the person was recognized DONE
    * Add image of person being recognized (default avatr icon if not recog) to the left DONE 
    * Better styling in general DONE
    
* Make updates to the embedding npz file incremental DONE
    * Store the filename of the image from which the embedding was computed DONE
    * Don't recompute embeddings for old images DONE

* Config and training
    * Save pictures of unrecognized people DONE
    * Config UI: Training mode and retrain button (DONT)     
    * Add training mode: select a person and capture images of his/her face.(DONT)
    * Add person CRUD (DONT)
    

* Links    
    * https://www.hackster.io/mjrobot/video-streaming-web-server-ef11e3
    * https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
    * https://medium.com/@generativist/a-simple-streaming-http-server-in-aiohttp-4233dbc173c7
    
