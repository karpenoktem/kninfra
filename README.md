kninfra
=======

Deze repository bevat het grootste deel van
de digitale infrastructuur van [ASV Karpe Noktem](https://karpenoktem.nl)
waaronder de website en het [smoelenboek](https://karpenoktem.nl/smoelen).
Het gros is geschreven in [Python 2](http://python.org), hoewel we
langzaam overgaan naar Python 3.  [Dit](https://docs.python.org/2/tutorial/)
is een prima Python *tutorial*.

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
kunnen we bijna alle informatie voor een gebruiker kwijt in een object,
waar je normaal allerlei hulptabellen nodig hebt.  Een voorbeeld van een
gebruikersobject is:

    {"_id" : ObjectId("4e6fcc85e60edf3dc0000270"),
     "addresses" : [ { "city" : "Nijmegen",
                       "zip" : "...",
                       "number" : "...",
                       "street" : "...",
                       "from" : ISODate("2004-..."),
                       "until" : DT_MAX) } ],
      "types" : [ "user" ],
      "names" : [ "giedo" ],
      "humanNames" : [ { "human" : "Giedo Jansen" } ],
      "person" : { "given" : null,
                   "family" : "Jansen",
                   "nick" : "Giedo",
                   "dateOfBirth" : ISODate("..."),
                   "titles" : [ ] },
      "is_active" : 0,
      "emailAddresses" : [ { "email" : "...",
                             "from" : ISODate("2004-08-31T00:00:00Z"),
                             "until" : DT_MAX } ],
      "password" : "pbkdf2_sha256$15000$...$...",
      "studies" : [ { "institute" : ObjectId("4e6fcc85e60edf3dc000001d"),
                      "study" : ObjectId("4e6fcc85e60edf3dc0000030"),
                      "number" : "...",
                      "from" : ...,
                      "until" : DT_MAX } ],
      "telephones" : [ { "number" : "...",
                         "from" : ISODate("2004-08-31T00:00:00Z"),
                         "until" : ISODate("5004-09-01T00:00:00Z") } ] },
      "preferred_language": "nl",
      "preferences" : {
          "visibility" : {
              "telephone" : false
          }
      }
    }


Mappen
------

De Django website is te vinden onder de `kn` map, met daaronder de volgende
*apps* (zoals dat heet in Django-jargon):

 * `kn/static`. De homepage
 * `kn/leden`. Smoelenboek (en ledenadministratie)
 * `kn/agenda`. De agenda
 * `kn/fotos`. Fotoboek
 * `kn/base`. Gedeeld
 * `kn/planning`. Tappers planning

Wat minder gebruikte *apps* zijn:

 * `kn/moderation`. E-Mail moderatie
 * `kn/barco`. Invullen van tapformulieren

Een *app* kan de volgende bestanden bevatten:

 * `kn/app/urls.py`.  Dit vertelt welke URL naar welke *view* moet.
 * `kn/app/views.py`.  Bevat de *views* van de *app*: dit zijn Python functies
    die een of meerdere pagina's renderen.
 * `kn/app/entities.py`.  Bevat de mongo database definities en abstracties
    voor deze *app*.
 * `kn/app/forms.py`.  Bevat definities en hulpfuncties voor webformulieren.
 * `kn/app/templates/app/`.  Bevat de HTML templates voor de app.

Daarnaast zijn er de volgende mappen:

 * `utils`.  Bevat scripts die buiten de webserver om gedraaid  kunnen worden.
   De meeste daarvan worden met de hand gedraaid als ze nodig zijn.

Vagrant
-------

Met [vagrant](https://www.vagrantup.com) is het systeem op je eigen
computer te testen:

 1. Installeer [vagrant](https://www.vagrantup.com).
 2. Maak een kopie van deze *repository*

        $ git clone https://github.com/karpenoktem/kninfra

 3. Start vagrant:

        $ cd pad/naar/kninfra
        $ vagrant up
           (...)
        $ vagrant ssh

Salt
----

De servers worden geinstalleerd met [saltstack](http://saltstack.com).
De beschrijvingen daarvan zijn te vinden onder de map `salt`.
