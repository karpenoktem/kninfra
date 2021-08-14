# normally, nix would use whatever version of nixpkgs you have installed.
# here, we make sure to always use the latest 19.09 version
builtins.fetchTarball channel:nixos-21.05
