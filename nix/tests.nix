{system, nixosTest, inputs, curl, kn}:
let
  infra = import ./infra.nix;
in
nixosTest ({
  nodes.machine = {config, pkgs, lib, ...}: {
    imports = [
      infra.virtualized
      inputs.agenix.nixosModule
    ];
  };
  testScript = ''
    machine.wait_for_unit("kndjango.socket")
    machine.wait_for_unit("nginx.service")
    machine.succeed("${curl}/bin/curl -f -LI http://localhost/")
    machine.succeed("${kn.puppetCheck}/bin/kn-puppet http://localhost admin 'CHANGE ME'")
    machine.succeed("${kn.puppetCheck}/bin/kn-puppet http://localhost test 'CHANGE ME'")
  '';
})
