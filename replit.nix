{pkgs}: {
  deps = [
    pkgs.nano
    pkgs.unixtools.ping
    pkgs.playwright-driver
    pkgs.gitFull
    pkgs.cacert
    pkgs.iana-etc
    pkgs.wget
  ];
}
