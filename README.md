kninfra
=======

Een groot deel van de digitale infrastructuur van [ASV Karpe Noktem](http://karpenoktem.nl).

Vindt onder

 * `kn/static`. Homepage
 * `kn/leden`. Smoelenboek (en ledenadministratie)
 * `kn/fotos`. Fotoboek
 * `kn/base`. Gedeeld
 * `kn/utils/giedo` en `kn/utils/daan` Synchronisatie met maillijsten, wiki, forum, etc.
 * `kn/planning`. Tappers planning
 * `kn/moderation`. E-Mail moderatie
 
Vagrant
-------

Met [vagrant](https://www.vagrantup.com) is het systeem op je eigen
computer te testen:

 1. Installeer [vagrant](https://www.vagrantup.com).
 2. Maak een kopie van deze *repository*

        git clone https://github.com/karpenoktem/kninfra

 3. Start vagrant:

        cd pad/naar/kninfra
        vagrant up
