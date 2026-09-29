export interface TopPilot {
  character_id: number;
  character_name: string;
  main_name: string | null;
  count: number;
  total_value: number;
}

export interface CombatStatsResponse {
  total_kills: number;
  active_pvpers: number;
  destroyed_isk: number;
  lost_isk: number;
  top_attackers: TopPilot[];
  top_victims: TopPilot[];
}

/** Lightweight summary returned by the fast /stats/v2/summary/ endpoint. */
export interface CombatSummaryResponse {
  total_kills: number;
  active_pvpers: number;
  destroyed_isk: number;
  lost_isk: number;
}

/** Top-N pilot list returned by /stats/v2/attackers/ or /stats/v2/victims/. */
export interface TopPilotsResponse {
  pilots: TopPilot[];
}

export interface HallEntry {
  killmail_id: number;
  char_id: number;
  char_name: string;
  ship_id: number;
  ship_name: string;
  victim_ship_id: number;
  victim_ship_name: string;
  total_value: number;
  damage_done: number;
  zkb_link: string;
}

export interface HallResponse {
  hall_of_fame: HallEntry[];
  hall_of_shame: HallEntry[];
}

export interface KillmailItem {
  killmail_id: number;
  killmail_date: string;
  victim_id: number;
  victim_name: string;
  victim_ship_id: number;
  victim_ship_name: string;
  total_value: number;
  solar_system_id: number;
  solar_system_name: string;
  security_status: number;
  pilot_count: number;
  final_blow_id: number;
  final_blow_name: string;
  is_loss?: boolean;
  zkb_link: string;
}

export interface KillmailListResponse {
  killmails: KillmailItem[];
  total: number;
  page?: number;
  page_size?: number;
}
