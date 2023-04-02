{ config, lib, ... }:

let cfg = config.kn.fotos;

in {
  options.kn.fotos = {
    enable = lib.mkEnableOption "fotos";
    dir = lib.mkOption {
      type = lib.types.path;
      default = "/var/fotos";
      description = ''
        Directory with all fotos in directories named after events.
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.tmpfiles.rules = [ "d ${cfg.dir} 0550 root infra -" ];

    users.users.fotos = {
      isSystemUser = true;
      group = "fotos";
    };

    users.groups.fotos = { };
  };
}
