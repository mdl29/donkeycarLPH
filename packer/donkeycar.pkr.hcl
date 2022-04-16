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
      "apt install -y python3-venv", // Install updated ansible version from pip, apt's version is outdated
      "mkdir -p /tmp/ansible",
      "python3 -m venv /tmp/ansible/venv",
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
