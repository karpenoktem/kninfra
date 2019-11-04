with import (import ./nix/nixpkgs.nix) {
  overlays = [ (import ./nix/packages) ];
}; (kninfra // { vm = vipassana-vm; })
