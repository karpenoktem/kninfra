let pkgs = import ./nix; in
(import ./default.nix).overrideAttrs (o: {
  buildInputs = o.buildInputs ++ [pkgs.poetry];
})
