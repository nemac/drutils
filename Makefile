prefix=/usr/local
libdir=${prefix}/lib/drutils
bindir=${prefix}/bin
EDIT_LIB_DIR=sed -e 's|^sys\.path\.append.*this line gets replaced.*$$|sys.path.append("${libdir}")|'

.PHONY: _always

all:

install:
	${EDIT_LIB_DIR} < dumpsite > dumpsite.edited
	install -D -m 0755 dumpsite.edited ${bindir}/dumpsite
	/bin/rm -f dumpsite.edited
	install -D drutils.py ${libdir}/drutils.py
