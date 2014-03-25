REPOS = contiki wsn430 openlab cli-tools

help:
	@printf "\nWelcome to the IoT-LAB development environment setup.\n\n"
	@echo "targets:"
	@egrep '^setup-[^%:]+:' Makefile | sed 's/:.*//; s/^/\t/' && echo
	@echo  "	pull"
	@echo  ""

setup-wsn430 : parts/wsn430
	parts/wsn430/install.sh | less

setup-openlab: parts/openlab
	less parts/openlab/README_COMPILING

setup-contiki: parts/openlab parts/contiki
	less parts/contiki/README-BUILDING.md

setup-cli-tools: parts/cli-tools

parts/%:
	git clone https://github.com/iot-lab/$*.git parts/$*


# Pull in new changes

pull: $(addprefix pull-, $(REPOS))
	git pull
pull-%: parts/%
	cd $^; git pull; cd -
	@# Following does not work on the server because of a git bug 1.7.2.5
	@# git --work-tree=$(shell readlink -e $^) --git-dir=$(shell readlink -e $^/.git) pull

setup-%: parts/%;

.PHONY: help setup-% pull pull-%
.PRECIOUS: parts/%
