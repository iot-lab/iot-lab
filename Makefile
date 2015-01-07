REPOS = contiki wsn430 openlab cli-tools

help:
	@printf "\nWelcome to the IoT-LAB development environment setup.\n\n"
	@echo "targets:"
	@egrep '^setup-[^%:]+:' Makefile | sed 's/:.*//; s/^/\t/' && echo
	@echo  "	pull"
	@echo  ""

setup-wsn430 : parts/wsn430
	cat parts/wsn430/README.md

setup-openlab: parts/openlab
	cat parts/openlab/README-IoT-LAB.md

setup-contiki: parts/openlab parts/contiki
	cat parts/contiki/README-IoT-LAB.md

setup-riot: parts/RIOT


# Tools
setup-cli-tools: parts/cli-tools

setup-aggregation-tools: parts/aggregation-tools


parts/RIOT:
	git clone https://github.com/RIOT-OS/RIOT.git $@

parts/%:
	git clone https://github.com/iot-lab/$*.git $@


all: $(addprefix setup-, $(REPOS))


# Pull in new changes

pull: $(subst parts/,pull-,$(wildcard parts/*))
	git pull
pull-%: parts/%
	cd $^; git pull; cd -
	@# Following does not work on the server because of a git bug 1.7.2.5
	@# git --work-tree=$(shell readlink -e $^) --git-dir=$(shell readlink -e $^/.git) pull

setup-%: parts/%



#
# Run tests
#
tests: openlab-tests contiki-tests wsn430-tests tools_and_scripts__tests
tools_and_scripts__tests:
	bash tools_and_scripts/tests/run_tests.sh
%-tests: parts/%
	make -C $^ -f iotlab.makefile tests

tests-clean: openlab-tests-clean contiki-tests-clean wsn430-tests
%-tests-clean: parts/%
	make -C $^ -f iotlab.makefile clean




.PHONY: help setup-% pull pull-% tests tests-%
.PRECIOUS: parts/%
