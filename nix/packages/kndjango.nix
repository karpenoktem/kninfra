{stdenv, lib, pkgs, poetry2nix, python2-hans, python3, makeWrapper}:
let
  requirements = poetry2nix.mkPoetryEnv {
    python = python3;
    projectDir = ../../.;
    overrides = poetry2nix.overrides.withDefaults (self: super: {
      zipseeker = super.zipseeker.overridePythonAttrs (old: {
        propagatedBuildInputs = old.propagatedBuildInputs ++ [ self.setuptools ];
      });
      tarjan = super.tarjan.overridePythonAttrs (old: {
        propagatedBuildInputs = old.propagatedBuildInputs ++ [ self.setuptools ];
      });
      singledispatch = super.singledispatch.overridePythonAttrs (old: {
        propagatedBuildInputs = old.propagatedBuildInputs ++ [ self.setuptools ];
      });
      msgpack-python = super.msgpack-python.overridePythonAttrs (old: {
        propagatedBuildInputs = old.propagatedBuildInputs ++ [ self.setuptools ];
      });
      graphene-django = super.graphene-django.overridePythonAttrs (old: {
        propagatedBuildInputs = old.propagatedBuildInputs ++ [ self.singledispatch ];
        postPatch = ''
          sed -i '/singledispatch/d' setup.py
        '';
      });
      reserved = super.reserved.overridePythonAttrs (old: {
        propagatedBuildInputs = old.propagatedBuildInputs ++ [ self.setuptools ];
      });
      gitpython = super.gitpython.overridePythonAttrs (old: {
        inherit (python3.pkgs.GitPython) patches doCheck pythonImportsCheck;
        propagatedBuildInputs = old.propagatedBuildInputs ++ lib.optionals (self.pythonOlder "3.10") [ self.typing-extensions ];
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
