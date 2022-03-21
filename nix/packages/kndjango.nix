{stdenv, lib, pkgs, poetry2nix, python2-hans, python3, makeWrapper}:
let
  requirements = poetry2nix.mkPoetryEnv {
    projectDir = ../../.;
    overrides = poetry2nix.overrides.withDefaults (self: super: {
      gitpython = super.gitpython.overridePythonAttrs (old: {
        inherit (python3.pkgs.GitPython) patches doCheck pythonImportsCheck;
        propagatedBuildInputs = old.propagatedBuildInputs ++ lib.optionals (self.pythonOlder "3.10") [ self.typing-extensions ];
      });
      graphene-django = super.graphene-django.overridePythonAttrs (o: {
        propagatedBuildInputs = o.propagatedBuildInputs ++ [ self.pytestrunner ];
        doCheck = false;
        # pretty sure this exists?!
        preConfigure = ''
          ${o.preConfigure or ""}
          sed -i '/singledispatch/d' setup.py
        '';
      });
      sarah = super.sarah.overridePythonAttrs (old: {
        # remove mirte cycle
        propagatedBuildInputs =
          builtins.filter (i: i.pname != "mirte") old.propagatedBuildInputs;
        preConfigure = ''
          ${old.preConfigure or ""}
          sed -i '/mirte/d' setup.py
        '';
      });
    });
  };
in
stdenv.mkDerivation {
  name = "kninfra";
  src = lib.cleanSourceWith {
    src = ../..;
    filter = path: type: !(lib.hasSuffix "qcow2" path);
  };
  buildInputs = [ makeWrapper requirements ];
  PYTHONPATH = "${requirements}/${requirements.sitePackages}";
  buildPhase = ''
    python -m py_compile $(find . -iname '*.py')
  '';
  installPhase = ''
    mkdir $out $out/libexec
    cp --reflink=auto -R kn locale manage.py media protobufs utils bin $out
    cp --reflink=auto -R salt/states/sankhara/initial{-db.yaml,izeDb.py} $out/libexec
    makeWrapper $(type -p ipython) $out/bin/shell --add-flags "-i $out/utils/shell.py"
    makeWrapper ${python2-hans}/bin/python $out/bin/hans --add-flags "$out/utils/hans.py"
    chmod +x $out/libexec/initializeDb.py
  '';
}
