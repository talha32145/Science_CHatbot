from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os

app = Flask(__name__)

encoder_model = load_model("encoder_model2.keras")
decoder_model = load_model("decoder_model2.keras")

with open("encoder_tokenizer.pkl","rb") as f:
    encoder_tokenizer = pickle.load(f)

with open("decoder_tokenizer.pkl","rb") as f:
    decoder_tokenizer = pickle.load(f)

encoder_maxlen=17
decoder_maxlen=54

reverse_dec_word_index = {
    index: word
    for word, index in decoder_tokenizer.word_index.items()
}


def predict_sentence(sentence):

    # ============== Encoder ==============

    input_seq = encoder_tokenizer.texts_to_sequences([sentence])
    if len(input_seq[0]) == 0:
        return "Sorry, I don't understand."

    input_seq = pad_sequences(
        input_seq,
        maxlen=encoder_maxlen,
        padding="post"
    )

    state_h, state_c = encoder_model.predict(input_seq, verbose=0)

    # ============== Decoder ==============

    start_token = decoder_tokenizer.word_index["<start>"]
    end_token = decoder_tokenizer.word_index["<end>"]

    target_seq = np.array([[start_token]])

    decoded_sentence = []

    while True:

        output_tokens, h, c = decoder_model.predict(
            [target_seq, state_h, state_c],
            verbose=0
        )

        sampled_token_index = np.argmax(output_tokens[0, -1, :])

        if sampled_token_index == end_token:
            break

        sampled_word = reverse_dec_word_index.get(sampled_token_index)

        if sampled_word is not None:
            decoded_sentence.append(sampled_word)

        target_seq = np.array([[sampled_token_index]])

        state_h = h
        state_c = c

        if len(decoded_sentence) >= decoder_maxlen:
            break

    return " ".join(decoded_sentence)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data.get("message", "")

    if not message:
        return jsonify({"reply": "Please enter a message."})

    reply = predict_sentence(message)

    return jsonify({
        "reply": reply
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
