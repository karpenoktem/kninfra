with import <nixpkgs> {
  overlays = [ (import ./nix/packages) ];
}; (kninfra // { vm = vipassana-vm; })
