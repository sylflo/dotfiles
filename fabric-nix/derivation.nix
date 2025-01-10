{
  lib,
  fetchFromGitHub,
  python311Packages,
  gtk3,
  gtk-layer-shell,
  cairo,
  gobject-introspection,
  libdbusmenu-gtk3,
  gdk-pixbuf,
  cinnamon,
  gnome,
  pkg-config,
  wrapGAppsHook3,
}:

python311Packages.buildPythonPackage {
  pname = "python-fabric";
  version = "0.0.1";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "Fabric-Development";
    repo = "fabric";
    rev = "c81e4f148add9d2d15820a4a1a704931315f24de";
    sha256 = "sha256-0a2As4+9/mPVfrQrby8/QVqqsCUcVfXJ3MNLWZqtDMg=";
    #rev = "1134b7f96ecc54d2626788ad59b4717ed86e5cf4";
    #sha256 = "sha256-t+tb+0isS/AloTd+HUkCvfpNXOl6RkkenIPxMsk++LA=";
  };

  nativeBuildInputs = [
    pkg-config
    wrapGAppsHook3
    gobject-introspection
    cairo
  ];

  propagatedBuildInputs = [
    gtk3
    gtk-layer-shell
    libdbusmenu-gtk3
    cinnamon.cinnamon-desktop
    gnome.gnome-bluetooth
  ];

  dependencies = with python311Packages; [
    setuptools
    click
    pycairo
    pygobject3
    pygobject-stubs
    loguru
    psutil
  ];

  meta = {
    changelog = "";
    description = ''
      next-gen framework for building desktop widgets using Python (check the rewrite branch for progress)
    '';
    homepage = "https://github.com/Fabric-Development/fabric";
    license = lib.licenses.agpl3Only;
    maintainers = with lib.maintainers; [ ];
  };
}
