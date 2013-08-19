Workflow for building rpm releases using tito
=============================================

0. Do this just once, to initialize the project in tito:

        tito init


1. Edit/Test

    1. Make changes to source

    2. Use git to commit changes

    3. Build: tito build --rpm --test


2. Finalize a release

       NOTE: for these steps to work, vagrant user needs ssh keys that allow access to github
             repo nemac/drutils, and for access to dev.nemac.org

    1. Tag: tito tag --accept-auto-changelog

    2. Push: git push && git push $ORIGIN $TAG

    3. Build: 
         rm -rf /tmp/tito/* ; tito build --rpm

    4. Update the yum repo at http://dev.nemac.org/yum-repo:
         ./updaterepo


For more info, see *man tito*, or https://github.com/dgoodwin/tito.
