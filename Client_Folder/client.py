import socket
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad
from PIL import Image
import hashlib
import numpy as np
from tqdm import tqdm
import time
import sys

BLOCK_SIZE = Blowfish.block_size


def image_to_bytes(image_path):
    """Convert an image to bytes."""
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        return img.tobytes(), img.size


def encrypt_image(image_path, key):
    """Encrypt the image using Blowfish with progress."""
    image_data, size = image_to_bytes(image_path)
    cipher = Blowfish.new(key, Blowfish.MODE_CBC)

    print("Encrypting the image data...")
    padded_data = pad(image_data, BLOCK_SIZE)
    time.sleep(1)
    encrypted_data = cipher.iv + cipher.encrypt(padded_data)
    print("Encryption completed.")
    return encrypted_data, size


def save_as_visual_encrypted_image(encrypted_data, size, output_path):
    """Save the encrypted data as an image to visualize it."""

    encrypted_pixels = encrypted_data[BLOCK_SIZE:]

    expected_bytes = size[0] * size[1] * 3
    encrypted_pixels = encrypted_pixels[:expected_bytes]

    encrypted_array = np.frombuffer(encrypted_pixels, dtype=np.uint8)
    encrypted_image = encrypted_array.reshape((size[1], size[0], 3))

    encrypted_img = Image.fromarray(encrypted_image, "RGB")
    encrypted_img.save(output_path)


def dynamic_progress_bar(task, duration):
    """Display a dynamic progress bar with percentage and estimated time."""
    start_time = time.time()
    for i in range(duration):
        percent = ((i + 1) / duration) * 100
        elapsed_time = time.time() - start_time
        remaining_time = elapsed_time * (duration - i - 1) / (i + 1)
        bar = "█" * int(percent // 2) + "-" * (50 - int(percent // 2))
        sys.stdout.write(
            f"\r{task}: |{bar}| {percent:.2f}% Elapsed: {elapsed_time:.1f}s, Remaining: {remaining_time:.1f}s"
        )
        sys.stdout.flush()
        time.sleep(0.5)
    print("\n")


def loading_messages(task):
    """Simulate realistic loading messages."""
    stages = [
        f"{task}: Initializing...",
        f"{task}: Encrypting image data...",
        f"{task}: Preparing data for transfer...",
        f"{task}: Sending encrypted image...",
        f"{task}: Task completed!",
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

    print("Preparing image for encryption...")
    image_path = "input_images/spiderman.jpg"
    key = input("Enter the encryption key: ").encode()

    loading_messages("Encrypting the image")
    dynamic_progress_bar("Encryption Progress", duration=10)

    encrypted_data, size = encrypt_image(image_path, key)

    encrypted_image_path = "output_images/encrypted_image.jpg"
    with open(encrypted_image_path, "wb") as f:
        f.write(encrypted_data)

    visual_encrypted_path = "output_images/visual_encrypted_image.bmp"
    save_as_visual_encrypted_image(encrypted_data, size, visual_encrypted_path)

    checksum = hashlib.md5(encrypted_data).hexdigest()

    client_socket.send(f"{size[0]},{size[1]}".encode())

    client_socket.send(checksum.encode())

    print("Sending encrypted image to the server...")
    total_size = len(encrypted_data)
    with tqdm(
        total=total_size, unit="B", unit_scale=True, desc="Data Transfer"
    ) as pbar:
        with open(encrypted_image_path, "rb") as f:
            while chunk := f.read(8192):
                client_socket.send(chunk)
                pbar.update(len(chunk))

    print("\nEncrypted image sent to the server successfully.")

    client_socket.close()


if __name__ == "__main__":
    client()
