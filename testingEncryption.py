from cryptography.fernet import Fernet
import pymongo
import gridfs
import os

# MongoDB Connection
client = pymongo.MongoClient("mongodb+srv://gaurav552sharma:e1uK6Of6qzRD1zm6@cluster0.aa1wcrb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["face_detection_db"]
fs = gridfs.GridFS(db, collection="encrypted_images")  # Use a new collection

# Encryption Key Storage
KEY_FILE = "encryption_key.key"

def generate_key():
    """Generates a new encryption key and saves it if not already created."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print(" Encryption key generated and saved.")
    else:
        print(" Encryption key already exists.")

def load_key():
    """Loads the existing encryption key."""
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_and_store_image(image_path):
    """Encrypts the image and stores it in MongoDB."""
    key = load_key()
    cipher = Fernet(key)
    
    # Read image as binary
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    
    # Encrypt the image data
    encrypted_data = cipher.encrypt(image_data)

    # Store encrypted image in MongoDB
    image_id = fs.put(encrypted_data, filename="encrypted_test.jpg")
    print(f" Encrypted image stored in MongoDB with ID: {image_id}")

def decrypt_and_save_image(output_path):
    """Retrieves the encrypted image from MongoDB, decrypts it, and saves."""
    key = load_key()
    cipher = Fernet(key)

    # Retrieve encrypted data
    encrypted_file = fs.find_one({"filename": "encrypted_test.jpg"})
    
    if encrypted_file:
        encrypted_data = encrypted_file.read()
        # Decrypt the data
        decrypted_data = cipher.decrypt(encrypted_data)

        # Save decrypted image
        with open(output_path, "wb") as output_file:
            output_file.write(decrypted_data)

        print(f" Decrypted image saved as {output_path}")
    else:
        print(" Encrypted image not found in MongoDB!")

# Run the process
generate_key()  # Generate key if not exists
encrypt_and_store_image("glovevc.jpeg")  # Encrypt & store the image
decrypt_and_save_image("decrypted_test.jpg")  # Decrypt & save image
