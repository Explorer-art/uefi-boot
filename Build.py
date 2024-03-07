import argparse
import os
import shutil
import sys
import subprocess as sp
from pathlib import Path

ARCH = "x86_64"
TARGET = ARCH + "-none-efi"
CONFIG = "debug"
QEMU = "qemu-system-" + ARCH

WORKSPACE_DIR = Path(__file__).resolve().parents[0]
BUILD_DIR = WORKSPACE_DIR / "build"

OVMF_FW = WORKSPACE_DIR / "ovmf" / "OVMF_CODE.fd"
OVMF_VARS = WORKSPACE_DIR / "ovmf" / "OVMF_VARS-1024x768.fd"

def build():
    boot_dir = BUILD_DIR / "EFI" / "BOOT"
    boot_dir.mkdir(parents=True, exist_ok=True)
    
    built_file = "boot.efi"
    output_file = boot_dir / "BootX64.efi"
    shutil.copy2(built_file, output_file)

    startup_file = open(BUILD_DIR / "startup.nsh", "w")
    startup_file.write("\EFI\BOOT\BOOTX64.EFI")
    startup_file.close()

def run():
    qemu_flags = [
        # Disable default devices
        # QEMU by default enables a ton of devices which slow down boot.
        "-nodefaults",
    
        # Use a standard VGA for graphics
        "-vga", "std",
    
        # Use a modern machine, with acceleration if possible.
        "-machine", "q35,accel=kvm:tcg",
    
        # Allocate some memory
        "-m", "128M",
    
        # Set up OVMF
        "-drive", f"if=pflash,format=raw,readonly,file={OVMF_FW}",
        "-drive", f"if=pflash,format=raw,file={OVMF_VARS}",
    
        # Mount a local directory as a FAT partition
        "-drive", f"format=raw,file=fat:rw:{BUILD_DIR}",
    
        # Enable serial
        #
        # Connect the serial port to the host. OVMF is kind enough to connect
        # the UEFI stdout and stdin to that port too.
        "-serial", "stdio",
    
        # Setup monitor
        "-monitor", "vc:1024x768",
      ]

    sp.run([QEMU] + qemu_flags).check_returncode()

def main():
    if len(sys.argv) < 2:
        print("Error! Unknown command.")
        print("Example: python3.11 Build.py [build/run]")

        return False
        
    if sys.argv[1] == "build":
        build()
    elif sys.argv[1] == "run":
        run()
    else:
        print("Error! Unknown command.")
        print("Example: python3.11 Build.py [build/run]")

if __name__ == "__main__":
    main()
