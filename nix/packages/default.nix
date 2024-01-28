final: prev: {
  mailman2 = final.callPackage ./mailman2.nix {};
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
        --set NODE_PATH ${puppeteer-cli.node_modules} \
        --set PUPPETEER_EXECUTABLE_PATH ${chromium}/bin/chromium
    '') {
    nodejs = final.nodejs-slim_latest;
  };
  # django 1.8.19 does not support python 3.10
  # https://stackoverflow.com/q/72032032
  python3-kn = final.python39;
  # minimal python2 environment for Hans
  python2-hans = final.poetry2nix.mkPoetryEnv {
    projectDir = ../poetry-hans;
    python = final.python2;
    # https://github.com/nix-community/poetry2nix/pull/899#issuecomment-1446049098
    # revert to `poetry2nix.overrides.withDefaults` after that's reverted
    overrides = [
      final.poetry2nix.defaultPoetryOverrides
      (self: super: {
        wheel = final.python2.pythonForBuild.pkgs.wheel.override {
          inherit (self) buildPythonPackage;
        };
        pytest = null;
        pytest-runner = null;
        hatchling = null;
        # conflict on backport site-pkg
        configparser = super.configparser.overrideAttrs (o: {
          meta.priority = 100;
        });
      })
    ];
  };
  python3-with-grpcio = final.python3-kn.withPackages (p: with p; [
    grpcio-tools
  ]);
  vipassana-vm = (final.nixos [
    (import ../infra.nix).vm
    final.inputs.agenix.nixosModules.default
  ]).vm;
}
