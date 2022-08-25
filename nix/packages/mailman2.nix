{ stdenv, lib, fetchurl, python2 }:

stdenv.mkDerivation rec {
  name = "mailman-${version}";
  version = "2.1.39";

  src = fetchurl {
    url = "mirror://gnu/mailman/${name}.tgz";
    hash = "sha256-e46SIjZKvf0lyyBTxCIxmqx7Ygwofdl5cD4DmdcvQ5A=";
  };

  buildInputs = [ python2 (python2.pkgs.buildPythonPackage (rec {
    pname = "dnspython";
    version = "1.16.0";
    src = python2.pkgs.fetchPypi {
      inherit pname version;
      extension = "zip";
      sha256 = "36c5e8e38d4369a08b6780b7f27d790a292b2b08eea01607865bf0936c558e01";
    };
    doCheck = false;
  })) ];

  patches = [ ./fix-var-prefix.patch ];

  configureFlags = [
    "--without-permcheck"
    "--with-cgi-gid=cgi"
    "--with-var-prefix=/var/lib/mailman"
  ];

  installTargets = "doinstall"; # Leave out the 'update' target that's implied by 'install'.
  postInstall = ''
    rm -f $out/Mailman/mm_cfg.py $out/Mailman/mm_cfg.pyc
    ln -s /etc/mailman_cfg.py $out/Mailman/mm_cfg.py
    cp -r misc $out/
  '';

  makeFlags = [ "DIRSETGID=:" ];

  meta = {
    homepage = https://www.gnu.org/software/mailman/;
    description = "Free software for managing electronic mail discussion and e-newsletter lists";
    license = lib.licenses.gpl2Plus;
    platforms = lib.platforms.linux;
    maintainers = [ lib.maintainers.yorickvp ];
  };
}
