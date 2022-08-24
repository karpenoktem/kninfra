final: prev: {
  mailman2 = final.callPackage ./mailman2.nix {};
  kninfra = final.callPackage ./kndjango.nix { };
  kn.checks = final.callPackage ../tests.nix {};
  kn.puppetCheck = final.callPackage ({stdenv, runCommandNoCC, makeWrapper, puppeteer-cli, chromium, nodejs}:
    runCommandNoCC "kn-puppet" {
      buildInputs = [ makeWrapper ];
    } ''
      mkdir -p $out/bin
      makeWrapper ${nodejs}/bin/node $out/bin/kn-puppet \
        --add-flags ${../puppet.js} \
        --set NODE_PATH ${puppeteer-cli.node_modules} \
        --set PUPPETEER_EXECUTABLE_PATH ${chromium}/bin/chromium
    '') {
    nodejs = final.nodejs-slim_latest;
  };
  # minimal python2 environment for Hans
  python2-hans = final.poetry2nix.mkPoetryEnv {
    projectDir = ../poetry-hans;
    python = final.python2;
    overrides = final.poetry2nix.overrides.withDefaults (self: super: {
      # conflict on backport site-pkg
      configparser = super.configparser.overrideAttrs (o: {
        meta.priority = 100;
      });
    });
  };
  python3-with-grpcio = final.python3.withPackages (p: with p; [
    grpcio-tools
  ]);
  vipassana-vm = (final.nixos [
    (import ../infra.nix).vm
    final.inputs.agenix.nixosModule
  ]).vm;
}
