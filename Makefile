prefix=/usr/local
libdir=${prefix}/lib/drutils
bindir=${prefix}/bin
EDIT_LIB_DIR=sed -e 's|^sys\.path\.append.*this line gets replaced.*$$|sys.path.append("${libdir}")|'

.PHONY: _always

all:

install:
	install -D drutils.py ${libdir}/drutils.py
	${EDIT_LIB_DIR} < dumpsite > dumpsite.edited
	install -D -m 0755 dumpsite.edited ${bindir}/dumpsite
	/bin/rm -f dumpsite.edited
	${EDIT_LIB_DIR} < loadsite > loadsite.edited
	install -D -m 0755 loadsite.edited ${bindir}/loadsite
	/bin/rm -f loadsite.edited
