{
  description = "IMACS: Intelligent Multi-Agent Chores Scheduler";

  inputs = {
    nixpkgs.url = "nixpkgs";
    django-nixos.url = "github:pnmadelaine/django-nixos";
  };

  outputs = { self, nixpkgs, django-nixos }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
    args = {
      name = "imacs";
      keys-file = "${./dev_secrets.sh}";
      src = ./.;
      inherit pkgs;
      settings = "imacs.settings.nix";
    };
    nixosModule = django-nixos.lib.mkNixosModule args;
    python = pkgs.python38.withPackages (ps: with ps; [ django_3 ]);
  in
  {
    devShell.${system} = pkgs.stdenv.mkDerivation {
      name = "django-dev-shell";
      buildInputs = [ python ];
      shellHook = ''
        source ${./dev_secrets.sh}
      '';
    };
    nixosModules = { imacs = nixosModule; };
    inherit nixosModule;
  };
}
