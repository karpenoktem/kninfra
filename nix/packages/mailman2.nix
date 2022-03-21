{ stdenv, lib, fetchurl, python2 }:

stdenv.mkDerivation rec {
  name = "mailman-${version}";
  version = "2.1.39";

  src = fetchurl {
    url = "mirror://gnu/mailman/${name}.tgz";
    hash = "sha256-e46SIjZKvf0lyyBTxCIxmqx7Ygwofdl5cD4DmdcvQ5A=";
  };

  buildInputs = [ python2 python2.pkgs.dnspython ];

  patches = [ ./fix-var-prefix.patch ];

  configureFlags = [
    "--without-permcheck"
    "--with-cgi-ext=.cgi"
    "--with-var-prefix=/var/lib/mailman"
  ];

  installTargets = "doinstall"; # Leave out the 'update' target that's implied by 'install'.

  makeFlags = [ "DIRSETGID=:" ];

  meta = {
    homepage = https://www.gnu.org/software/mailman/;
    description = "Free software for managing electronic mail discussion and e-newsletter lists";
    license = lib.licenses.gpl2Plus;
    platforms = lib.platforms.linux;
    maintainers = [ lib.maintainers.yorickvp ];
  };
}
