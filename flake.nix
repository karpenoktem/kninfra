{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      # TODO: revert to nix-community after
      # https://github.com/nix-community/poetry2nix/pull/984
      url = "github:yorickvP/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    agenix = {
      url = "github:ryantm/agenix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    devshell = {
      url = "github:numtide/devshell";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };
  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    let
      out =
        # add your fancy ARM macbook to this list
        flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (system:
          let pkgs = self.legacyPackages.${system};
          in {
            legacyPackages = import nixpkgs {
              overlays = with inputs; [
                poetry2nix.overlay
                self.overlays.default
                agenix.overlays.default
                devshell.overlay
                # add 'inputs' pseudo-package
                (self: super: { inherit inputs; })
              ];
              inherit system;
            };
            packages = with pkgs; {
              # what you get when running `nix build`
              default = kninfra;
              # nix build .#kninfra
              kninfra = kninfra;
              # nix build .#vm
              vm = vipassana-vm;
            };
            devShells = {
              ## what you get when running `nix develop`
              # see ./nix/devshell.toml
              default = pkgs.devshell.mkShell {
                imports = [ (pkgs.devshell.importTOML ./nix/devshell.toml) ];
              };
              ## nix develop .#python
              # shell augmented with python deps, useful for python development
              python = pkgs.devshell.mkShell {
                imports = [ (pkgs.devshell.importTOML ./nix/devshell.toml) ];
                devshell.name = "python-dev";
                env = [{
                  name = "PYTHONPATH";
                  value = pkgs.kninfra.PYTHONPATH;
                }];
              };
            };
          });
    in out // {
      overlays.default = import ./nix/packages;
      nixosConfigurations.staging = self.legacyPackages.x86_64-linux.nixos [
        inputs.agenix.nixosModules.default
        (import ./nix/infra.nix).staging
      ];
    };
}
