# merged-in config for hetzner VM
{ modulesPath, ... }: {
  # installation:
  # make hetzner cloud, mount nixos 21.11 iso
  # rescue console, curl https://pub.yori.cc/install-hetzner.sh | bash
  # unmount, restart server, login with yorick's ssh key
  imports = [ (modulesPath + "/profiles/qemu-guest.nix") ];
  networking = {
    usePredictableInterfaceNames = false;
    useDHCP = false;
    interfaces.eth0 = { useDHCP = true; };
    defaultGateway6 = {
      address = "fe80::1";
      interface = "eth0";
    };
  };
  boot.loader.grub = {
    enable = true;
    devices = [ "/dev/sda" ];
  };
  boot.initrd.availableKernelModules =
    [ "ahci" "xhci_pci" "virtio_pci" "sd_mod" "sr_mod" ];
  boot.initrd.kernelModules = [ ];
  boot.kernelModules = [ ];
  boot.extraModulePackages = [ ];

  fileSystems."/" = {
    device = "/dev/sda1";
    fsType = "ext4";
  };

  swapDevices = [ ];

  hardware.cpu.amd.updateMicrocode = true;
}
