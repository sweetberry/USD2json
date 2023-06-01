command_file="usd2json.command"
self_dir=$(cd $(dirname $0); pwd)
touch $command_file
echo 'cd '$self_dir > $command_file
echo 'pipenv run app' >> $command_file
chmod +x $command_file
