import socket
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad
from PIL import Image
import os
import time
import sys

BLOCK_SIZE = Blowfish.block_size


def image_to_bytes(image_path):
    """Convert an image to bytes."""
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        return img.tobytes(), img.size


def bytes_to_image(byte_data, size, output_path):
    """Convert bytes back to image and save it."""
    img = Image.frombytes("RGB", size, byte_data)
    img.save(output_path)


def encrypt_image(image_path, key):
    """Encrypt the image using Blowfish."""
    image_data, size = image_to_bytes(image_path)

    cipher = Blowfish.new(key, Blowfish.MODE_CBC)

    padded_data = pad(image_data, BLOCK_SIZE)

    encrypted_data = cipher.iv + cipher.encrypt(padded_data)
    return encrypted_data, size


def dynamic_progress_bar(task, duration=10):
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
        time.sleep(0.5)
    print("\n")


def loading_messages(task):
    """Simulate different stages of the process."""
    stages = [
        f"{task}: Initializing encryption...",
        f"{task}: Encrypting image...",
        f"{task}: Sending encrypted data...",
        f"{task}: Finalizing...",
        f"{task}: Done!",
    ]
    for stage in stages:
        sys.stdout.write(f"\r{stage}")
        sys.stdout.flush()
        time.sleep(1)
    print("\n")


def client():
    """Client side code for sending the encrypted image."""
    host = input("Enter the IP address of the second laptop: ")
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    image_path = "input_images/spiderman.jpg"

    key = input("Enter the encryption key: ").encode()

    loading_messages("Encrypting the image")

    dynamic_progress_bar("Encrypting", duration=10)

    encrypted_data, size = encrypt_image(image_path, key)

    encrypted_image_path = "output_images/encrypted_image.jpg"
    encrypted_data_rgb = bytes((byte % 256 for byte in encrypted_data))
    bytes_to_image(encrypted_data_rgb, size, encrypted_image_path)
    print(f"Encrypted image saved to {encrypted_image_path}")

    print(f"\nSending image size {size[0]} x {size[1]}")
    client_socket.send(f"{size[0]},{size[1]}".encode())

    print("Sending encrypted data to the server...")
    dynamic_progress_bar("Sending data", duration=15)

    client_socket.sendall(encrypted_data)

    print("\nEncrypted image sent to the server.")

    client_socket.close()


if __name__ == "__main__":
    client()
