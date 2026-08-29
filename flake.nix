{
  description = "mkdocstrings-R";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/c27cdad491a991b11ed731760aa2ef8db0cb0410";
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
            python313
            uv
            R
            radian
            rPackages.renv

            # For rpy2
            zstd
            xz
            bzip2
            zlib
            icu
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
