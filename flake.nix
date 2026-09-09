{
  description = "Reproducible ESP-IDF development environment for PodlESP";

  inputs = {
    nixpkgs.follows = "nixpkgs-esp-dev/nixpkgs";
    nixpkgs-esp-dev.url = "github:mirrexagon/nixpkgs-esp-dev";
  };

  outputs =
    {
      self,
      nixpkgs,
      nixpkgs-esp-dev,
    }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      espIdf = nixpkgs-esp-dev.packages.${system}.esp-idf-full;

      mkEspIdfFirmware =
        {
          pname,
          target,
          src,
        }:
        pkgs.stdenv.mkDerivation {
          inherit pname src;
          version = "0.1.0";

          nativeBuildInputs = [ espIdf ];
          phases = [
            "unpackPhase"
            "buildPhase"
            "installPhase"
          ];

          buildPhase = ''
            runHook preBuild
            export HOME="$TMPDIR/home"
            mkdir -p "$HOME"
            export IDF_COMPONENT_MANAGER=0
            export CMAKE_BUILD_PARALLEL_LEVEL="''${NIX_BUILD_CORES:-2}"
            export NINJAFLAGS="-j''${NIX_BUILD_CORES:-2}"
            idf.py set-target ${target}
            idf.py build
            runHook postBuild
          '';

          installPhase = ''
            runHook preInstall
            mkdir -p "$out"
            cp build/podlesp-smoke.elf "$out/"
            cp build/podlesp-smoke.bin "$out/"
            cp build/bootloader/bootloader.bin "$out/"
            cp build/partition_table/partition-table.bin "$out/"
            cp build/flasher_args.json "$out/"
            runHook postInstall
          '';
        };

      smoke = mkEspIdfFirmware {
        pname = "podlesp-esp32-s3-touch-lcd-1-9-smoke";
        target = "esp32s3";
        src = ./boards/esp32-s3-touch-lcd-1.9/smoke;
      };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        name = "podlesp-esp-idf";
        packages = [ espIdf ];
      };

      packages.${system} = {
        default = smoke;
        inherit smoke;
      };

      checks.${system}.smoke = smoke;
    };
}
