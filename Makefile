#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Todo: add
# python /opt/python/generateDS-2.7c/generateDS.py -o report.py report.xsd

#
# Makefile for Red Hat Support Library
#

# ex. export APP_VERSION=1.0.0
#RPM_VERSION:=$(shell echo $(APP_VERSION) | sed "s/-/_/")
RPM_VERSION:=1.0.0
# ex. export APP_RELEASE=1
#RPM_RELEASE:=$(shell echo $(APP_RELEASE) | sed "s/-/_/")
RPM_RELEASE:=0
RPMTOP=$(shell bash -c "pwd -P")/rpmtop
SPEC_FILE_IN=redhat-support-lib-python.spec.in
SPEC_FILE=redhat-support-lib-python.spec
TARBALL=redhat-support-lib-python-$(RPM_VERSION).tar.gz
SRPM=$(RPMTOP)/SRPMS/redhat-support-lib-python-$(RPM_VERSION)-$(RPM_RELEASE)*.src.rpm

TESTS=pyflakes

all: rpm

test: pyflakes exceptions
		echo $(RPM_RELEASE) $(RPM_VERSION)

pyflakes:
		@git ls-files '*.py' | xargs pyflakes \
            || (echo "Pyflakes errors or pyflakes not found"; exit 1)

.PHONY: tarball
tarball: $(TARBALL)
$(TARBALL): Makefile #$(TESTS)
		git archive --format=tar --prefix redhat-support-lib-python/ HEAD | gzip > $(TARBALL)

.PHONY: srpm rpm
srpm: $(SRPM)
$(SRPM): $(TARBALL) $(SPEC_FILE_IN)
		sed 's/^Version:.*/Version: $(RPM_VERSION)/;s/^Release:.*/Release: $(RPM_RELEASE)%{dist}/;s/%{release}/$(RPM_RELEASE)/' $(SPEC_FILE_IN) > $(SPEC_FILE)
		mkdir -p $(RPMTOP)/{RPMS,SRPMS,SOURCES,BUILD}
		rpmbuild -bs \
            --define="_topdir $(RPMTOP)" \
            --define="_sourcedir ." $(SPEC_FILE)

rpm: $(SRPM)
		rpmbuild --define="_topdir $(RPMTOP)" --rebuild $<

clean:
		@for i in `find . -iname *.pyc`; do \
                rm $$i; \
        done; \
        for i in `find . -iname *.pyo`; do \
                rm $$i; \
        done; \
        rm -rf $(SPEC_FILE) $(RPMTOP) $(TARBALL)
