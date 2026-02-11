{
  description = "mkdocstrings-R";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/c05d2232d2feaa4c7a07f1168606917402868195";
  };

  outputs =
    { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
    in
    {
      devShells."${system}".default =
        let
          pkgs = import nixpkgs { inherit system; };
        in
        pkgs.mkShell {
          packages = with pkgs; [
            python314
            uv
            R
            radian
          ];
          shellHook = ''
            VENV=.venv
              if ! [ -d $VENV ]; then
              uv venv .venv --no-managed-python
            fi

            source .venv/bin/activate

            export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH
          '';
        };

    };
}
