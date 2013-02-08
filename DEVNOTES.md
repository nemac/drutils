Workflow for building rpm releases using tito
=============================================

0. Do this just once, to initialize the project in tito:

    tito init

1. Edit/Test

    1. Make changes to source

    2. Use git to commit changes

    3. Build: tito build --rpm --test

2. Finalize a release

    1. Tag: tito tag --accept-auto-changelog

    2. Push: git push && git push $ORIGIN $TAG

    3. Build: tito build --rpm
