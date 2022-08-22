kninfra
=======

Deze repository bevat het grootste deel van
de digitale infrastructuur van [ASV Karpe Noktem](https://karpenoktem.nl)
waaronder de website en het [smoelenboek](https://karpenoktem.nl/smoelen).
Het gros is geschreven in [Python 2](http://python.org), hoewel we
langzaam overgaan naar Python 3.  [Dit](https://docs.python.org/2/tutorial/)
is een prima Python *tutorial*.

De website
----------

We gebruiken het [Django raamwerk](https://www.djangoproject.com/)
voor de website.  Om over Django te leren, kun je het beste beginnen bij
de officiele
[Django Tutorial](https://docs.djangoproject.com/en/1.10/intro/tutorial01/).
Er is een groot verschil tussen de meeste Django websites en de onze:
wij gebruiken namelijk niet de Django modellen & database abstractie.
In plaats daarvan gebruiken we
[MongoDB](https://docs.mongodb.com/getting-started/shell/introduction/).
Het grote voordeel aan MongoDB is dat in plaats van tabellen en rijen,
het lijsten (*collections*) van JSON-objecten opslaat.  Op deze manier
kunnen we bijna alle informatie voor een gebruiker kwijt in één object,
waar je normaal allerlei hulptabellen nodig hebt.  Een voorbeeld van een
gebruikersobject is:

    {"_id" : ObjectId("4e6fcc85e60edf3dc0000270"),
     "address" : { "city" : "Nijmegen",
                   "zip" : "...",
                   "number" : "...",
                   "street" : "..." },
      "types" : [ "user" ],
      "names" : [ "giedo" ],
      "humanNames" : [ { "human" : "Giedo Jansen" } ],
      "person" : { "given" : null,
                   "family" : "Jansen",
                   "nick" : "Giedo",
                   "dateOfBirth" : ISODate("..."),
                   "titles" : [ ] },
      "is_active" : 0,
      "email" : "...",
      "password" : "pbkdf2_sha256$15000$...$...",
      "studies" : [ { "institute" : ObjectId("4e6fcc85e60edf3dc000001d"),
                      "study" : ObjectId("4e6fcc85e60edf3dc0000030"),
                      "number" : "...",
                      "from" : ...,
                      "until" : DT_MAX } ],
      "telephone" : "...",
      "preferred_language": "nl",
      "preferences" : {
          "visibility" : {
              "telephone" : false
          }
      }
    }


De Django website is te vinden onder de `kn` map, met daaronder de volgende
*apps* (zoals dat heet in Django-jargon):

 * `kn/static`. De homepage
 * `kn/leden`. Smoelenboek (en ledenadministratie)
 * `kn/agenda`. De agenda
 * `kn/fotos`. Fotoboek
 * `kn/base`. Gedeeld
 * `kn/planning`. Tappers planning

Wat minder gebruikte *apps* zijn:

 * `kn/browser`.  Voor het online browser van bestanden zoals de
    [stukken pagina](https://karpenoktem.nl/groups/leden/).

Een *app* bestaat (vaak) uit de volgende bestanden:

 * `kn/app/urls.py`.  Dit vertelt welke URL naar welke *view* moet.
 * `kn/app/views.py`.  Bevat de *views* van de *app*: dit zijn Python functies
    die een of meerdere pagina's renderen.
 * `kn/app/entities.py`.  Bevat de mongo database definities en abstracties
    voor deze *app*.
 * `kn/app/forms.py`.  Bevat definities en hulpfuncties voor webformulieren.
 * `kn/app/templates/app/`.  Bevat de HTML templates voor de app.

Daarnaast zijn er de volgende mappen/bestanden:

 * `utils`.  Bevat scripts die buiten de webserver om gedraaid  kunnen worden.
   De meeste daarvan worden met de hand gedraaid als ze nodig zijn.
   Een voorbeeld is `utils/prepare-for-the-next-year.py` dat een paar
   dagen voor de overgang naar een nieuw verenigingsjaar gedraaid wordt.
   Anderen worden automatisch gedraaid, zoals
   `utils/cron/send-informacie-digest.py` dat de informacie informatie e-mails
   stuurt.
 * `locale`.  Bevat vertalingen.
 * `nix`.  Bevat code om de website-infrastructuur en dependencies op te zetten
   met behulp van [nix](https://nixos.org). Zie ook het kopje *Development*
   hieronder.
 * `kn/urls.py` beschrijft welke *app* achter welke URL zit.


Synchronisatie
--------------

Naast de website draaien we nog een heleboel andere diensten, zoals

 * [E-Maillijsten](https://karpenoktem.nl/mailman/)
   met [Mailman](http://www.list.org).
 * Een e-mail server met [Postfix](http://www.postfix.org)
   om e-mail te ontvangen en te versturen.
 * Een [wiki](https://karpenoktem.nl/wiki/) met het
   [MediaWiki](https://www.mediawiki.org/wiki/MediaWiki) pakket.

En nog een aantal die niet *user-facing* zijn:

 * Een BIND9 DNS server
 * Een [saslauthd](http://www.linuxcommand.org/man_pages/saslauthd8.html)
   die gebruikt wordt door postfix om gebruikers te authenticeren.

Karpe Noktem heeft 1 server: *sankhara*. De website
en de meeste andere diensten draaien op *sankhara*.

Al deze verschillende diensten op *sankhara* moeten
gesynchroniseerd blijven met de ledenadministratie: als iemand in een
commissie gaat moet zij ook automatisch in de goede e-maillijsten komen.
Bij elke verandering van de ledenadministratie wordt
er gecontroleerd of alle instellingen nog ok zijn en zo nodig veranderingen
aangebracht.  Dit wordt gedaan door drie verschillende *daemons*
(programma's die in de achtergrond draaien).

 * **giedo** draait als de `infra`-gebruiker op *sankhara*.  Dat is dezelfde
   gebruiker als waaronder de website draait.  Als er een wijziging aan de
   ledenadministratie wordt gedaan, krijgt *giedo* daar een seintje van.
   *giedo* controleert dan of er zaken gewijzigd moeten worden en stuurt
   de wijzigingen door naar de andere *daemons*.  De code van *giedo* is
   te vinden onder `kn/utils/giedo`.  (Giedo was de eerste voorzitter.)
 * **daan** draait als de `root`-gebruiker op *sankhara*.  *daan* voert de
   wijzigingen op *sankhara* uit die *giedo* nodig acht.  De code an *daan*
   is te vinden onder `kn/utils/daan`.  (Daan was de eerste secretaris.)
 * **hans** draait als de `list`-gebruiker op *sankhara* en laat giedo
   de mailman e-maillijsten inkijken en aanpassen.  Code: `kn/utils/hans`.
 * **rimapd** draait als een anonieme gebruiker op *sankhara* en is de brug
   tussen saslauthd en de database.
   
Development VM
--------------

Met [nix](https://nixos.org/nix/) is het systeem op je eigen computer te testen:

 1. Installeer [nix](https://nixos.org/nix/) (of vanuit je distro)
 2. Maak een kopie van deze *repository* met [git](https://git-scm.com)

        $ git clone https://github.com/karpenoktem/kninfra

 3. Start een VM

        $ cd pad/naar/kninfra
        $ nix build .#vm
           (...)
        $ ./result/bin/run-vipassana-vm
           (andere terminal)
        $ ./result/bin/ssh
 4. Verander dingen

        $ nix-build -A vm && ./result/bin/switch-running-vm

Development Server
------------------

Een VM is handig om de hele website, inclusief daemons te testen. Vaak wil je alleen
maar iets aan de website veranderen.

 1. Volg stap 1 en 2 hierboven
 2.
 
        $ nix develop
        $ mongod --db-path ../kn-db &
        $ ./bin/reset-database
        $ ./bin/run-dev-server

