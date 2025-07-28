from sentence_transformers import SentenceTransformer

# This is a small but powerful model that is well under the 1GB limit
model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

# Save the model to the 'models' directory
model.save('models/sentence-transformer-model')
print(f"Model '{model_name}' downloaded and saved to 'models/sentence-transformer-model'")