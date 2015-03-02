# Add new repositories in REPOS variable

REPOS = contiki wsn430 openlab cli-tools aggregation-tools riot
SETUP_REPOS = $(sort $(addprefix setup-, $(REPOS)))

help:
	@printf "\nWelcome to the IoT-LAB development environment setup.\n\n"
	@printf "targets:\n"
	@for setup_cmd in $(SETUP_REPOS); do \
		printf "\t$${setup_cmd}\n";    \
	done
	@echo  ""
	@printf "\tpull\n"
	@echo  ""


all: $(addprefix setup-, $(REPOS))
setup-%: parts/%
parts/%:
	git clone https://github.com/iot-lab/$*.git $@


# print documentation on release
setup-wsn430: parts/wsn430
	cat parts/wsn430/README.md

setup-openlab: parts/openlab
	cat parts/openlab/README-IoT-LAB.md

setup-contiki: parts/contiki
	cat parts/contiki/README-IoT-LAB.md

# External repository
setup-riot: parts/RIOT
parts/RIOT:
	git clone https://github.com/RIOT-OS/RIOT.git $@


# Pull in new changes

pull: $(subst parts/,pull-,$(wildcard parts/*))
	git pull
pull-%: parts/%
	cd $^; git pull; cd -


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
