{ config, lib, ... }:

let cfg = config.kn.fotos;

in {
  options.kn.fotos = {
    enable = lib.mkEnableOption "fotos";
    dir = lib.mkOption {
      type = lib.types.path;
      default = "/var/fotos";
      description = ''
        The daan service will create event directories here and the kndjango
        service will put photos in them.
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    # kndjango and daan will create stuff here under their own user and with the
    # fotos group.
    systemd.tmpfiles.rules = [ "d ${cfg.dir} 0770 fotos fotos -" ];

    users.users.fotos = {
      isSystemUser = true;
      group = "fotos";
    };

    users.groups.fotos = { };
  };
}
