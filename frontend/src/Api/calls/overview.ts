// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA Killstats
import { apiClient } from "@/Api/Api";
import { ProjectName } from "@/constants";

/** Query keys of the overview area: the corporations or alliances with a killboard. */
export const overviewQueryKeys = {
  entities: (entityType: string) => ["overview", entityType] as const,
};

export interface OverviewEntity {
  id: number;
  name: string;
}

export async function loadCorporationsOverview(): Promise<OverviewEntity[]> {
  const { data, error } = await apiClient.GET(`/${ProjectName}/api/killboard/corporation/admin/`);
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load corporation overview"));
  }

  const entities: OverviewEntity[] = [];
  for (const item of data) {
    if (item.corporation) {
      for (const val of Object.values(item.corporation)) {
        const corp = val as { corporation_id?: number; corporation_name?: string };
        if (corp?.corporation_id && corp?.corporation_name) {
          entities.push({
            id: corp.corporation_id,
            name: corp.corporation_name,
          });
        }
      }
    }
  }

  return entities.sort((a, b) => a.name.localeCompare(b.name));
}

export async function loadAlliancesOverview(): Promise<OverviewEntity[]> {
  const { data, error } = await apiClient.GET(`/${ProjectName}/api/killboard/alliance/admin/`);
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load alliance overview"));
  }

  const entities: OverviewEntity[] = [];
  for (const item of data) {
    if (item.alliance) {
      for (const val of Object.values(item.alliance)) {
        const alliance = val as { alliance_id?: number; alliance_name?: string };
        if (alliance?.alliance_id && alliance?.alliance_name) {
          entities.push({
            id: alliance.alliance_id,
            name: alliance.alliance_name,
          });
        }
      }
    }
  }

  return entities.sort((a, b) => a.name.localeCompare(b.name));
}
