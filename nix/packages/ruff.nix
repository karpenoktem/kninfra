{ stdenv, lib, fetchurl }:
stdenv.mkDerivation (o: {
  pname = "ruff";
  version = "0.0.252";
  sourceRoot = ".";
  src = {
    # curl -L 'https://github.com/charliermarsh/ruff/releases/download/v0.0.252/ruff-x86_64-unknown-linux-musl.tar.gz.sha256' | cut -f1 -d' '
    # nix hash to-sri $(!!) --type sha256
    "x86_64-linux" = fetchurl {
      url = "https://github.com/charliermarsh/ruff/releases/download/v${o.version}/ruff-x86_64-unknown-linux-musl.tar.gz";
      hash = "sha256-wJb6nW/zhRD3xj6qSwAqW8xaRPKiuk+s+sjQ0NRPB0Q=";
    };
    "aarch64-linux" = fetchurl {
      url = "https://github.com/charliermarsh/ruff/releases/download/v${o.version}/ruff-aarch64-unknown-linux-musl.tar.gz";
      hash = "sha256-4jIp3mQRwT2JYs+sJWx+tt+5bupxl6PnAGdiLamdMqI=";
    };
  }.${stdenv.system} or (throw "Unsupported system: ${stdenv.system}");
  installPhase = ''
    mkdir -p $out/bin
    cp ruff $out/bin
  '';
})
