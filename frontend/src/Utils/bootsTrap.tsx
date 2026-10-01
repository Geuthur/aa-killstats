// React
import React, { type JSX } from "react";

// Third Party
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";

/**
 * Tooltip notification component
 * @param toastNotice The message to display inside the tooltip
 */
export function toolTipContainer({ toastNotice }: { toastNotice: string }): JSX.Element {
    return (
        <div className="inline-flex items-center rounded-xl border border-emerald-500/50 bg-[#1e222e]/95 px-3 py-1.5 text-xs font-mono-tech font-semibold text-emerald-300 shadow-[0_0_25px_rgba(0,0,0,0.6)] backdrop-blur-md pointer-events-none">
            <span className="whitespace-nowrap">{toastNotice}</span>
        </div>
    );
}

/**
 * Helper function for rendering tooltips
 * @param message The message to display inside the tooltip
 * @param children The React element that triggers the tooltip
 */
export function renderTooltip(
    message: string,
    children: React.ComponentProps<typeof OverlayTrigger>["children"],
) {
    return (
        <OverlayTrigger
            placement="auto"
            trigger={["hover", "focus"]}
            overlay={
                <Tooltip id="vowra" className="!z-[9999]">
                    {message}
                </Tooltip>
            }
        >
            {children}
        </OverlayTrigger>
    );
}
export const ToolTipContainer = toolTipContainer;

const bootsTrap = {
    toolTipContainer,
    ToolTipContainer,
    renderTooltip,
};

export default bootsTrap;
