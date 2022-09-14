packer {
  required_plugins {
    arm-image = {
      source  = "github.com/solo-io/arm-image"
      version = ">= 0.2.5"
    }
  }
}

source "arm-image" "raspbian" {
  iso_url      = "https://downloads.raspberrypi.org/raspios_oldstable_lite_armhf/images/raspios_oldstable_lite_armhf-2021-12-02/2021-12-02-raspios-buster-armhf-lite.zip"
  iso_checksum = "9276d71a4793accb4e29ad337f58865fcb92f831716305fc93adf0adb4784129"
  target_image_size = 8178892800 // Adding 6Gb TESTING (524288000×12+1887436800), original size 1887436800 to last rpi partition, main rootfs, so that we have space to install stuff
}

build {
  sources = ["source.arm-image.raspbian"]

  provisioner "shell" {
    // Use temporary installed ansible
    inline = [
      // --- Installing Rust ---
      "echo \"=== Installing Rust as required for python cryptography (dependency of Ansible) ===\"",
      "echo \"See: https://cryptography.io/en/latest/installation/#rust\"",
      "apt install -y build-essential curl",
      // Workaround for armv7 : https://github.com/rust-lang/cargo/issues/8719#issuecomment-932084513
      // Using tempfs for cargo to bypass qemu arm bug : https://github.com/docker/buildx/issues/395#issuecomment-1069229784 
      "mkdir -p /root/.cargo && chmod 777 /root/.cargo && mount -t tmpfs none /root/.cargo",
      "curl https://sh.rustup.rs -sSf | bash -s -- -y",
      "export PATH=\"$PATH:/root/.cargo/bin\"",

      // --- Installing Python-venv and upgrade pip ---
      "echo \"=== Installing Python-venv and upgrade pip ===\"",
      "apt install -y python3-venv python3-dev", // Install updated ansible version from pip, apt's version is outdated
      "mkdir -p /tmp/ansible",
      "python3 -m venv /tmp/ansible/venv",
      "/tmp/ansible/venv/bin/pip install --upgrade pip",

      // --- Installing Ansible ---
      "echo \"=== Installing Ansible ===\"",
      "/tmp/ansible/venv/bin/pip install ansible"
    ]
  }

  // Launch ansible book
  provisioner "ansible-local" {
    // Use temporary installed ansible
    playbook_dir = "../ansible"
    playbook_file = "../ansible/donkeycar.yml"
    command = "/tmp/ansible/venv/bin/ansible-playbook"
    extra_arguments = [
      "--extra-vars", "ansible_python_interpreter=/tmp/ansible/venv/bin/python"
    ]
  }

  // Remove Ansible
  // provisioner "shell" {
  //   inline = [
  //     "apt autoremove ansible"
  //   ]
  // }

  provisioner "shell" {
    // See still available place
    inline = [
      "df -h"
    ]
  }


}
