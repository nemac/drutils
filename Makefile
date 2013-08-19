root=/
prefix=/usr/local
libdir=${prefix}/lib/drutils
bindir=${prefix}/bin
dest_prefix=${prefix}
dest_libdir=${dest_prefix}/lib/drutils
EDIT_LIB_DIR=sed -e 's|^sys\.path\.append.*this line gets replaced.*$$|sys.path.append("${dest_libdir}")|'

.PHONY: _always

all:

install:
	install -D drutils.py ${libdir}/drutils.py
	${EDIT_LIB_DIR} < dumpsite > dumpsite.edited ; install -D -m 0755 dumpsite.edited ${bindir}/dumpsite ; /bin/rm -f dumpsite.edited
	${EDIT_LIB_DIR} < loadsite > loadsite.edited ; install -D -m 0755 loadsite.edited ${bindir}/loadsite ; /bin/rm -f loadsite.edited
	${EDIT_LIB_DIR} < makesite > makesite.edited ; install -D -m 0755 makesite.edited ${bindir}/makesite ; /bin/rm -f makesite.edited
	${EDIT_LIB_DIR} < dbcreate > dbcreate.edited ; install -D -m 0755 dbcreate.edited ${bindir}/dbcreate ; /bin/rm -f dbcreate.edited
	${EDIT_LIB_DIR} < dblist > dblist.edited ; install -D -m 0755 dblist.edited ${bindir}/dblist ; /bin/rm -f dblist.edited
	${EDIT_LIB_DIR} < dbdrop > dbdrop.edited ; install -D -m 0755 dbdrop.edited ${bindir}/dbdrop ; /bin/rm -f dbdrop.edited
	${EDIT_LIB_DIR} < dbpw > dbpw.edited ; install -D -m 0755 dbpw.edited ${bindir}/dbpw ; /bin/rm -f dbpw.edited
	mkdir -p ${root}var/drutils/mysql
	chmod g=,o= ${root}var/drutils/mysql
