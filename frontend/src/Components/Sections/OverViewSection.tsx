// React
import { useState } from "react";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { Search, Shield } from "lucide-react";
import { useTranslation } from "react-i18next";

// AA Killstats
import {
    loadAlliancesOverview,
    loadCorporationsOverview,
} from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import { ProjectName } from "@/App";
import { FetchingLoader } from "@/Components/Loader";
import { renderLink } from "@/Utils/general";

import styles from "@/Components/Sections/OverViewSection.module.css";

export interface OverviewPageProps {
    entityType: "corporation" | "alliance";
}

export function OverViewSection({ entityType }: OverviewPageProps) {
    const { t } = useTranslation();

    const [searchTerm, setSearchTerm] = useState("");

    const isCorp = entityType === "corporation";

    // Load entities
    const { data: entities = [], isLoading, error } = useQuery({
        queryKey: queryKeys.Overview(entityType),
        queryFn: () =>
            isCorp ? loadCorporationsOverview() : loadAlliancesOverview(),
    });

    const filteredEntities = entities.filter((item) =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.id.toString().includes(searchTerm)
    );

    const title = isCorp ? t("Corporation Overview") : t("Alliance Overview");
    const subtitle = isCorp
        ? t("Overview of all tracked corporations in Killstats.")
        : t("Overview of all tracked alliances in Killstats.");
    return (
        <div className={styles["section"]}>
            {/* Header section */}
            <div className={`aa-panel-lg ${styles["section-header-container"]}`}>
                <div className={styles["section-header-content"]}>
                    <div className={styles["section-icon-header"]}>
                        <Shield size="24" />
                    </div>
                    <div>
                        <h1 className="text-xl sm:text-2xl tracking-wide text-white m-0">
                            {title}
                        </h1>
                        <p className="text-xs sm:text-sm text-zinc-400 m-0 mt-1">{subtitle}</p>
                    </div>
                </div>
            </div>

            {/* Filter and Search Bar */}
            <div className={`mt-3 aa-panel-lg ${styles["search-bar"]}`}>
                <Search size="14" />
                <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder={t("Filter by name or ID...")}/>
                {searchTerm && (
                    <button onClick={() => setSearchTerm("")}>
                        {t("Clear")}
                    </button>
                )}
            </div>

            {/* Content */}
            {isLoading ? (
                <div className={`mt-3 aa-panel-lg ${styles["content-loading"]}`}>
                    <FetchingLoader message={t("Loading overview...")} />
                </div>
            ) : error ? (
                <div className={`mt-3 aa-panel-lg ${styles["content-error"]}`}>
                    <p className="text-sm font-medium">
                        {t("Failed to load overview data.")}
                    </p>
                </div>
            ) : filteredEntities.length === 0 ? (
                <div className={`mt-3 aa-panel-lg ${styles["content-empty"]}`}>
                    <p className="text-sm">{t("No entries found.")}</p>
                </div>
            ) : (
                <div className={`mt-3 ${styles["content"]}`}>
                    {filteredEntities.map((item) => {
                        const logoUrl = isCorp
                            ? `https://images.evetech.net/corporations/${item.id}/logo?size=64`
                            : `https://images.evetech.net/alliances/${item.id}/logo?size=64`;

                        const killboardUrl = `/${ProjectName}/v2/${entityType}/${item.id}/`;

                        return (
                            <div key={item.id} className={`aa-panel-lg ${styles["card"]}`}>
                                <div className={styles["card-content"]}>
                                    <img
                                        src={logoUrl}
                                        alt={item.name}
                                        loading="lazy"
                                    />
                                    <div className="min-w-0 flex-1">
                                        <h3>{item.name}</h3>
                                        <span>ID: {item.id}</span>
                                    </div>
                                </div>

                                {renderLink({url: killboardUrl, text: t("View Killstats"), external: true})}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}