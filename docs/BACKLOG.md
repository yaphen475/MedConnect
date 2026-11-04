> Source : `MedConnect_Product_Backlog.pdf` fourni par l'equipe.
> **CECI EST LE BACKLOG DE REFERENCE** pour le developpement (P0 = MVP).
> Matrice de propriete des fichiers + premieres taches : voir CONTRIBUTING.md.

---

Product Backlog — MedConnect
Système de gestion intelligent pour un cabinet médical privé
Projet : SI — 4A Informatique — ENSIM
Équipe : 4 étudiants
Durée prévue : 7 heures de TP
Type de projet : Application web — CRM médical
1. Présentation du projet
1.1. Contexte
MedConnect est une application web de gestion destinée à un médecin exerçant dans son propre cabinet
médical.
L'objectif est de centraliser et de simplifier la gestion des rendez-vous, des patients, des consultations et des
échanges entre les différents utilisateurs.
Le système repose sur quatre profils : administrateur, médecin, secrétaire médicale et patient.
Le projet intègre également des fonctionnalités innovantes permettant d'automatiser certaines tâches
administratives et d'améliorer l'expérience des patients grâce à l'intelligence artificielle.
1.2. Objectifs principaux
Faciliter la gestion des rendez-vous médicaux.
Centraliser les informations administratives et médicales.
Permettre la consultation des comptes rendus et des ordonnances selon les droits d'accès.
Améliorer la communication entre les utilisateurs.
Automatiser la présentation des créneaux disponibles.
Proposer un assistant conversationnel intelligent utilisant une approche RAG.
Garantir la confidentialité des informations médicales.
1.3. Périmètre
Le projet consiste à réaliser un prototype fonctionnel, utilisant exclusivement des données fictives.
Les prescriptions présentées dans le prototype sont des documents de démonstration sans valeur médicale
officielle.
2. Acteurs et gestion des permissions
Administrateur
Responsable de l'administration technique du système.
MedConnect_Product_Backlog.md 2026-11-04
1 / 13
Fonctionnalités :
Gérer les comptes utilisateurs.
Attribuer et modifier les rôles.
Gérer les paramètres généraux.
Superviser le fonctionnement technique.
L'administrateur ne dispose pas automatiquement d'un accès aux données médicales.
Médecin
Responsable des consultations et du suivi médical.
Fonctionnalités :
Consulter son agenda.
Accéder aux dossiers médicaux de ses patients.
Consulter l'historique des consultations.
Rédiger des comptes rendus médicaux.
Rédiger des ordonnances.
Communiquer avec les patients et la secrétaire.
Secrétaire médicale
Responsable de l'organisation administrative du cabinet.
Fonctionnalités :
Consulter et gérer l'agenda du médecin.
Ajouter, confirmer, modifier ou annuler des rendez-vous.
Traiter les demandes de rendez-vous des patients.
Accéder uniquement aux informations administratives nécessaires.
Communiquer avec le médecin et les patients.
Restrictions :
Aucun accès aux comptes rendus médicaux.
Aucun accès aux diagnostics ou aux ordonnances.
Aucun accès aux données personnelles non nécessaires aux tâches administratives.
Patient
Utilisateur bénéficiant des services du cabinet.
Fonctionnalités :
Consulter les créneaux de rendez-vous disponibles.
Envoyer une demande de rendez-vous.
Suivre l'état de ses demandes.
Consulter ses rendez-vous confirmés.
Consulter ses propres ordonnances.
MedConnect_Product_Backlog.md 2026-11-04
2 / 13
Utiliser la messagerie interne.
Utiliser l'assistant intelligent.
Le patient ne peut pas confirmer directement un rendez-vous.
3. Product Backlog
Niveaux de priorité :
P0 — Must Have : fonctionnalités essentielles au prototype.
P1 — Should Have : fonctionnalités importantes, à intégrer selon l'avancement.
P2 — Could Have : améliorations facultatives.
P3 — Future : fonctionnalités réservées à une évolution du projet.
Epic 1 — Authentification et gestion des utilisateurs
US-01 — Authentification
En tant qu'utilisateur, je souhaite me connecter à mon compte afin d'accéder aux fonctionnalités correspondant à
mon rôle.
Priorité : P0
Critères d'acceptation :
Chaque utilisateur possède un compte.
La connexion permet d'identifier le rôle de l'utilisateur.
Les fonctionnalités accessibles dépendent de ce rôle.
US-02 — Gestion des comptes
En tant qu'administrateur, je souhaite créer, modifier et désactiver des comptes utilisateurs afin de gérer l'accès
au système.
Priorité : P1
Critères d'acceptation :
L'administrateur peut gérer les comptes.
Chaque compte possède un rôle.
Un compte désactivé ne peut plus accéder au système.
US-03 — Gestion des fiches patients
En tant qu'utilisateur autorisé, je souhaite consulter et mettre à jour les informations administratives des patients
afin d'assurer leur suivi.
Priorité : P0
Critères d'acceptation :
MedConnect_Product_Backlog.md 2026-11-04
3 / 13
Une fiche patient peut être créée.
Les informations administratives peuvent être consultées et modifiées par les personnes autorisées.
Les informations sont accessibles selon les permissions définies.
US-04 — Protection des données personnelles
En tant que patient, je souhaite que mes informations personnelles et médicales soient accessibles uniquement
aux personnes autorisées afin de préserver ma confidentialité.
Priorité : P0
Critères d'acceptation :
Le médecin peut accéder aux informations médicales nécessaires aux soins.
La secrétaire accède uniquement aux données administratives nécessaires à ses missions.
Les autres informations personnelles sont masquées.
Un utilisateur ne peut pas contourner ces restrictions en accédant directement à une page protégée.
Epic 2 — Gestion des rendez-vous
US-05 — Consultation des disponibilités
En tant que patient, je souhaite visualiser les créneaux disponibles du médecin afin de choisir facilement un
horaire qui me convient.
Priorité : P0
Critères d'acceptation :
Les créneaux libres sont affichés automatiquement.
Les créneaux déjà occupés ne peuvent pas être demandés comme disponibles.
L'interface est simple et compréhensible.
US-06 — Demande de rendez-vous
En tant que patient, je souhaite sélectionner un créneau disponible et envoyer une demande de rendez-vous afin
d'obtenir une consultation.
Priorité : P0
Critères d'acceptation :
Le patient peut sélectionner un créneau.
La demande possède initialement le statut « En attente ».
La demande est transmise à la secrétaire.
La demande ne constitue pas une réservation définitive.
US-07 — Validation des rendez-vous
En tant que secrétaire médicale, je souhaite consulter et traiter les demandes afin de confirmer ou de refuser les
rendez-vous.
MedConnect_Product_Backlog.md 2026-11-04
4 / 13
Priorité : P0
Critères d'acceptation :
La secrétaire visualise les demandes en attente.
Elle peut accepter ou refuser une demande.
Une demande acceptée devient un rendez-vous confirmé.
Un créneau ne peut pas accueillir deux rendez-vous confirmés simultanément.
US-08 — Gestion de l'agenda
En tant que secrétaire médicale, je souhaite créer, modifier et annuler des rendez-vous afin d'organiser l'agenda
du médecin.
Priorité : P0
Critères d'acceptation :
La secrétaire peut consulter l'agenda.
Elle peut ajouter un rendez-vous directement.
Elle peut modifier ou annuler un rendez-vous.
Les changements sont visibles dans l'agenda du médecin.
US-09 — Consultation de l'agenda personnel
En tant que médecin ou patient, je souhaite consulter mes rendez-vous afin de connaître les consultations
prévues.
Priorité : P0
Critères d'acceptation :
Le médecin visualise les rendez-vous de son cabinet.
Le patient visualise uniquement ses propres rendez-vous.
Le statut des rendez-vous est clairement indiqué.
US-10 — Suivi des demandes
En tant que patient, je souhaite connaître l'état de mes demandes afin de savoir si mes rendez-vous sont
confirmés.
Priorité : P1
Critères d'acceptation :
Le patient peut consulter ses demandes.
Chaque demande affiche son statut.
Une confirmation ou un refus est visible dans son espace personnel.
Epic 3 — Dossiers médicaux et consultations
US-11 — Création d'un compte rendu médical
MedConnect_Product_Backlog.md 2026-11-04
5 / 13
En tant que médecin, je souhaite enregistrer un compte rendu après chaque consultation afin de conserver les
informations relatives au suivi médical.
Priorité : P0
Critères d'acceptation :
Le médecin peut rédiger un compte rendu.
Le compte rendu est associé au bon patient.
La date de consultation est enregistrée.
Le contenu est inaccessible à la secrétaire.
US-12 — Historique des consultations
En tant que médecin, je souhaite consulter l'historique médical d'un patient afin de disposer des informations
nécessaires à son suivi.
Priorité : P0
Critères d'acceptation :
Les anciens comptes rendus sont accessibles au médecin.
Les comptes rendus sont associés au patient concerné.
L'historique est présenté chronologiquement.
Les utilisateurs non autorisés ne peuvent pas le consulter.
US-13 — Création d'ordonnances
En tant que médecin, je souhaite rédiger une ordonnance afin de formaliser les prescriptions destinées à un
patient.
Priorité : P1
Critères d'acceptation :
Le médecin peut créer une ordonnance de démonstration.
L'ordonnance est associée au patient.
Le document comporte une date et l'identification du médecin.
La secrétaire ne peut pas consulter son contenu.
US-14 — Consultation des ordonnances
En tant que patient, je souhaite consulter mes ordonnances afin de retrouver les documents transmis par mon
médecin.
Priorité : P1
Critères d'acceptation :
Le patient visualise ses propres ordonnances.
Il ne peut pas consulter celles des autres patients.
Les documents sont présentés de manière lisible.
MedConnect_Product_Backlog.md 2026-11-04
6 / 13
Epic 4 — Messagerie interne
US-15 — Envoi de messages
En tant qu'utilisateur, je souhaite envoyer des messages aux autres utilisateurs autorisés afin de faciliter la
communication au sein du cabinet.
Priorité : P0
Critères d'acceptation :
Un utilisateur peut sélectionner un destinataire autorisé.
Il peut rédiger et envoyer un message.
Le destinataire peut consulter le message reçu.
US-16 — Consultation des conversations
En tant qu'utilisateur, je souhaite consulter l'historique de mes messages afin de retrouver les échanges
précédents.
Priorité : P0
Critères d'acceptation :
Les messages reçus et envoyés sont accessibles.
L'historique est organisé chronologiquement.
Chaque utilisateur consulte uniquement les conversations auxquelles il participe.
US-17 — Confidentialité de la messagerie
En tant que patient, je souhaite que mes échanges médicaux restent confidentiels afin de protéger mes
informations personnelles.
Priorité : P0
Critères d'acceptation :
Les échanges privés entre le médecin et le patient ne sont pas accessibles à la secrétaire.
Les échanges administratifs sont accessibles uniquement aux participants autorisés.
L'administrateur technique ne dispose pas d'un accès automatique aux conversations.
Epic 5 — Fonctionnalités innovantes
US-18 — Détection automatique des créneaux disponibles
En tant que patient, je souhaite que le système identifie automatiquement les créneaux libres dans l'agenda du
médecin afin de pouvoir demander rapidement un rendez-vous.
Priorité : P0 — Innovation 1
Critères d'acceptation :
MedConnect_Product_Backlog.md 2026-11-04
7 / 13
Le système identifie les créneaux disponibles en fonction de l'agenda.
Les créneaux occupés sont exclus des possibilités de demande.
Les disponibilités sont actualisées après la confirmation d'un rendez-vous.
Le patient choisit directement parmi les créneaux proposés.
La confirmation définitive reste exclusivement sous la responsabilité de la secrétaire.
US-19 — Assistant intelligent RAG
En tant qu'utilisateur, je souhaite interroger un chatbot intelligent afin d'obtenir rapidement des réponses aux
questions concernant le fonctionnement du cabinet médical.
Priorité : P1 — Innovation 2
Critères d'acceptation :
Le chatbot répond à des questions concernant le cabinet.
Les réponses reposent sur une base documentaire préalablement définie.
Le chatbot utilise une approche RAG (Retrieval-Augmented Generation).
Les réponses peuvent indiquer les documents utilisés.
Le chatbot ne remplace pas un professionnel de santé et ne fournit pas de diagnostic.
Exemples de questions :
Quels sont les horaires d'ouverture du cabinet ?
Comment demander un rendez-vous ?
Comment retrouver mes ordonnances ?
Comment contacter la secrétaire ?
US-20 — Scoring comportemental et aide au diagnostic
En tant que médecin, je souhaite disposer à terme d'un outil d'analyse de données cliniques afin d'étudier des
indicateurs susceptibles d'aider à l'évaluation médicale.
Priorité : P3 — Évolution future
Critères envisagés :
L'outil utilise uniquement des données autorisées et appropriées.
Les résultats sont présentés comme des indicateurs expérimentaux.
Les limites, les biais et les incertitudes des résultats sont indiqués.
Les résultats ne constituent pas un diagnostic automatique.
Toute utilisation clinique exigerait une validation scientifique et réglementaire préalable.
Cette fonctionnalité est exclue du prototype initial.
Epic 6 — Expérience utilisateur
US-21 — Interface adaptée aux utilisateurs
En tant qu'utilisateur, je souhaite disposer d'une interface simple et intuitive afin de réaliser mes tâches sans
connaissances informatiques avancées.
MedConnect_Product_Backlog.md 2026-11-04
8 / 13
Priorité : P0
Critères d'acceptation :
L'interface est organisée selon les différents profils.
Les fonctionnalités principales sont facilement accessibles.
Les actions importantes sont clairement identifiées.
Le processus de demande de rendez-vous nécessite peu d'étapes.
US-22 — Tableau de bord personnalisé
En tant qu'utilisateur, je souhaite disposer d'un tableau de bord adapté à mon profil afin d'accéder rapidement
aux informations importantes.
Priorité : P1
Critères d'acceptation :
Le médecin visualise ses prochains rendez-vous.
La secrétaire visualise les demandes en attente et l'agenda.
Le patient visualise ses prochains rendez-vous.
Le tableau de bord respecte les permissions de chaque profil.
4. Règles de gestion
ID Règle
RG-
01 Seule la secrétaire médicale peut confirmer un rendez-vous.
RG-
02 Le patient peut uniquement demander un créneau disponible.
RG-
03 Toute nouvelle demande possède le statut « En attente ».
RG-
04 Un rendez-vous confirmé rend le créneau indisponible.
RG-
05 Plusieurs demandes peuvent concerner un même créneau, mais une seule peut être confirmée.
RG-
06 Un patient ne peut accéder qu'à ses propres informations.
RG-
07 La secrétaire n'a aucun accès aux informations médicales.
RG-
08 Les données personnelles non nécessaires à l'accueil sont également masquées pour la secrétaire.
MedConnect_Product_Backlog.md 2026-11-04
9 / 13
ID Règle
RG-
09 Seul le médecin peut rédiger des comptes rendus médicaux et des ordonnances.
RG-
10 Les comptes rendus sont conservés dans l'historique du patient.
RG-
11 Les messages privés sont accessibles uniquement aux participants autorisés.
RG-
12
L'administrateur technique ne possède pas automatiquement des droits d'accès aux données
médicales.
RG-
13 Le chatbot ne doit pas délivrer de diagnostics ou de prescriptions médicales.
Statuts des demandes et des rendez-vous
En attente : demande envoyée par le patient, non encore traitée.
Confirmé : rendez-vous validé par la secrétaire.
Refusé : demande rejetée.
Annulé : rendez-vous précédemment confirmé puis annulé.
5. Matrice des permissions
Fonctionnalité Admin Médecin Secrétaire Patient
Administration des comptes Oui Non Non Non
Consultation de l'agenda du
cabinet Non Oui Oui Non
Consultation de ses rendez-vous — Oui Oui Oui
Demande de rendez-vous Non Non Non Oui
Confirmation d'un rendez-vous Non Non Oui Non
Gestion de l'agenda Non Non Oui Non
Données administratives Gestion technique Oui Accèslimité Données propres
Données médicales Non Oui Non Accès limité
Rédaction de comptes rendus Non Oui Non Non
Rédaction d'ordonnances Non Oui Non Non
Consultation des ordonnances Non Oui Non Ordonnancespropres
MedConnect_Product_Backlog.md 2026-11-04
10 / 13
Fonctionnalité Admin Médecin Secrétaire Patient
Messagerie Sans accès aucontenu Oui Oui Oui
Chatbot Selon le profil Oui Oui Oui
6. Définition du MVP
Compte tenu de la durée limitée du projet, le développement sera organisé autour d'un produit minimum
viable.
Fonctionnalités prioritaires
Le premier prototype devra démontrer :
1. Une connexion avec différents rôles.
2. La séparation des permissions entre médecin, secrétaire et patient.
3. La gestion des fiches patients.
4. L'affichage automatique des disponibilités.
5. La demande d'un créneau par le patient.
6. La confirmation du rendez-vous par la secrétaire.
7. La consultation des rendez-vous par le médecin.
8. Une messagerie interne simple.
9. L'enregistrement et la consultation de comptes rendus médicaux.
Fonctionnalités à développer selon le temps disponible
Création et consultation d'ordonnances de démonstration.
Tableau de bord personnalisé.
Suivi détaillé des demandes.
Prototype du chatbot RAG sur une base documentaire réduite.
Les deux propositions innovantes retenues sont la gestion automatisée des disponibilités et le chatbot RAG.
La première fera partie du MVP ; la seconde pourra être présentée sous forme de démonstrateur limité, si le
temps le permet.
Fonctionnalité exclue du MVP
Scoring comportemental et prévision de diagnostic.
7. Scénario de démonstration
La soutenance pourra s'appuyer sur un scénario complet :
1. Un patient se connecte à son espace personnel.
2. Il consulte les disponibilités du médecin.
3. Il sélectionne un créneau et envoie une demande.
4. La secrétaire reçoit la demande et la confirme.
MedConnect_Product_Backlog.md 2026-11-04
11 / 13
5. Le médecin retrouve le rendez-vous dans son agenda.
6. Le médecin rédige un compte rendu après la consultation.
7. Le patient retrouve son rendez-vous et, si la fonctionnalité est disponible, son ordonnance.
8. Les utilisateurs échangent des messages.
9. Une démonstration de l'assistant intelligent est présentée si son prototype est disponible.
Ce scénario permet de présenter la circulation des informations entre les différents profils ainsi que les
contrôles d'accès.
8. Contraintes et exigences non fonctionnelles
Sécurité et confidentialité
Authentification des utilisateurs.
Contrôle des accès selon les rôles.
Protection des données médicales.
Limitation de l'accès aux données personnelles selon leur nécessité.
Utilisation exclusive de données fictives pour le prototype.
Absence de valeur médicale ou juridique officielle pour les documents de démonstration.
Ergonomie
Interface simple et cohérente.
Navigation intuitive.
Formulaires courts et compréhensibles.
Affichage clair des créneaux disponibles et des statuts.
Qualité
Fonctionnalités principales testables.
Cohérence entre les modules.
Prévention des conflits de rendez-vous confirmés.
Démonstration du respect des droits d'accès.
Évolutivité
Le système devra être conçu de manière à permettre, dans une version future, l'ajout de nouvelles
fonctionnalités telles que les notifications, les services de télémédecine ou les outils d'aide à la décision
médicale, sous réserve des validations nécessaires.
9. Répartition fonctionnelle prévisionnelle
Cette répartition pourra être adaptée selon les compétences de chaque membre de l'équipe.
Membre Responsabilité principale
Membre 1 Gestion des utilisateurs, fiches patients et permissions
Membre 2 Agenda, demandes de rendez-vous et disponibilités automatiques
MedConnect_Product_Backlog.md 2026-11-04
12 / 13
Membre Responsabilité principale
Membre 3 Dossiers médicaux, comptes rendus et ordonnances
Membre 4 Messagerie, chatbot et expérience utilisateur
L'intégration, les tests et la préparation de la soutenance seront des responsabilités communes.
10. Conclusion
MedConnect vise à proposer une solution de gestion centralisée pour un cabinet médical privé, avec une
attention particulière portée à l'automatisation administrative, à la simplicité d'utilisation et à la confidentialité
des données.
Le projet s'appuie sur quatre domaines fonctionnels principaux : gestion des utilisateurs, agenda médical,
dossiers patients et messagerie interne.
Les fonctionnalités innovantes proposées sont la détection automatique des créneaux disponibles et un
assistant conversationnel utilisant l'approche RAG.
Le développement sera réalisé de manière progressive, en donnant la priorité à un prototype fonctionnel
démontrant les principaux parcours utilisateurs et le respect des permissions.
Les fonctionnalités plus avancées, notamment le scoring comportemental et l'aide au diagnostic, seront
considérées comme des perspectives d'évolution.
MedConnect_Product_Backlog.md 2026-11-04
13 / 13