"use client";

import { useEffect, useState } from "react";
import { apiGet, ROLE_LABELS, STATUT_LABELS } from "@/lib/api";

type Kpi = {
  patients_total: number;
  rendez_vous_jour: number;
  rendez_vous_a_venir: number;
  demandes_en_attente: number;
  conversations_total: number;
  segments_total: number;
  comptes_rendus_total?: number;
};

type Rdv = {
  id: number;
  patient_nom: string;
  debut: string;
  duree_minutes: number;
  motif: string;
  statut: string;
};

/**
 * Tableau de bord (US-21 / US-22) - PROPRIETAIRE : Wissal.
 * Point de depart : KPIs + prochains rendez-vous. A enrichir selon le profil
 * connecte (medecin / secretaire / patient) une fois la connexion branchée.
 */
export default function Home() {
  const [kpi, setKpi] = useState<Kpi | null>(null);
  const [rdv, setRdv] = useState<Rdv[]>([]);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    Promise.all([apiGet("/dashboard/kpi/"), apiGet("/agenda/rendez-vous/")])
      .then(([k, r]) => {
        setKpi(k);
        setRdv(r as unknown as Rdv[]);
      })
      .finally(() => setChargement(false));
  }, []);

  return (
    <main>
      <h1>MedConnect</h1>
      <p>
        Gestion de cabinet médical — prototype POC, <strong>données fictives uniquement</strong>.
        Rôles : {Object.values(ROLE_LABELS).join(" · ")}.
      </p>

      <section className="grid" aria-label="Indicateurs">
        <div className="card">
          <div className="kpi">{kpi?.patients_total ?? "—"}</div>
          patients
        </div>
        <div className="card">
          <div className="kpi">{kpi?.rendez_vous_jour ?? "—"}</div>
          rendez-vous aujourd&apos;hui
        </div>
        <div className="card">
          <div className="kpi">{kpi?.demandes_en_attente ?? "—"}</div>
          demandes en attente
        </div>
        <div className="card">
          <div className="kpi">{kpi?.conversations_total ?? "—"}</div>
          conversations
        </div>
      </section>

      <section className="card" aria-label="Prochains rendez-vous">
        <h2>Prochains rendez-vous</h2>
        {chargement && <p>Chargement…</p>}
        {!chargement && rdv.length === 0 && <p>Aucun rendez-vous.</p>}
        {rdv.length > 0 && (
          <table>
            <thead>
              <tr>
                <th scope="col">Patient</th>
                <th scope="col">Date</th>
                <th scope="col">Motif</th>
                <th scope="col">Statut</th>
              </tr>
            </thead>
            <tbody>
              {rdv.map((r) => (
                <tr key={r.id}>
                  <td>{r.patient_nom}</td>
                  <td>{new Date(r.debut).toLocaleString("fr-FR")}</td>
                  <td>{r.motif}</td>
                  <td>
                    <span
                      className={`badge ${
                        r.statut === "CONFIRME"
                          ? "confirme"
                          : r.statut === "EN_ATTENTE"
                            ? "attente"
                            : ""
                      }`}
                    >
                      {STATUT_LABELS[r.statut] ?? r.statut}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="card">
        <h2>En attente de développement</h2>
        <ul>
          <li>Connexion par rôle (US-01) — Ahmed</li>
          <li>Workflow demande → confirmation par la secrétaire (US-07, RG-01) — Leonardo</li>
          <li>Comptes rendus &amp; ordonnances (US-11 → US-14) — Philippe</li>
          <li>Messagerie temps réel (US-15 → US-17) — Wissal</li>
          <li>Assistant RAG local, bonus (US-19) — Philippe</li>
        </ul>
      </section>
    </main>
  );
}
