{system, nixosTest, inputs, curl, kn, cyrus_sasl}:
let
  infra = import ./infra.nix;
in
nixosTest ({
  nodes.machine = {config, pkgs, lib, ...}: {
    imports = [
      infra.virtualized
      inputs.agenix.nixosModules.default
    ];
  };
  name = "kn-vm-check";
  testScript = ''
    machine.wait_for_unit("kndjango.socket")
    machine.wait_for_unit("nginx.service")
    machine.wait_for_unit("saslauthd.service")
    machine.succeed("${cyrus_sasl}/bin/testsaslauthd -u admin -p 'CHANGE ME'")
    machine.succeed("${curl}/bin/curl -f -LI http://localhost/")
    machine.wait_for_unit("phpfpm-mediawiki.service")
    machine.succeed("${kn.puppetCheck}/bin/kn-puppet http://localhost admin 'CHANGE ME'")
    machine.succeed("${kn.puppetCheck}/bin/kn-puppet http://localhost test 'CHANGE ME'")
    machine.succeed("kn-giedo-sync")
  '';
})
