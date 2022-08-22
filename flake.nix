{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-22.05";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
    inputs.flake-utils.follows = "flake-utils";
  };
  inputs.flake-compat = {
    url = "github:edolstra/flake-compat";
    flake = false;
  };
  inputs.agenix = {
    url = "github:ryantm/agenix";
    inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs = { self, nixpkgs, flake-utils, poetry2nix, agenix, ... }@inputs:
    let
      out =
        # add your fancy ARM macbook to this list
        flake-utils.lib.eachSystem [ "x86_64-linux" ] (system: rec {
          overlay = import ./nix/packages;
          legacyPackages = import nixpkgs {
            overlays = [
              poetry2nix.overlay
              overlay
              agenix.overlay
              (self: super: { inherit inputs; })
            ];
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
          devShells.protobufs = legacyPackages.mkShell {
            buildInputs = [ (legacyPackages.python3.withPackages (p: with p; [
              grpcio-tools
            ])) ];
          };
        });
    in out // {
      nixosConfigurations.staging =
        out.legacyPackages.x86_64-linux.nixos [
          inputs.agenix.nixosModule
          (import ./nix/infra.nix).staging
        ];
    };
}
