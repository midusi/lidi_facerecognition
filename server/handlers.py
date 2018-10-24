from http.server import BaseHTTPRequestHandler
import pickle
import logging

class RecognitionRequestHandler(BaseHTTPRequestHandler):


    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        paths = {
            '/foo': {'status': 200},
            '/bar': {'status': 302},
            '/baz': {'status': 404},
            '/qux': {'status': 500}
        }

        if self.path in paths:
            self.respond(paths[self.path])
        else:
            self.respond({'status': 500})

    def log_message(self, format, *args):
        message="%s - - [%s] %s\n" %(self.address_string(),
                          self.log_date_time_string(),
                          format % args)

        logging.debug(message)

    def handle_http(self, status_code, path):
        self.send_response(status_code)
        self.send_header('Content-type', ' application/octet-stream')
        self.end_headers()
        w = self.server.recognition_worker
        while not w.tracked_objects_queue.empty():
            self.server.tracked_objects=w.tracked_objects_queue.get()
        # descriptions="\n".join( map(str,objects))
        # content = f"Tracked objects:\n {descriptions}"

        objects = self.server.tracked_objects #w.tracked_objects.copy()
        # logging.info(f"response with {w.tracked_objects} objects ({objects}).")
        pickled_objects = pickle.dumps(objects)
        return pickled_objects

    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.wfile.write(response)
