help:
	@printf "\nWelcome to the IoT-LAB development environment setup.\n\n"
	@echo "targets:"
	@egrep '^setup-[^%:]+:' Makefile | sed 's/:.*//; s/^/\t/' && echo

setup-wsn430 : parts/wsn430
	parts/wsn430/install.sh | less

setup-openlab: parts/openlab
	less parts/openlab/README_COMPILING

contiki_plug = parts/contiki/platform/openlab/git
setup-contiki: parts/openlab parts/contiki $(contiki_plug)
	less parts/contiki/README-BUILDING.md

$(contiki_plug):
	ln -sT ../../../openlab $@


parts/%:
	git clone git@github.com:iot-lab/$*.git parts/$*

setup-%: parts/%;

.PHONY: help setup-%
.PRECIOUS: parts/%
