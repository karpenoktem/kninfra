self: super: {
  mailman2 = super.callPackage ./mailman2.nix {};
  kninfra = super.callPackage ./kndjango.nix { };
  # minimal python2 environment for Hans
  python2-hans = super.python2.withPackages (ps: [
    ps.sdnotify
    ps.grpcio
    (ps.buildPythonPackage rec {
      pname = "Django";
      version = "1.8.19";
      src = ps.fetchPypi {
        inherit pname version;
        hash = "sha256-M9RKXPnTMyR6mjdK4UeLeLg8m3jrMW/ASt3mIFO0wEc=";
      };
      doCheck = false;
      postFixup = ''
        wrapPythonProgramsIn $out/bin "$out $pythonPath"
      '';
    })
  ]);
  vipassana-vm = (import "${super.path}/nixos/lib/eval-config.nix" {
    modules = with (import ../infra.nix); [
      vipassana
      virt
      "${super.path}/nixos/modules/virtualisation/qemu-vm.nix"
      ({...}: {
        config.nixpkgs = {
          pkgs = self;
          inherit (self) system;
        };
      })
    ];
  }).config.system.build.vm.overrideAttrs (old:
    let
      # add switch-running-vm, ssh scripts
      # todo: host key checking for sanity
      ssh = self.writeShellScript "ssh" ''
        set -e
        key="$(mktemp)-vm-ssh.key"
        function finish {
          rm -f $key
        }
        cp ${toString ./..}/vm-ssh.key "$key"
        trap finish EXIT
        chmod 0600 $key
        ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$key" root@localhost -p 2222 "$@"
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
