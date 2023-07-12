import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify

app = Flask(__name__)

# Perform one-time setup tasks
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
model = SentenceTransformer('bert-base-nli-mean-tokens')


# Define API route for cosine similarity calculation
@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity():
    # Get the document texts from the request
    document1 = request.json.get('document1')
    document2 = request.json.get('document2')

    # Preprocess the input text
    topic1 = preprocess_text(document1)
    topic2 = preprocess_text(document2)

    # Calculate cosine similarity
    similarity = calculate_cosine_similarity(topic1, topic2)

    # Return the result as JSON
    return jsonify({'similarityScore': similarity*100})


# Text preprocessing
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    preprocessed_text = ' '.join(lemmatized_tokens)
    return preprocessed_text


# Cosine similarity calculation
def calculate_cosine_similarity(topic1, topic2):
    max_length = 512
    topic1_chunks = [topic1[i:i + max_length] for i in range(0, len(topic1), max_length)]
    topic2_chunks = [topic2[i:i + max_length] for i in range(0, len(topic2), max_length)]
    num_simialar_chunks = 0
    # Calculate the cosine similarity for each chunk
    similarity_sum = 0
    for chunk1 in topic1_chunks:
        for chunk2 in topic2_chunks:
            chunk1_embedding = model.encode([chunk1])[0]
            chunk2_embedding = model.encode([chunk2])[0]
            similarity = cosine_similarity([chunk1_embedding], [chunk2_embedding])[0][0]
            print("Similarity between chunk1 and chunk2 is: ", similarity)
            similarity_sum += similarity
            if similarity > 0.5:
                num_simialar_chunks += 1

    # return the similarity score
    return num_simialar_chunks / (len(topic1_chunks) * len(topic2_chunks))


# Run the Flask application
if __name__ == '__main__':
    app.run()
