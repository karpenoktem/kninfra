final: prev: {
  kninfra = final.callPackage ./kndjango.nix {
    python3 = final.python3-kn;
  };
  kn.vmCheck = final.callPackage ../tests.nix {};
  kn.puppetCheck = final.callPackage ({stdenv, runCommandNoCC, makeWrapper, puppeteer-cli, chromium, nodejs}:
    runCommandNoCC "kn-puppet" {
      buildInputs = [ makeWrapper ];
    } ''
      mkdir -p $out/bin
      makeWrapper ${nodejs}/bin/node $out/bin/kn-puppet \
        --add-flags ${../puppet.js} \
        --set NODE_PATH ${puppeteer-cli}/lib/node_modules/puppeteer-cli/node_modules \
        --set PUPPETEER_EXECUTABLE_PATH ${chromium}/bin/chromium
    '') {
    nodejs = final.nodejs-slim_latest;
  };
  # django 1.8.19 does not support python 3.10
  # https://stackoverflow.com/q/72032032
  python3-kn = final.python39;
  python3-with-grpcio = final.python3-kn.withPackages (p: with p; [
    grpcio-tools
  ]);
  vipassana-vm = (final.nixos [
    (import ../infra.nix).vm
    final.inputs.agenix.nixosModules.default
  ]).vm;
}
