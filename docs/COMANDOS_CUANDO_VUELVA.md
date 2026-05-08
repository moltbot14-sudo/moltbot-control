# Comandos cuando vuelva a los Ubuntu

## En cada Ubuntu

Ejecutar esto:

```bash
sudo apt update
sudo apt install git curl -y

cd ~
git clone https://github.com/TU_USUARIO/moltbot-control.git
cd moltbot-control

chmod +x install_later.sh
./install_later.sh
