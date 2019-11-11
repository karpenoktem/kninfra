{stdenv, pkgs, python37, makeWrapper}:
let
  requirements = import ./kndjango/requirements.nix { inherit pkgs; };
in
stdenv.mkDerivation {
  name = "kninfra";
  src = stdenv.lib.cleanSourceWith {
    src = ../..;
    filter = path: type: !(stdenv.lib.hasSuffix "qcow2" path);
  };
  buildInputs = [ makeWrapper requirements.interpreter ];
  PYTHONPATH = python37.pkgs.makePythonPath (builtins.attrValues requirements.packages);
  installPhase = ''
    mkdir $out $out/libexec
    cp --reflink=auto -R kn locale manage.py media protobufs utils bin $out
    cp --reflink=auto -R salt/states/sankhara/initial{-db.yaml,izeDb.py} $out/libexec
    chmod +x $out/libexec/initializeDb.py
  '';
}
