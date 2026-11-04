/** Données de démonstration (fictives) - PROPRIETAIRE : Wissal.
 *  Sert uniquement quand le backend n'est pas lancé. */

export const MOCKS = {
  "/dashboard/kpi/": {
    patients_total: 2,
    rendez_vous_jour: 1,
    rendez_vous_a_venir: 2,
    demandes_en_attente: 1,
    conversations_total: 2,
    segments_total: 0,
    comptes_rendus_total: 1,
  },
  "/agenda/rendez-vous/": [
    {
      id: 1,
      patient_nom: "Lucas Bernard",
      debut: new Date(Date.now() + 3 * 86400000).toISOString(),
      duree_minutes: 30,
      motif: "Consultation générale - demande en ligne",
      statut: "EN_ATTENTE",
    },
    {
      id: 2,
      patient_nom: "Emma Petit",
      debut: new Date(Date.now() + 2 * 86400000).toISOString(),
      duree_minutes: 30,
      motif: "Suivi tension",
      statut: "CONFIRME",
    },
  ],
  "/agenda/disponibilites/": [
    { id: 1, jour: "LUNDI", debut: "08:30", fin: "12:00", duree_par_defaut: 30, actif: true },
    { id: 2, jour: "LUNDI", debut: "14:00", fin: "18:00", duree_par_defaut: 30, actif: true },
    { id: 3, jour: "MARDI", debut: "08:30", fin: "12:00", duree_par_defaut: 30, actif: true },
  ],
  "/messagerie/threads/": [
    {
      id: 1,
      sujet: "Question administrative",
      patient_nom: "Lucas Bernard",
      participants_noms: ["Claire Fontaine", "Martine Roux", "Lucas Bernard"],
      messages: [
        { id: 1, emetteur_nom: "Lucas Bernard", corps: "Bonjour, puis-je changer mon rendez-vous de mardi ?", cree_le: "2026-11-03T10:00:00Z" },
        { id: 2, emetteur_nom: "Martine Roux", corps: "Bonjour, oui, je vous propose jeudi 9h.", cree_le: "2026-11-03T10:05:00Z" },
      ],
    },
  ],
  "/patients/patients/": [
    { id: 1, nom_complet: "Lucas Bernard", first_name: "Lucas", last_name: "Bernard", email: "lucas.bernard@example.fr", telephone: "0611223344" },
    { id: 2, nom_complet: "Emma Petit", first_name: "Emma", last_name: "Petit", email: "emma.petit@example.fr", telephone: "0655667788" },
  ],
  "/dossiers/comptes-rendus/": [
    {
      id: 1,
      patient_nom: "Emma Petit",
      date_consultation: "2026-10-28",
      titre: "Consultation de suivi",
      contenu: "Patient asymptomatique. TA 132/84. Examen clinique normal. [DEMONSTRATION]",
    },
  ],
  "/dossiers/ordonnances/": [
    {
      id: 1,
      patient_nom: "Emma Petit",
      date_ordonnance: "2026-10-28",
      contenu: "1. Mesure de la tension 2x/semaine\n2. Reprise progressive du sport [DEMONSTRATION]",
    },
  ],
} as const;
