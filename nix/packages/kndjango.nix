{stdenv, lib, pkgs, poetry2nix, python2-hans, python3, makeWrapper}:
let
  addBuildInput = pkg: bip: pkg.overridePythonAttrs (old: {
    propagatedBuildInputs = old.propagatedBuildInputs ++ [ bip ];
  });
  requirements = poetry2nix.mkPoetryEnv {
    python = python3;
    projectDir = ../../.;
    overrides = poetry2nix.overrides.withDefaults (self: super: {
      tarjan = addBuildInput super.tarjan self.setuptools;
      editables = addBuildInput super.editables self.flit-core;
      py3dns = addBuildInput super.py3dns self.flit-core;
      atpublic = addBuildInput super.atpublic self.pdm-backend;
      flufl-i18n = addBuildInput super.flufl-i18n self.pdm-pep517;
      flufl-lock = addBuildInput super.flufl-lock self.pdm-pep517;
      publicsuffix2 = addBuildInput super.publicsuffix2 self.requests;
      mailman = super.mailman.overridePythonAttrs (old: {
        patches = (old.patches or []) ++ pkgs.mailman.patches;
      });
      gitpython = super.gitpython.overridePythonAttrs (old: {
        inherit (python3.pkgs.GitPython) patches doCheck pythonImportsCheck;
        propagatedBuildInputs = old.propagatedBuildInputs ++ lib.optionals (self.pythonOlder "3.10") [ self.typing-extensions ];
        nativeBuildInputs = (old.nativeBuildInputs or []) ++ [ pkgs.git ];
      });
    });
  };
  # inverse of sourceByRegex, https://github.com/NixOS/nixpkgs/blob/master/lib/sources.nix#L138
  sourceByNotRegex = src: regexes: let
    isFiltered = src ? _isLibCleanSourceWith;
    origSrc = if isFiltered then src.origSrc else src;
  in lib.cleanSourceWith {
    filter = (path: type:
      let relPath = lib.removePrefix (toString origSrc + "/") (toString path);
      in !(lib.any (re: builtins.match re relPath != null) regexes));
    inherit src;
  };
in
stdenv.mkDerivation {
  name = "kninfra";
  src = sourceByNotRegex (lib.cleanSource ../..) [
    "\.qcow2$" # vm drive, never include this
    "^kn/static/media$" # share this between drvs, to optimize CI size
    # avoid rebuilds:
    "\.nix$"
    "\.md$"
    "^nix$"
  ];
  static_media = ../../kn/static/media;
  buildInputs = [ makeWrapper requirements ];
  PYTHONPATH = "${requirements}/${requirements.sitePackages}";
  buildPhase = ''
    python -m py_compile $(find . -iname '*.py')
  '';
  installPhase = ''
    ln -s $static_media kn/static/media
    mkdir $out $out/libexec
    cp --reflink=auto -R kn locale manage.py media protobufs utils bin $out
    cp --reflink=auto -R salt/states/sankhara/initial{-db.yaml,izeDb.py} $out/libexec
    makeWrapper $(type -p ipython) $out/bin/shell --add-flags "-i $out/utils/shell.py"
    makeWrapper ${python2-hans}/bin/python $out/bin/hans --add-flags "$out/utils/hans.py"
    chmod +x $out/libexec/initializeDb.py
  '';
}
