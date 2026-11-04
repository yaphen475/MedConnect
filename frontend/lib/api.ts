/**
 * Couche d'acces API - PROPRIETAIRE : Wissal.
 *
 * 1. On appelle le backend via le proxy Next (/api/* -> localhost:8000).
 * 2. Si le backend ne repond pas (pas encore lance, ou pendant un developpement
 *    en parallele), on retombe sur les donnees de demonstration de lib/mocks.ts
 *    pour que l'UI reste developpable sans blocage.
 */
import { MOCKS } from "./mocks";

export async function apiGet<T extends keyof typeof MOCKS>(
  path: T,
): Promise<(typeof MOCKS)[T]> {
  try {
    const res = await fetch(`/api${path}`, { cache: "no-store" });
    if (!res.ok) throw new Error(String(res.status));
    return (await res.json()) as (typeof MOCKS)[T];
  } catch {
    console.warn(`[mock] backend indisponible pour ${path}`);
    return MOCKS[path];
  }
}

export const ROLE_LABELS: Record<string, string> = {
  ADMIN: "Administrateur",
  MEDECIN: "Médecin",
  SECRETARIAT: "Secrétaire",
  PATIENT: "Patient",
};

export const STATUT_LABELS: Record<string, string> = {
  EN_ATTENTE: "En attente",
  CONFIRME: "Confirmé",
  REFUSE: "Refusé",
  ANNULE: "Annulé",
  TERMINE: "Terminé",
  ABSENTE: "Absent",
};
