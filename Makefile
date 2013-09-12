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
	install -D NapplMeta.py	  ${libdir}/NapplMeta.py  
	install -D Nappl.py ${libdir}/Nappl.py
	install -D EtcHoster.py	  ${libdir}/EtcHoster.py  
	install -D Container.py ${libdir}/Container.py
	install -D ApacheContainer.py ${libdir}/ApacheContainer.py
	install -D DrupalContainer.py ${libdir}/DrupalContainer.py
	${EDIT_LIB_DIR} < nappl > nappl.edited ; install -D -m 0755 nappl.edited ${bindir}/nappl ; /bin/rm -f nappl.edited
	mkdir -p ${root}var/drutils/mysql
	chmod g=,o= ${root}var/drutils/mysql
	mkdir -p ${root}var/nappl
	chmod g=,o= ${root}var/nappl
	mkdir -p ${root}deploy
	mkdir -p ${root}dumps
	mkdir -p ${root}var/vsites
	mkdir -p ${root}var/vsites/conf
	mkdir -p ${root}var/vsites/mysql


