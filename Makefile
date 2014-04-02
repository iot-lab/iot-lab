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


all: $(addprefix setup-, $(REPOS))


# Pull in new changes

pull: $(subst parts/,pull-,$(wildcard parts/*))
	git pull
pull-%: parts/%
	cd $^; git pull; cd -
	@# Following does not work on the server because of a git bug 1.7.2.5
	@# git --work-tree=$(shell readlink -e $^) --git-dir=$(shell readlink -e $^/.git) pull

setup-%: parts/%;



#
# Run tests
#
tests: openlab-tests contiki-tests tools_and_scripts__tests
tools_and_scripts__tests:
	bash tools_and_scripts/tests/run_tests.sh
%-tests: parts/%
	make -C $^ -f iotlab.makefile tests

tests-clean: openlab-tests-clean contiki-tests-clean
%-tests-clean: parts/%
	make -C $^ -f iotlab.makefile clean




.PHONY: help setup-% pull pull-% tests tests-%
.PRECIOUS: parts/%
