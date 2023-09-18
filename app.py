import os, sys
import webhook

# from pyngrok import ngrok
from flask import Flask, request, abort, send_from_directory
from linebot.exceptions import InvalidSignatureError

# import google.cloud.logging
# from google.cloud.logging.handlers import CloudLoggingHandler

# client = google.cloud.logging.Client()
# bot_event_handler = CloudLoggingHandler(client,name="gym_bot_event")
# bot_event_logger=logging.getLogger('gym_bot_event')
# bot_event_logger.setLevel(logging.INFO)
# bot_event_logger.addHandler(bot_event_handler)

sys.path.append(".")

# create flask server app
app = Flask(__name__)

# create line webhook handler & lins bot api
handler = webhook.handler
api = webhook.api


# define access point
@app.route("/", methods=["POST"])
def callback():
    # get request body as text
    body = request.get_data(as_text=True)

    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # logging
    # bot_event_logger.info(body)
    # f = open("log/event.log", "a")
    # f.write(body)
    # f.close()

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# route summary.jpg at app-url/images/filename
@app.route('/images/<path:filename>', methods=["GET","POST"])
def serve_image(filename):
    return send_from_directory('tmp/sums', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    # # Open a ngrok tunnel to the HTTP server
    # port = 5000
    # public_url = ngrok.connect(port).public_url
    # print(' * ngrok tunnel {} -> http://127.0.0.1:{}'.format(public_url, port))

    # start the server
    # app.run()
