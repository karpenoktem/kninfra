# generated using pypi2nix tool (version: 2.0.0)
# See more at: https://github.com/garbas/pypi2nix
#
# COMMAND:
#   pypi2nix -V 3.7 -e graphene -e graphene-django==2.1.0 -e sdnotify -e reserved -e zipseeker -e django==1.8.19 -e docutils
#

{ pkgs ? import <nixpkgs> {},
  overrides ? ({ pkgs, python }: self: super: {})
}:

let

  inherit (pkgs) makeWrapper;
  inherit (pkgs.stdenv.lib) fix' extends inNixShell;

  pythonPackages =
  import "${toString pkgs.path}/pkgs/top-level/python-packages.nix" {
    inherit pkgs;
    inherit (pkgs) stdenv;
    python = pkgs.python37;
    # patching pip so it does not try to remove files when running nix-shell
    overrides =
      self: super: {
        # bootstrapped-pip = super.bootstrapped-pip.overrideDerivation (old: {
        #   patchPhase = ''
        #     if [ -e $out/${pkgs.python37.sitePackages}/pip/req/req_install.py ]; then
        #       sed -i \
        #         -e "s|paths_to_remove.remove(auto_confirm)|#paths_to_remove.remove(auto_confirm)|"  \
        #         -e "s|self.uninstalled = paths_to_remove|#self.uninstalled = paths_to_remove|"  \
        #         $out/${pkgs.python37.sitePackages}/pip/req/req_install.py
        #     fi
        #   '';
        # });
      };
  };

  commonBuildInputs = [];
  commonDoCheck = false;

  withPackages = pkgs':
    let
      pkgs = builtins.removeAttrs pkgs' ["__unfix__"];
      interpreterWithPackages = selectPkgsFn: pythonPackages.buildPythonPackage {
        name = "python37-interpreter";
        buildInputs = [ makeWrapper ] ++ (selectPkgsFn pkgs);
        buildCommand = ''
          mkdir -p $out/bin
          ln -s ${pythonPackages.python.interpreter} \
              $out/bin/${pythonPackages.python.executable}
          for dep in ${builtins.concatStringsSep " "
              (selectPkgsFn pkgs)}; do
            if [ -d "$dep/bin" ]; then
              for prog in "$dep/bin/"*; do
                if [ -x "$prog" ] && [ -f "$prog" ]; then
                  ln -s $prog $out/bin/`basename $prog`
                fi
              done
            fi
          done
          for prog in "$out/bin/"*; do
            wrapProgram "$prog" --prefix PYTHONPATH : "$PYTHONPATH"
          done
          pushd $out/bin
          ln -s ${pythonPackages.python.executable} python
          ln -s ${pythonPackages.python.executable} \
              python3
          popd
        '';
        passthru.interpreter = pythonPackages.python;
      };

      interpreter = interpreterWithPackages builtins.attrValues;
    in {
      __old = pythonPackages;
      inherit interpreter;
      inherit interpreterWithPackages;
      mkDerivation = args: pythonPackages.buildPythonPackage (args // {
        nativeBuildInputs = (args.nativeBuildInputs or []) ++ args.buildInputs;
      });
      packages = pkgs;
      overrideDerivation = drv: f:
        pythonPackages.buildPythonPackage (
          drv.drvAttrs // f drv.drvAttrs // { meta = drv.meta; }
        );
      withPackages = pkgs'':
        withPackages (pkgs // pkgs'');
    };

  python = withPackages {};

  generated = self: {
    "aniso8601" = python.mkDerivation {
      name = "aniso8601-6.0.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/f8/1d/1cb919d85c0c33e1aa56d9a6f31ff2f799e41f98951c4551336254294ec1/aniso8601-6.0.0.tar.gz";
        sha256 = "b8a6a9b24611fc50cf2d9b45d371bfdc4fd0581d1cc52254f5502130a776d4af";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://bitbucket.org/nielsenb/aniso8601";
        license = "UNKNOWN";
        description = "A library for parsing ISO 8601 strings.";
      };
    };

    "django" = python.mkDerivation {
      name = "django-1.8.19";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ad/da/980dbd68970fefbdf9c62faeed5da1d8ed49214ff3ea3991c2d233719b51/Django-1.8.19.tar.gz";
        sha256 = "33d44a5cf9d333247a9a374ae1478b78b83c9b78eb316fc04adde62053b4c047";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://www.djangoproject.com/";
        license = licenses.bsdOriginal;
        description = "A high-level Python Web framework that encourages rapid development and clean, pragmatic design.";
      };
    };

    "docutils" = python.mkDerivation {
      name = "docutils-0.15";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/72/0b/d728058694261c99fd5980419d77e1c4d63a390b26a6a0ea7f0993cd5c57/docutils-0.15.tar.gz";
        sha256 = "54a349c622ff31c91cbec43b0b512f113b5b24daf00e2ea530bb1bd9aac14849";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://docutils.sourceforge.net/";
        license = "public domain, Python, 2-Clause BSD, GPL 3 (see COPYING.txt)";
        description = "Docutils -- Python Documentation Utilities";
      };
    };

    "graphene" = python.mkDerivation {
      name = "graphene-2.1.7";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/98/30/6ef08e720ef4cfe9f2bab6b09250251bde60cda93d010ed8e16081070e1a/graphene-2.1.7.tar.gz";
        sha256 = "77d61618132ccd084c343e64c22d806cee18dce73cc86e0f427378dbdeeac287";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."aniso8601"
        #self."graphene-django"
        self."graphql-core"
        self."graphql-relay"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphene";
        license = licenses.mit;
        description = "GraphQL Framework for Python";
      };
    };

    "graphene-django" = python.mkDerivation {
      name = "graphene-django-2.1.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/6a/8e/b47059cb56ab9e9c24f0baae3e0bb0f1e4c28be6a3e9d0e2deebd0ddfa6d/graphene-django-2.1.0.tar.gz";
        sha256 = "6abc3ec4f1dcbd91faeb3ce772b428e431807b8ec474f9dae918cff74bf7f6b1";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."django"
        self."graphene"
        self."graphql-core"
        self."iso8601"
        self."promise"
        self."singledispatch"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphene-django";
        license = "MIT";
        description = "Graphene Django integration";
      };
    };

    "graphql-core" = python.mkDerivation {
      name = "graphql-core-2.2.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/98/9b/7a610ac16df594e18263db0404367bd1523127cf7f280285b0f7765be89c/graphql-core-2.2.1.tar.gz";
        sha256 = "da64c472d720da4537a2e8de8ba859210b62841bd47a9be65ca35177f62fe0e4";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."promise"
        self."rx"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphql-core";
        license = "MIT";
        description = "GraphQL implementation for Python";
      };
    };

    "graphql-relay" = python.mkDerivation {
      name = "graphql-relay-2.0.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/a0/83/bea0cd12b51e1459d6702b0975d2f42ae4607021f22ec90c50b03c397fcc/graphql-relay-2.0.0.tar.gz";
        sha256 = "7fa74661246e826ef939ee92e768f698df167a7617361ab399901eaebf80dce6";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."graphql-core"
        self."promise"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphql-relay-py";
        license = "MIT";
        description = "Relay implementation for Python";
      };
    };

    "iso8601" = python.mkDerivation {
      name = "iso8601-0.1.12";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/45/13/3db24895497345fb44c4248c08b16da34a9eb02643cea2754b21b5ed08b0/iso8601-0.1.12.tar.gz";
        sha256 = "49c4b20e1f38aa5cf109ddcd39647ac419f928512c869dc01d5c7098eddede82";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://bitbucket.org/micktwomey/pyiso8601";
        license = "MIT";
        description = "Simple module to parse ISO 8601 dates";
      };
    };

    "promise" = python.mkDerivation {
      name = "promise-2.2.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/5a/81/221d09d90176fd90aed4b530e31b8fedf207385767c06d1d46c550c5e418/promise-2.2.1.tar.gz";
        sha256 = "348f5f6c3edd4fd47c9cd65aed03ac1b31136d375aa63871a57d3e444c85655c";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/syrusakbary/promise";
        license = "MIT";
        description = "Promises/A+ implementation for Python";
      };
    };

    "pyyaml" = python.mkDerivation {
      name = "pyyaml-5.1.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/a3/65/837fefac7475963d1eccf4aa684c23b95aa6c1d033a2c5965ccb11e22623/PyYAML-5.1.1.tar.gz";
        sha256 = "b4bb4d3f5e232425e25dda21c070ce05168a786ac9eda43768ab7f3ac2770955";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/yaml/pyyaml";
        license = "MIT";
        description = "YAML parser and emitter for Python";
      };
    };

    "reserved" = python.mkDerivation {
      name = "reserved-0.1.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/71/df/1aa392c666f6d59e71424367f488191f31915527f75d13d2dd415a849e2f/reserved-0.1.1.tar.gz";
        sha256 = "0bf2eadeabd486f70b1225677dfafddf06b864ce3d621ff833bca08ef0c7adca";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."pyyaml"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/aykevl/reserved";
        license = licenses.bsdOriginal;
        description = "Check usernames for reserved email addresses, subdomains, or Unix usernames.";
      };
    };

    "rx" = python.mkDerivation {
      name = "rx-1.6.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/25/d7/9bc30242d9af6a9e9bf65b007c56e17b7dc9c13f86e440b885969b3bbdcf/Rx-1.6.1.tar.gz";
        sha256 = "13a1d8d9e252625c173dc795471e614eadfe1cf40ffc684e08b8fff0d9748c23";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://reactivex.io";
        license = "Apache License";
        description = "Reactive Extensions (Rx) for Python";
      };
    };

    "sdnotify" = python.mkDerivation {
      name = "sdnotify-0.3.2";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ce/d8/9fdc36b2a912bf78106de4b3f0de3891ff8f369e7a6f80be842b8b0b6bd5/sdnotify-0.3.2.tar.gz";
        sha256 = "73977fc746b36cc41184dd43c3fe81323e7b8b06c2bb0826c4f59a20c56bb9f1";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/bb4242/sdnotify";
        license = "UNKNOWN";
        description = "A pure Python implementation of systemd's service notification protocol (sd_notify)";
      };
    };

    "singledispatch" = python.mkDerivation {
      name = "singledispatch-3.4.0.3";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/d9/e9/513ad8dc17210db12cb14f2d4d190d618fb87dd38814203ea71c87ba5b68/singledispatch-3.4.0.3.tar.gz";
        sha256 = "5b06af87df13818d14f08a028e42f566640aef80805c3b50c5056b086e3c2b9c";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://docs.python.org/3/library/functools.html#functools.singledispatch";
        license = "MIT";
        description = "This library brings functools.singledispatch from Python 3.4 to Python 2.6-3.3.";
      };
    };

    "six" = python.mkDerivation {
      name = "six-1.12.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/dd/bf/4138e7bfb757de47d1f4b6994648ec67a51efe58fa907c1e11e350cddfca/six-1.12.0.tar.gz";
        sha256 = "d16a0141ec1a18405cd4ce8b4613101da75da0e9a7aec5bdd4fa804d0e0eba73";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/benjaminp/six";
        license = "MIT";
        description = "Python 2 and 3 compatibility utilities";
      };
    };

    "zipseeker" = python.mkDerivation {
      name = "zipseeker-1.0.11";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/35/21/00435b5ea857c82ca47d305fbd569bb07d0f459100cdde8520eda2fd3139/zipseeker-1.0.11.tar.gz";
        sha256 = "f0bc6b8dd5a66a8e09c98cb41ffeb31b83e2fc99d3f947afeda60c7605210e82";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/aykevl/python-zipseeker";
        license = "UNKNOWN";
        description = "Create a streamable and (somewhat) seekable .ZIP file";
      };
    };
  };
  localOverridesFile = ./requirements_override.nix;
  localOverrides = import localOverridesFile { inherit pkgs python; };
  commonOverrides = [
    
  ];
  paramOverrides = [
    (overrides { inherit pkgs python; })
  ];
  allOverrides =
    (if (builtins.pathExists localOverridesFile)
     then [localOverrides] else [] ) ++ commonOverrides ++ paramOverrides;

in python.withPackages
   (fix' (pkgs.lib.fold
            extends
            generated
            allOverrides
         )
   )
