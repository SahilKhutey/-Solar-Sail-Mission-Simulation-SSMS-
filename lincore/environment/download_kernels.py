import os
import urllib.request
import sys

def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    try:
        urllib.request.urlretrieve(url, target_path)
        print("Success.")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

def download_kernels():
    kernel_dir = "kernels"
    if not os.path.exists(kernel_dir):
        os.makedirs(kernel_dir)
        
    kernels = [
        ("https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp", "de440.bsp"),
        ("https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls", "naif0012.tls")
    ]
    
    for url, filename in kernels:
        target_path = os.path.join(kernel_dir, filename)
        if os.path.exists(target_path):
            print(f"{filename} already exists.")
        else:
            download_file(url, target_path)

if __name__ == "__main__":
    download_kernels()
