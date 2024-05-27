from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def gen_key(file_path, size_in_mb):
    size_in_bytes = size_in_mb * 1024 * 1024  # Convert size from MB to bytes
    binary_key = os.urandom(size_in_bytes)  # Generate random binary data
    
    with open(file_path, 'wb') as file:
        file.write(binary_key)  # Save the binary data to a file
    
    return binary_key

def encrypt_aes(key, filename):
    if len(key) < 32:
        raise ValueError("Key must be at least 32 bytes long.")
    
    iv = os.urandom(16)  # Generate a random initialization vector (IV)
    cipher = Cipher(algorithms.AES(key[:32]), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    with open(filename, 'rb') as file:
        file_data = file.read()
    
    encrypted_data = encryptor.update(file_data) + encryptor.finalize()
    
    prefix = b'ENCRYPTED'  # Known prefix to indicate the file is encrypted
    with open(filename, 'wb') as encrypted_file:
        encrypted_file.write(prefix + iv + encrypted_data)  # Save prefix, IV, and encrypted data together

def decrypt_aes(key, filename):
    if len(key) < 32:
        raise ValueError("Key must be at least 32 bytes long.")

    with open(filename, 'rb') as encrypted_file:
        prefix = encrypted_file.read(9)  # Read the prefix
        if prefix != b'ENCRYPTED':
            raise ValueError("File is not encrypted with the expected prefix.")
        
        iv = encrypted_file.read(16)  # Read the IV
        encrypted_data = encrypted_file.read()  # Read the rest of the file (the encrypted data)
    
    cipher = Cipher(algorithms.AES(key[:32]), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    with open(filename, 'wb') as file:
        file.write(decrypted_data)  # Write the decrypted data back to the file

def get_key(filename):
    with open(filename, 'rb') as file:
        key = file.read()
    return key

def is_file_encrypted(filename):
    try:
        with open(filename, 'rb') as file:
            prefix = file.read(9)  # Read the prefix
            return prefix == b'ENCRYPTED'
    except IOError:
        print("File not accessible or doesn't exist.")
        return False