self: super: {
  kninfra = super.callPackage ./kndjango.nix { };
  vipassana-vm = (import <nixpkgs/nixos/lib/eval-config.nix> {
    modules = with (import ../infra.nix); [
      vipassana
      virt
      <nixpkgs/nixos/modules/virtualisation/qemu-vm.nix>
    ];
  }).config.system.build.vm.overrideAttrs (old:
    let
      # add switch-running-vm, ssh scripts
      ssh = self.writeShellScript "ssh" ''
        set -e
        ssh -i ${toString ./..}/vm-ssh.key root@localhost -p 2222 "$@"
      '';
      switch-running-vm = self.writeShellScript "switch-running-vm" ''
        set -e
        $(dirname "$0")/ssh $(realpath $(dirname "$0"))/../system/bin/switch-to-configuration test
      '';
    in {
      buildCommand = old.buildCommand + ''
        ln -s ${switch-running-vm} $out/bin/switch-running-vm
        ln -s ${ssh} $out/bin/ssh
      '';
    });
}
