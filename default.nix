let
  lock = builtins.fromJSON (builtins.readFile ./flake.lock);

  flake-compat = fetchTarball {
    url =
      "https://github.com/edolstra/flake-compat/archive/${lock.nodes.flake-compat.locked.rev}.tar.gz";
    sha256 = lock.nodes.flake-compat.locked.narHash;
  };

  result = (import flake-compat { src = ./.; }).defaultNix // {
    vm = result.packages.${builtins.currentSystem}.vm;
  };

in result
