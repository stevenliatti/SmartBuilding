run_example: knx.py
	./knx.py "3/4/1" 100 2 2

run_actuasim: install
	actuasim_iot/actuasim.py &

install: knxnet_iot actuasim_iot

knxnet_iot:
	sudo apt-get update && sudo apt-get install -y python3-setuptools python3-pyqt5 git
	git clone https://gitedu.hesge.ch/adrienma.lescourt/knxnet_iot.git
	cd knxnet_iot && sudo python3 setup.py install

actuasim_iot:
	git clone https://gitedu.hesge.ch/steven.liatti/actuasim_iot.git

docker_run:
	docker run -it -v "$$PWD":/root/app -w /root/app py-knx

docker_build:
	docker build -t py-knx .

clean:
	sudo rm -rf knxnet_iot actuasim_iot *.json *.log
