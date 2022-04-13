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
  last_partition_extra_size = 524288000 // Adding 500 Mb to last rpi partition, main rootfs, so that we have space to install stuff
}

build {
  sources = ["source.arm-image.raspbian"]

  // Install Ansible, will be removed after
  provisioner "shell" {
    inline = [
      "apt-get update",
      "apt-get install -y ansible"
    ]
  }

  // Launch ansible book
  provisioner "ansible-local" {
    // Use temporary installed ansible
    playbook_dir = "../ansible"
    playbook_file = "../ansible/donkeycar.yml"
  }

  // Remove Ansible
  // provisioner "shell" {
  //   inline = [
  //     "apt autoremove ansible"
  //   ]
  // }

}
