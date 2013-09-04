openssh-server:
  pkg:
    - latest

ssh:
  service:
    - running

  require:
    - pkg: openssh-server
