{ config, lib, pkgs, ... }:

let
  cfg = config.services.imacs;
  inherit (lib) types;
in {
  options = {
    services.imacs = {
      enable = lib.mkEnableOption "Intelligent Multi-Agent Chores Scheduler";
      unsafeSettings = lib.mkOption {
        description = ''
          Disable security settings, for testing only.
          You may have to clear your browser HSTS cache for it to take effect.
        '';
        type = types.bool;
        default = false;
      };
      hostName = lib.mkOption {
        description = "The hostname IMACS is served on";
        type = types.nonEmptyStr;
        default = "localhost";
      };
      keysFile = lib.mkOption {
        description = "Path to the secret keys file";
        type = types.either types.nonEmptyStr types.path;
      };
      setupNginx = lib.mkOption {
        description = "Whether to setup nginx";
        type = types.bool;
        default = true;
      };
    };
  };

  config = lib.mkIf cfg.enable
    (lib.mkMerge [
      {
        services.django.enable = true;
        services.django.servers.imacs = {
          root = ./.;
          settings = if cfg.unsafeSettings
                     then "imacs.settings.nix-unsafe"
                     else "imacs.settings.nix";
          port = 8001;
          inherit (cfg) keysFile setupNginx hostName;
        };

        warnings = if cfg.unsafeSettings
                   then [ "IMACS is configured with unsafe settings" ]
                   else [ ];
      }
      (lib.mkIf (cfg.enable && cfg.setupNginx) { services.nginx.enable = true; })
      (lib.mkIf (cfg.enable && cfg.setupNginx && !cfg.unsafeSettings) {
        services.nginx.virtualHosts."${cfg.hostName}".forceSSL = true;
      })
    ]);
}
