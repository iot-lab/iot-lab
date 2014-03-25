help:
	@printf "\nWelcome to the IoT-LAB development environment setup.\n\n"
	@echo "targets:"
	@egrep '^setup-[^%:]+:' Makefile | sed 's/:.*//; s/^/\t/' && echo

setup-wsn430 : parts/wsn430
	parts/wsn430/install.sh | less

setup-openlab: parts/openlab
	less parts/openlab/README_COMPILING

setup-contiki: parts/openlab parts/contiki
	less parts/contiki/README-BUILDING.md


parts/%:
	git clone https://github.com/iot-lab/$*.git parts/$*

setup-%: parts/%;

.PHONY: help setup-%
.PRECIOUS: parts/%
