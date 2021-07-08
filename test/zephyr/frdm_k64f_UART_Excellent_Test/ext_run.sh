#! /bin/bash

while true; do
    read -p "Did you start the Halucinator virtual environment? [Y/N]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Please start it and try again"; exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo "Starting UART terminal"
hal_dev_uart --id=0 --newline
