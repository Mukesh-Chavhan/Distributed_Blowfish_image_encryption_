import socket
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import unpad
from PIL import Image
import hashlib
import numpy as np
import os
import time
import sys

BLOCK_SIZE = Blowfish.block_size


def bytes_to_image(byte_data, size, output_path):
    """Convert bytes to an image and save it."""
    try:
        img = Image.frombytes("RGB", size, byte_data)
        img.save(output_path, format="JPEG")
    except Exception as e:
        print(f"Error converting bytes to image: {e}")


def save_as_visual_encrypted_image(encrypted_data, size, output_path):
    """Save the encrypted data as a visual image."""
    encrypted_pixels = encrypted_data[BLOCK_SIZE:]
    expected_bytes = size[0] * size[1] * 3  # RGB image
    encrypted_pixels = encrypted_pixels[:expected_bytes]

    encrypted_array = np.frombuffer(encrypted_pixels, dtype=np.uint8)
    encrypted_image = encrypted_array.reshape((size[1], size[0], 3))

    encrypted_img = Image.fromarray(encrypted_image, "RGB")
    encrypted_img.save(output_path)


def decrypt_image(encrypted_data, key, size, decrypted_image_path):
    """Decrypt the image and save it."""
    iv = encrypted_data[:BLOCK_SIZE]
    encrypted_image_data = encrypted_data[BLOCK_SIZE:]

    cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv=iv)

    try:
        print("Decrypting image...")
        dynamic_progress_bar("Decrypting", duration=5)  # Progress bar during decryption
        decrypted_data = unpad(cipher.decrypt(encrypted_image_data), BLOCK_SIZE)
        bytes_to_image(decrypted_data, size, decrypted_image_path)
        print(f"Decrypted image saved to {decrypted_image_path}")
        return True
    except ValueError:
        print("Error: Incorrect decryption key or corrupt data.")
    except Exception as e:
        print(f"Unexpected error during decryption: {e}")
    return False


def dynamic_progress_bar(task, duration=5):
    """Display a dynamic progress bar."""
    start_time = time.time()
    for i in range(1, duration + 1):
        percent = (i / duration) * 100
        elapsed_time = time.time() - start_time
        remaining_time = elapsed_time * (duration - i) / i if i != 0 else 0
        bar = "█" * int(percent // 2) + "-" * (50 - int(percent // 2))
        sys.stdout.write(
            f"\r{task}: |{bar}| {percent:.2f}% Elapsed: {elapsed_time:.1f}s, Remaining: {remaining_time:.1f}s"
        )
        sys.stdout.flush()
        time.sleep(0.2)
    print("\n")


def server():
    """Server code to receive and decrypt an image."""
    host = "0.0.0.0"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("Waiting for connection...")

    client_socket, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    # Step 1: Receive image size
    size_data = client_socket.recv(1024).decode()
    size = tuple(map(int, size_data.split(",")))

    # Step 2: Receive checksum
    checksum = client_socket.recv(32).decode()

    # Step 3: Receive encrypted data
    encrypted_data = b""
    buffer_size = 8192
    print("Receiving encrypted image data...")
    for i in range(5):  # Simulating dynamic progress for receiving
        dynamic_progress_bar("Receiving Data", duration=5)
    while chunk := client_socket.recv(buffer_size):
        encrypted_data += chunk

    # Save received encrypted image
    encrypted_image_path = "received_encrypted_image.jpg"
    with open(encrypted_image_path, "wb") as f:
        f.write(encrypted_data)

    # Verify checksum
    computed_checksum = hashlib.md5(encrypted_data).hexdigest()
    if checksum != computed_checksum:
        print("Error: Checksum mismatch. Data integrity compromised.")
        client_socket.close()
        return

    # Step 4: Save visual representation
    visual_encrypted_path = "visual_received_encrypted_image.bmp"
    save_as_visual_encrypted_image(encrypted_data, size, visual_encrypted_path)

    # Step 5: Decrypt image
    key = input("Enter the decryption key: ").encode()
    decrypted_image_path = "decrypted_image.jpg"

    if decrypt_image(encrypted_data, key, size, decrypted_image_path):
        print("Decryption completed successfully.")
    else:
        print("Decryption failed. Please check the key or data.")

    client_socket.close()


if __name__ == "__main__":
    server()
