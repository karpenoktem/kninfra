{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-21.05";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.flake-compat = {
    url = "github:edolstra/flake-compat";
    flake = false;
  };
  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    let
      out =
        # add your fancy ARM macbook to this list
        flake-utils.lib.eachSystem [ "x86_64-linux" ] (system: rec {
          overlay = import ./nix/packages;
          legacyPackages = import nixpkgs {
            overlays = [ overlay ];
            inherit system;
          };
          # buildable with `nix build .#kninfra`, etc
          packages = with legacyPackages; {
            kninfra = kninfra;
            vm = vipassana-vm;
          };
          # what you get when running `nix build`
          defaultPackage = packages.kninfra;
          # what you get when running `nix develop`
          devShell = packages.kninfra.overrideAttrs (o: {
            # extra packages inside the shell
            buildInputs = o.buildInputs
              ++ (with legacyPackages; [ poetry gettext mongodb nixos-rebuild ]);
          });
        });
    in out // {
      nixosConfigurations.staging =
        out.legacyPackages.x86_64-linux.nixos (import ./nix/infra.nix).staging;
    };
}
