let
  users = builtins.mapAttrs (k: v: v.agekey or (builtins.head v.sshkeys))
    (builtins.fromTOML (builtins.readFile ../nix/users.toml));
  hosts = {
    vm = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAA9K8nzOTUOhGeuZbWl2eb7qi3qzhB70hyT2rKsRarI";
    staging = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKqWsHmgcjvjl22xNE8kjtIbZ3BSIA+z9drzbKLoSnaE";
    production = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILcgLIlUI9xDCZcLWt10QVtggmMPKV4P+nVD7FhkeOus";
  };
  allUsers = builtins.attrValues users;
in with hosts; {
  "vm.age".publicKeys = allUsers ++ [ vm ];
  "staging.age".publicKeys = allUsers ++ [ staging ];
  "production.age".publicKeys = allUsers ++ [ production ];
  "google-oauth-key.json.age".publicKeys = allUsers ++ [ production ];
}
