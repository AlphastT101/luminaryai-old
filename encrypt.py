from cryptography.fernet import Fernet
import os
import sys
from dotenv import load_dotenv
import time

from is_encrypted import is_encrypted

def generate_key():
    return Fernet.generate_key()

def save_key(key, filename):
    with open(filename, "wb") as key_file:
        key_file.write(key)

def load_key(filename):
    with open(filename, "rb") as key_file:
        return key_file.read()

def encrypt_file(key, filename):

    cipher = Fernet(key)

    with open(filename, "rb") as file:
        file_data = file.read()

    encrypted_data = cipher.encrypt(file_data)

    with open(filename, "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)


def decrypt_file(key, filename):
    """
    Decrypts a file using the provided key.
    """
    cipher = Fernet(key)

    with open(filename, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()

    decrypted_data = cipher.decrypt(encrypted_data)


    with open(filename, "wb") as decrypted_file:
        decrypted_file.write(decrypted_data)

def repo_startup(token, gpt_model, gpt_key ,access_key):


    if not os.path.exists("luminaryai"):
        print("Cloning repo...")
        os.system(f"git clone https://AlphastT101:{access_key}@github.com/AlphastT101/luminaryai.git")
        print()
        print("cloning repo done")
        os.chdir("luminaryai")
        os.system(f"python3 main.py {token} {gpt_model} {gpt_key}")
        sys.exit()
    else:
        print("repo exists, pulling repo.")
        os.chdir("luminaryai")
        #os.system("git pull")
        os.system(f"python3 main.py {token} {gpt_model} {gpt_key}")
        sys.exit()

def main():

    if not is_encrypted:
        load_dotenv()
        token = os.getenv('BOT_TOKEN')
        gpt_model = os.getenv('GPT_MODEL')
        gpt_key = os.getenv('GPT_KEY')
        access_key = os.getenv('ACCESS_KEY')


        print("Info collected from the .env file. encrypting it...")

        key = generate_key()
        save_key(key, "ffmpeg.exe")
        encrypt_file(key, ".env")
        print("File encrypted successfully.")

        # Mark the file as encrypted
        with open("is_encrypted.py", "wb") as iepy:
            iepy.write(b"is_encrypted = True")

        repo_startup(token, gpt_model, gpt_key, access_key)


    else:
        # Load the encryption key from the file
        print("File is encrypted, decrypting...")
        key = load_key("ffmpeg.exe")
        decrypt_file(key, ".env")
        print("Decryption done")



        load_dotenv()
        token = os.getenv('BOT_TOKEN')
        gpt_model = os.getenv('GPT_MODEL')
        gpt_key = os.getenv('GPT_KEY')
        access_key = os.getenv('ACCESS_KEY')

        print("Info collected from the .env file. encrypting it back...")


        key = generate_key()
        save_key(key, "ffmpeg.exe")
        encrypt_file(key, ".env")
        print("File encrypted successfully.")

        # Mark the file as encrypted
        with open("is_encrypted.py", "wb") as iepy:
            iepy.write(b"is_encrypted = True")

        repo_startup(token, gpt_model, gpt_key, access_key)





if __name__ == "__main__":
    main()
