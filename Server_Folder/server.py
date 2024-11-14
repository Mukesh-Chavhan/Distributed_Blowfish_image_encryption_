import socket
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import unpad
from PIL import Image
import os
import time
import sys

BLOCK_SIZE = Blowfish.block_size


def bytes_to_image(byte_data, size, output_path):
    """Convert bytes to an image and save it in a specified format."""
    try:
        img = Image.frombytes("RGB", size, byte_data)
        img.save(output_path, format="JPEG")
    except Exception as e:
        print("Error converting bytes to image:", e)


def decrypt_image_stream(encrypted_data, key, size, decrypted_image_path):
    """Decrypt the image in a stream and save it directly to disk."""
    print(f"Starting decryption process...")

    iv = encrypted_data[:BLOCK_SIZE]
    encrypted_image_data = encrypted_data[BLOCK_SIZE:]

    cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv=iv)

    try:

        decrypted_data = unpad(cipher.decrypt(encrypted_image_data), BLOCK_SIZE)

        bytes_to_image(decrypted_data, size, decrypted_image_path)
        print(f"Decrypted image saved to {decrypted_image_path}")
    except ValueError as e:
        print("Error: Incorrect decryption key or corrupt data. Please try again.")
        return False
    except Exception as e:
        print("Unexpected error during decryption:", e)
        return False
    return True


def dynamic_progress_bar(task, duration=5, stop_at_error=False):
    """Display a progress bar with percentage and estimated time."""
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

        if stop_at_error and i == duration:
            sys.stdout.write(f"\r{task}: Decryption failed! Please check the key.\n")
            sys.stdout.flush()
            return False
    print("\n")
    return True


def loading_messages(task):
    """Simulate different stages of the process."""
    stages = [
        f"{task}: Initializing decryption...",
        f"{task}: Decrypting image...",
        f"{task}: Finalizing...",
        f"{task}: Done!",
    ]
    for stage in stages:
        sys.stdout.write(f"\r{stage}")
        sys.stdout.flush()
        time.sleep(0.5)
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

    size_data = client_socket.recv(1024).decode()
    size = tuple(map(int, size_data.split(",")))

    encrypted_data = b""
    print("Receiving encrypted image data...")
    if not dynamic_progress_bar("Receiving data", duration=10):
        return

    buffer_size = 8192
    while True:
        data = client_socket.recv(buffer_size)
        if not data:
            break
        encrypted_data += data

    key = input("Enter the decryption key: ").encode()

    decrypted_image_path = "decrypted_image.jpg"
    if not decrypt_image_stream(encrypted_data, key, size, decrypted_image_path):
        return

    client_socket.close()


if __name__ == "__main__":
    server()
