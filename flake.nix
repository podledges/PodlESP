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
            # project() name varies per firmware folder
            elf=$(echo build/*.elf | awk '{print $1}')
            bin=$(echo build/*.bin | awk 'NR==1{print; exit}')
            cp "$elf" "$out/firmware.elf"
            cp build/*.bin "$out/" 2>/dev/null || true
            # keep legacy smoke names when present
            if [ -f build/podlesp-smoke.elf ]; then cp build/podlesp-smoke.elf "$out/"; fi
            if [ -f build/podlesp-smoke.bin ]; then cp build/podlesp-smoke.bin "$out/"; fi
            if [ -f build/podlesp-led-pattern.elf ]; then cp build/podlesp-led-pattern.elf "$out/"; fi
            if [ -f build/podlesp-led-pattern.bin ]; then cp build/podlesp-led-pattern.bin "$out/"; fi
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

      ledPattern = mkEspIdfFirmware {
        pname = "podlesp-esp32-s3-touch-lcd-1-9-led-pattern";
        target = "esp32s3";
        src = ./boards/esp32-s3-touch-lcd-1.9/led-pattern;
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
        led-pattern = ledPattern;
      };

      checks.${system}.smoke = smoke;
      checks.${system}.led-pattern = ledPattern;
    };
}
