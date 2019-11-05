{ pkgs, python }:

self: super: {
  sarah = (python.mkDerivation rec {
    name = "sarah-${version}";
    version = "0.1.4";
    buildInputs = with self; [ docutils six ];
    doCheck = false;
    patchPhase = ''
      sed -i '/mirte/d' setup.py
    '';
    src = pkgs.fetchFromGitHub {
      owner = "bwesterb";
      repo = "sarah";
      rev = version;
      sha256 = "135fbz41f5nb68bz6w3997x6l9b930ld8ivv0bfvviq7dgym7782";
    };
  });
  mirte = (python.mkDerivation rec {
    name = "mirte-${version}";
    version = "0.1.8";
    patchPhase = ''
      sed -i 's/msgpack-python/msgpack/' setup.py
    '';
    buildInputs = with self; [ pyyaml docutils pkgs.python37Packages.msgpack six sarah ];
    src = pkgs.fetchFromGitHub {
      owner = "bwesterb";
      repo = "mirte";
      rev = version;
      sha256 = "06y6wlpprcvmqi7a4xzr6b0qyi2rxvrgrp88i62n6243n9g9hv8x";
    };
  });
  graphene-django = super.graphene-django.overrideDerivation (o: rec {
    propagatedBuildInputs = o.propagatedBuildInputs ++ [ pkgs.python37Packages.pytestrunner ];
  });
  graphene = super.graphene.overrideAttrs (o: {
    propagatedBuildInputs = (builtins.filter (x: x.name != "graphene-django") o.propagatedBuildInputs);
  });
  tarjan = (python.mkDerivation rec {
    pname = "tarjan";
    version = "0.2.4.dev0";
    buildInputs = [];
    src = pkgs.fetchFromGitHub {
      owner = "bwesterb";
      repo = "py-tarjan";
      rev = "e6e89524601b0f8d4b4a94423cde5c5abc5a04ec";
      sha256 = "0a013cgzc3bk2c4d40ccpbjm9pqcdhk8ks7knnghdl12d54g4xdm";
    };
  });
  inherit (pkgs.python37Packages)
    pymongo six protobuf grpcio
    msgpack html2text unidecode pyx pillow
    markdown pyparsing ldap httplib2 oauth2client google_api_python_client
    pymysql;
}
